#!/usr/bin/env python3

import socket
import sys
# try to detect whether IPv6 is supported at the present system and
# fetch the IPv6 address of localhost.
if not socket.has_ipv6:
    print("Nu putem folosi IPv6")
    sys.exit(1)

s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
adresa = ('::', 8080, 0, 0)
s.connect(adresa)

# restul e la fel ca la IPv4
s.send(b'Salut prin IPv6')
print (s.recv(1400))
s.close()