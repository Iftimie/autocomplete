FROM python:3.8-buster

RUN apt-get update
RUN apt-get install python3-dev -y

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
RUN pip install "confluent-kafka[avro]"