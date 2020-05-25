#!/usr/bin/env python3

from scapy.all import *

icmp = ICMP(type='echo-request')
ip = IP(dst="137.254.16.101")
pachet = ip / icmp

# folosim sr1 pentru send și un reply
rec = sr1(pachet)
rec.show()
