FROM python:3.8-buster

COPY requirements.txt /tmp/
RUN apt-get update
RUN apt-get install python3-dev -y

RUN pip install --requirement /tmp/requirements.txt