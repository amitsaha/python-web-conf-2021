# Python Web Conference 2021 Materials

This repository contains materials for my talk [You Have Written A Web Application, Now What?](https://2021.pythonwebconf.com/presentations/you-have-written-a-web-application-now-what).

# Demos
## Tools needed

Docker and Docker Compose

## Code

- [Logging](./logging-wsgi)
- [Metrics](./metrics-wsgi)
- [Distributed Tracing](./distributed-tracing-wsgi)

# OpenTelemetry, Metrics and WSGI applications

I mentioned in the presentation that we cannot use OpenTelemetry APIs for exporting
metrics from WSGI applications. The short answer is that - OpenTelemetry collector 
[doesn't](https://github.com/open-telemetry/opentelemetry-collector/issues/1422) currently support 
aggregation and we don't have any way to have shared state in the [opentelemetry-python
client](https://github.com/open-telemetry/opentelemetry-python/issues/93).

We have exactly the same limitation which prevents us from using Prometheus client
in Python natively - a topic I have written [about](https://echorand.me/posts/python-prometheus-monitoring-options/).

# Explore more

- [OpenTelemetry Automatic instrumentation](https://lightstep.com/blog/opentelemetry-automatic-instrumentation/)
- [OpenTelemetry + AWS Lambda + Python](https://lightstep.com/blog/opentelemetry-lambda-for-python/)


