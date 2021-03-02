# Logging stuff
from datetime import datetime

from pythonjsonlogger import jsonlogger
import logging
import uuid

# Flask and friends
from flask import Flask, request
import werkzeug

import mysql.connector
import os

# Adding any custom fields to be added to all logs
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if not log_record.get('request_id'):
            log_record['request_id'] = request.request_id

logger = logging.getLogger()
# gunicorn logging configuration will register a handler as well
# so we clear any handlers
if logger.hasHandlers():
    logger.handlers.clear()
logHandler = logging.StreamHandler()
formatter = CustomJsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)


app = Flask(__name__)

REQUEST_ID_HEADERS = ["X-Trace-ID", "X-Request-ID"]

def get_or_set_request_id():
    # TODO: Ideally check if we are in a request context
    for h in REQUEST_ID_HEADERS:
        if h in request.headers:
            return request.headers[h]
    return str(uuid.uuid4())

# setup middleware to log the request
# before handling it
@app.before_request
def log_request():
    request.request_id = get_or_set_request_id()
    request_body = "{}"
    if request.method == "POST":
        if request.content_type == "application/json":
            request_body = json.loads(request.json)

    logger.info('Request receieved', extra={
        'request_id': request.request_id,
        'request_path': request.path,
        'request_method': request.method,
        'request_content_type': request.content_type,
        'request_body': request_body,
    })

# setup middleware to log the response before
# sending it back to the client
@app.after_request
def log_response(response):
    logger.info('Request processed', extra={
        'request_id': request.request_id,
        'request_path': request.path,
        'response_status': response.status_code
    })

    response.headers['X-Request-ID'] = request.request_id
    return response


@app.route('/')
def index():
    cnx = mysql.connector.connect(user='joe', password='password',
                                host='db',
                                database='service2')
    data = "<h1>Data</h1><p><table>{0}</table></p>"
    cursor = cnx.cursor()
    cursor.execute("SELECT first_name, last_name from users")
    rows = ""
    for first_name, last_name in cursor:
        rows += '<tr><td>{0}</td><td>{1}</td></tr>'.format(first_name, last_name)
    return data.format(rows), 200
