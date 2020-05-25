#!/usr/bin/env python3

from scapy.all import *


def handler(pachet):
    if pachet.haslayer(TCP):
        if pachet[TCP].sport == 80 or pachet[TCP].dport == 80:
            if pachet.haslayer(Raw):
                raw = pachet.getlayer(Raw)
                print(raw.load)


sniff(prn=handler)
