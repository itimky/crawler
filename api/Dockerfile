FROM python:3.6.1-alpine

MAINTAINER Aevrika
RUN apk add --no-cache g++ linux-headers

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip install --ignore-installed -r requirements.txt
RUN adduser -SH www-data
USER www-data
