FROM python:3.8

RUN pip install "ezomero==2.1.0"

RUN pip install "arkitekt[all]>=0.7.5"
RUN pip install "omero-ark==0.0.4"

RUN mkdir /app
WORKDIR /app
COPY .arkitekt /app/.arkitekt
COPY app.py /app/app.py
