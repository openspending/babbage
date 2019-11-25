FROM python:3.7.4

COPY . /app
WORKDIR "/app"

# Development version:

RUN pip install tox

RUN python3.7 setup.py develop
