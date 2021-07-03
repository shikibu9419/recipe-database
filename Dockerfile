FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

USER root

WORKDIR /app

RUN apt-get update
RUN pip install --upgrade pip
RUN pip install --upgrade pipenv

COPY Pipfile /app
COPY Pipfile.lock /app

RUN pipenv install --system

COPY . /app
