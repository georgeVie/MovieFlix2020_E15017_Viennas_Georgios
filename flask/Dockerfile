FROM python:3
MAINTAINER Giorgos Viennas <viennas.g@gmail.com>

RUN pip3 install flask pymongo
RUN mkdir /app
RUN mkdir -p /app/templates
COPY main.py /app/main.py
ADD templates /app/templates
EXPOSE 5000
WORKDIR /app
ENTRYPOINT ["python3","-u", "main.py"]