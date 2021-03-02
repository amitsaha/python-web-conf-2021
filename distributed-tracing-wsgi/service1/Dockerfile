FROM python:3.9
ADD . /application
WORKDIR /application
RUN pip install -r requirements.txt --use-deprecated=legacy-resolver
CMD ["gunicorn", "--log-config", "gunicorn_logging.conf", "--workers", "5", "--bind", "0.0.0.0:8000", "app:app"]