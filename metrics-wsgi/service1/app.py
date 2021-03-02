# Logging stuff
import logging
import time
import uuid
from datetime import datetime

from datadog import statsd

# HTTP client library
import requests
import werkzeug
# Flask and friends
from flask import Flask, request
from pythonjsonlogger import jsonlogger

# Metrics
from metrics_middleware import setup_metrics

# Other libraries
import json


# Set up the logging really early before initialization
# of the Flask app instance

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
setup_metrics(app)

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
        'request_path': request.path,
        'response_status': response.status_code
    })

    response.headers['X-Request-ID'] = request.request_id
    return response


def do_stuff():
    headers = {'X-Request-ID': request.request_id}

    # TODO: Put in a context manager
    request_start = time.time()
    data = requests.get('http://service2:8000', headers=headers)
    request_stop = time.time()
    latency = request_stop - request_start

    statsd.histogram("client_request_latency",
                     latency,
                     tags=[
                         'origin:service1',
                         'destination:service2',
                     ]
                     )
    return data


@app.route('/')
def index():
    data = do_stuff()
    return data.text, 200


@app.errorhandler(werkzeug.exceptions.HTTPException)
def handle_500(error):
    return "Something went wrong", 500


@app.route('/honeypot/')
def test1():
    1 / 0
    return 'lol'
