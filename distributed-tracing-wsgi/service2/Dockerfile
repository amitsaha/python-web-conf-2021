FROM python:3.9
RUN apt-get -y update && apt-get -y install libprotobuf17 python-pkg-resources python-protobuf python-six
RUN pip install mysql-connector

ADD . /application
WORKDIR /application
RUN pip install -r requirements.txt
CMD ["gunicorn", "--log-config", "gunicorn_logging.conf", "--workers", "5", "--bind", "0.0.0.0:8000", "app:app"]