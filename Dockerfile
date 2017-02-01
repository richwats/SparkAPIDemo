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

EXPOSE 8080
#EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["/app/data/app.py"]