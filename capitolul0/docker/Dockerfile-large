FROM ubuntu:20.04

MAINTAINER Sergiu Nisioi <sergiu.nisioi@fmi.unibuc.ro>

USER root

RUN apt-get update && apt-get install -y build-essential git net-tools arp-scan python3 python3-pip tcpdump ethtool nmap rtpflood

# move tcpdump from the default location to /usr/local
RUN mv /usr/sbin/tcpdump /usr/local/bin
# add the new location to the PATH in case it's not there
ENV PATH="/usr/local/bin:${PATH}"

RUN apt-get update && apt-get install -y graphviz imagemagick texlive
RUN pip3 install cryptography matplotlib graphviz vpython PyX geoip2 scipy notebook

RUN wget https://web.archive.org/web/20191227182209/https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz
RUN tar -xvf GeoLite2-City.tar.gz && mv GeoLite2-City_20191224/GeoLite2-City.mmdb /GeoLite2-City.mmdb

RUN apt-get update && apt-get install -y libgeos-* proj-* libproj-dev libgeos++-dev python3-cartopy python3-tk

RUN pip3 install --pre scapy[complete]

#RUN git clone https://github.com/senisioi/scapy.git && cd scapy && python3 setup.py install

RUN apt-get update && apt-get install -y iputils-ping dnsutils