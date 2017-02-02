### Python3 based Flask Container ###
FROM ubuntu:latest

## Python 3
MAINTAINER Richard Watson <richwats@cisco.com>

RUN apt-get update && apt-get install -y \
    iputils-ping \
    dnsutils \
    python3 \
    python3-pip \
&& rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app/

RUN pip3 install -r requirements.txt --upgrade pip

ENV WEBHOOK_NAME=SparkChatDemo-Messages
ENV WEBHOOK_URL=
ENV SPARK_API_VERSION=v1
ENV SPARK_API_URL=https://api.ciscospark.com
ENV SPARK_INT_ID=C88d6dfbb9a503d291b035cf7fcfd34cf5ab5266fc072e6b2724b692c5f05e21c
ENV SPARK_INT_SECRET=5433e110aeaa07ab9651a919b6a156ca53c0a6bc36b04f226e52f283ad305ea7
ENV SPARK_INT_REDIRECT_URI=
ENV FLASK_SECRET_KEY=

EXPOSE 8080
#EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["/app/data/app.py"]