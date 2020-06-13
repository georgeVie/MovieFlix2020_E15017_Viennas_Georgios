FROM python:3.8.3-slim
MAINTAINER Giorgos Viennas <viennas.g@gmail.com>

RUN pip install flask pymongo
RUN mkdir /app
RUN mkdir -p /app/templates
COPY main.py /app/main.py
ADD templates /app/templates
EXPOSE 5000
WORKDIR /app
ENTRYPOINT ["python3","-u", "main.py"]