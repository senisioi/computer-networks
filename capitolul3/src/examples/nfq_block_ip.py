#!/usr/bin/env python3

from scapy.all import *
from netfilterqueue import NetfilterQueue as NFQ
import os


def proceseaza(pachet):
    # octeti raw, ca dintr-un raw socket
    octeti = pachet.get_payload()
    # convertim octetii in pachet scapy
    scapy_packet = IP(octeti)
    scapy_packet.summary()
    if scapy_packet[IP].src == '198.10.0.2':
        print("Drop la: ", scapy_packet.summary())
        pachet.drop()
    else:
        print("Accept la: ", scapy_packet.summary())
        pachet.accept()


queue = NFQ()
try:
    os.system("iptables -I INPUT -j NFQUEUE --queue-num 5")
    # bind trebuie să folosească aceiași coadă ca cea definită în iptables
    queue.bind(5, proceseaza)
    queue.run()
except KeyboardInterrupt:
    queue.unbind()
