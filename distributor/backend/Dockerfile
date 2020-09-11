FROM python:3.8-buster

RUN apt-get update
RUN apt-get install git -y

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
RUN git clone https://github.com/pypa/pip
RUN cd pip && python setup.py install
RUN pip install docker-py