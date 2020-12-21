FROM python:3.8.5
LABEL name='TraderNet API Utils' version=1
WORKDIR /code
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./ .