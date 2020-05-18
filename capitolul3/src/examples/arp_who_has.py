#!/usr/bin/env python3

from scapy.all import *

eth = Ether(dst = "ff:ff:ff:ff:ff:ff")

# adresa proto destinație - IP pentru care dorim să aflăm adersa fizică
arp = ARP(pdst = '198.10.0.1')

# folosim srp1 - send - receive (sr) 1 pachet
# litera p din srp1 indică faptul că trimitem pachetul la layer data link 
answered = srp1(eth / arp, timeout = 2)

if answered is not None:
    print (answered[ARP].psrc)
    # adresa fizică este:
    print (answered[ARP].hwsrc)
else:
    print ("Nu a putut fi gasita") 