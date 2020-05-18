#!/usr/bin/env python3

import socket
import select
from scapy.all import *

raw_udp = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto=socket.IPPROTO_UDP)
raw_udp.bind(('0.0.0.0', 53))
# dummy socket to keep the port busy:  https://stackoverflow.com/a/9969618
simple_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
simple_udp.bind(('0.0.0.0', 53))


while True:
    #responses, _, _ = select.select([raw_udp, simple_udp], [], [])
    # citeste doar din RAW UDP
    request, adresa_sursa = raw_udp.recvfrom(65535)
    # converitm octetii in pachet scapy
    packet = IP(request)
    dns = packet.getlayer(DNS)
    if dns.opcode == 0: # dns QUERY
        '''
            qname= 'fmi.unibuc.ro.'
            qtype= A
            qclass= IN
        '''
        print ("got: ")
        print (packet.show())
        if dns.qd.qname == b'fmi.unibuc.ro.':
               ip = packet.getlayer(IP)
               udp = packet.getlayer(UDP)
               ip_response = IP(src=ip.dst, dst=ip.src)
               udp_response = UDP(sport=udp.dport, dport=udp.sport)
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
               response =  udp_response / dns_response
               print (response.__str__)
               raw_udp.sendto(bytes(response), adresa_sursa)
raw_udp.close()
simple_udp.close()