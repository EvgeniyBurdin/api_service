FROM python:3.8-slim

WORKDIR /sources

ADD ./sources/requirements.txt /sources/requirements.txt
RUN pip install -r /sources/requirements.txt

ADD ./sources /sources

ENV PYTHONPATH /sources

CMD python3 run.py
