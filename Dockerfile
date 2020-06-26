FROM ubuntu:18.04

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    software-properties-common \
    vim \
    curl \
    git \
    gettext

RUN apt-get install -y build-essential python3 python3-dev python3-pip python3-venv libpq-dev

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

RUN mkdir /project
WORKDIR /project
ADD . /project/

RUN python3 -m pip install -r requirements/requirements.txt
RUN python3 -m pip install -e .