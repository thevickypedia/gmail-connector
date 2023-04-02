FROM python:3.9-slim

RUN mkdir /opt/temp
COPY . /opt/temp

RUN /usr/local/bin/python3 -m pip install --upgrade pip
RUN pip install --user gmail-connector

WORKDIR /opt/temp

ENTRYPOINT ["/usr/local/bin/python", "./test_runner.py"]
