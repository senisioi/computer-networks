#!/usr/bin/env python3

import socket
import select
from scapy.all import *

simple_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
simple_udp.bind(('0.0.0.0', 53))

while True:
    request, adresa_sursa = simple_udp.recvfrom(65535)
    # converitm octetii in pachet scapy
    packet = DNS(request)
    dns = packet.getlayer(DNS)

    if dns is not None and dns.opcode == 0: # dns QUERY
        '''
            qname= 'fmi.unibuc.ro.'
            qtype= A
            qclass= IN
        '''
        print ("got: ")
        print (packet.summary())
        dns_answer = DNSRR(      # DNS Reply
           rrname=dns.qd.qname, # for question
           ttl=330,             # DNS entry Time to Live
           type="A",            
           rclass="IN",
           rdata='1.1.1.1')     # found at IP: 1.1.1.1 :)
        dns_response = DNS(
                          id = packet[DNS].id, # DNS replies must have the same ID as requests
                          qr = 1,              # 1 for response, 0 for query 
                          aa = 0,              # Authoritative Answer
                          rcode = 0,           # 0, nicio eroare http://www.networksorcery.com/enp/protocol/dns.htm#Rcode,%20Return%20code
                          qd = packet.qd,      # request-ul original
                          an = dns_answer)     # obiectul de reply
        print('response:')
        print (dns_response.summary())
        simple_udp.sendto(bytes(dns_response), adresa_sursa)
simple_udp.close()