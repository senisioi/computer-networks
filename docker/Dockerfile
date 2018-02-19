FROM kalilinux/kali-linux-docker

MAINTAINER Sergiu Nisioi <sergiu.nisioi@fmi.unibuc.ro>

USER root

RUN apt-get update 
RUN apt-get install -y build-essential git net-tools arp-scan nmap rtpflood python python-pip
RUN pip install scapy

RUN useradd -u 1000 -m athena
RUN mkdir /home/rtuser
USER rtuser
WORKDIR /home/rtuser
