from pythonjsonlogger import jsonlogger
import logging

from opentelemetry import trace

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace import sampling
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)

from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


from opentelemetry import trace

from flask import Flask, request
import werkzeug
import requests
import os

resource = Resource({"service.name": "service1"})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

OTEL_AGENT = os.getenv('OTEL_AGENT', "otel-agent")

otlp_exporter = OTLPSpanExporter(endpoint=OTEL_AGENT + ":4317", insecure=True)
span_processor = BatchExportSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)


logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

app = Flask(__name__)

@app.before_request
def record_request():
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

@app.after_request
def record_response(response):
    logger.info('Request processed', extra={
        'request_path': request.path,
        'response_status': response.status_code
    })

    return response


FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

def do_stuff():
    return requests.get('http://service2:5000')

@app.route('/')
def index():
    with tracer.start_as_current_span("service2-request"):
        data = do_stuff()
    return data.text, 200

@app.errorhandler(werkzeug.exceptions.HTTPException)
def handle_500(error):
    return "Something went wrong", 500

@app.route('/honeypot/')
def test1():
    1/0
    return 'lol'