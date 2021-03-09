# Distributed tracing

# OpenTelemetry python imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

# Intrumentation libraries for tracing
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Flask and friends
from flask import Flask, request
import werkzeug

# HTTP client library
import requests

# Other libraries
import os

# Initialize the tracing machinery
resource = Resource({"service.name": "service1"})

OTEL_AGENT = os.getenv('OTEL_AGENT', "otel-agent")
otlp_exporter = OTLPSpanExporter(endpoint=OTEL_AGENT + ":4317", insecure=True)

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
span_processor = BatchExportSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)


app = Flask(__name__)

# Setup the instrumentation for the Flask app
# and Requests library
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()



def do_stuff():
    return requests.get('http://service2:8000')

@app.route('/')
def index():
    # We create a span here
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
