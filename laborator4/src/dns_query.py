'''
Sample script to send a DNS query 
'''
import scapy
from scapy.sendrecv import sendp, sniff, sr1
from scapy.all import  IP, UDP, DNS, DNSQR

network_layer = IP(dst = '8.8.8.8')

transport_layer = UDP(dport = 53)

dns = DNS(rd = 1)
dns_query = DNSQR(qname = 'fmi.unibuc.ro')
dns.qd = dns_query

pachet = network_layer / transport_layer / dns

answer = sr1(pachet)
print answer[DNS].summary()
