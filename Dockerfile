FROM jtl-tkgiharbor.hq.bni.co.id/mnd-dev/python:3.9-slim

ENV http_proxy=http://192.168.98.199:8080
ENV https_proxy=http://192.168.98.199:8080


ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
    && apt-get -y install apt-utils \
    && apt-get -y install libaio-dev \
    && apt-get -y install unzip \
    && apt-get -y install git \
    && apt-get -y install nano \
    && apt-get -y install telnet \
    && apt-get -y install curl \
    && apt-get -y install htop \
    && apt-get install tzdata -y \
    && mkdir -p /logs


RUN chmod -R 777 /logs/

ENV TZ=Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

COPY . /app


# INSTALL DEPENDENCY PYHTON
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


WORKDIR /app

ENV http_proxy=
ENV https_proxy=

CMD ["streamlit", "run", "main.py"]