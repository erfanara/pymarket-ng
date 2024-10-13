FROM python:alpine

WORKDIR /pymarketng

COPY . /pymarketng

RUN pip install --no-cache-dir -r requirements.txt