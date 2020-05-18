#!/usr/bin/env python3

import socket
import sys
# try to detect whether IPv6 is supported at the present system and
# fetch the IPv6 address of localhost.
if not socket.has_ipv6:
    print("Nu putem folosi IPv6")
    sys.exit(1)

# "::0" este echivalent cu 0.0.0.0
infos = socket.getaddrinfo("::0", 8080, socket.AF_INET6, 0, socket.IPPROTO_TCP, socket.AI_CANONNAME)
# [(<AddressFamily.AF_INET6: 10>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('::', 8080, 0, 0))]
# info contine o lista de parametri, pentru fiecare interfata, cu care se poate instantia un socket
print (len(infos))
1

info = infos[0]
adress_family = info[0].value # AF_INET
socket_type = info[1].value # SOCK_STREAM
protocol = info[2].value # IPPTROTO_TCP == 6
cannonical_name = info[3] # tot ::0 adresa de echivalenta cu 0.0.0.0
adresa_pt_bind = info[4] # tuplu ('::', 8080, 0, 0):
'''
Metodele de setare a adreselor (bind, connect, sendto) 
pentru socketul IPv6 sunt un tuplu cu urmatoarele valori:
- adresa_IPv6               ::0
- port                      8080
- flow_label ca in header   0
- scope-id - id pt NIC      0
mai multe detalii: https://stackoverflow.com/a/11930859
'''

# instantiem socket TCP cu AF_INET6
s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)

# executam bind pe tuplu ('::', 8080, 0, 0)
s.bind(adresa_pt_bind)

# restul e la fel ca la IPv4
s.listen(1)
conn, addr = s.accept()
print(conn.recv(1400))
conn.send(b'am primit mesajul')
conn.close()
s.close()