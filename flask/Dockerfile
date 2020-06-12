FROM ubuntu:16.04

MAINTAINER Giorgos Viennas <george-viennas@hotmail.gr>

RUN apt-get update
RUN apt-get install -y python3 python3-pip 
RUN pip3 install flask pymongo
RUN mkdir /app
RUN mkdir -p /app/templates
COPY main.py /app/main.py
ADD templates /app/templates
EXPOSE 5000
WORKDIR /app
ENTRYPOINT ["python3","-u", "service.py"]