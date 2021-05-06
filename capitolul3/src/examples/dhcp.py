#!/usr/bin/env python3

'''
Sample script to send a DHCP discover
'''
from scapy.sendrecv import sendp, sniff
from scapy.all import DHCP, ARP, BOOTP, Ether, UDP, TCP, IP, srp1

# data link layer
ethernet = Ether()
ethernet.dst = 'ff:ff:ff:ff:ff:ff'

# network layer
ip = IP()
ip.dst = '192.168.0.255'

# transport layer
udp = UDP()
udp.sport = 68
udp.dport = 67

# application layer
bootp = BOOTP()
bootp.flags = 1

dhcp = DHCP()
dhcp.options = [("message-type", "discover"), "end"]

packet = ethernet / ip / udp / bootp / dhcp

ans = srp1(packet, iface='wlp4s0')
ans.show()