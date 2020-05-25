#!/usr/bin/env python3

import socket
import struct

data = b'E\x00\x00!\xc2\xd2@\x00@\x11\xeb\xe1\xc6\n\x00\x01\xc6\n\x00\x02\x08\xae\t\x1a\x00\r\x8c6salut'

# extragem headerul de baza de IP:
ip_header = struct.unpack('!BBHHHBBH4s4s', data[:20])
ip_ihl_ver, ip_dscp_ecn, ip_tot_len, ip_id, ip_frag, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr = ip_header

print("Versiune IP: ", ip_ihl_ver >> 4)
# & cu 1111 pentru a extrage ultimii 4 biti
print("Internet Header Length: ", ip_ihl_ver & 0b1111)
print("DSCP: ", ip_dscp_ecn >> 6)
print("ECN: ", ip_dscp_ecn & 0b11)  # & cu 11 pt ultimii 2 biti
print("Total Length: ", ip_tot_len)
print("ID: ", ip_id)
print("Flags: ", bin(ip_frag >> 13))
print("Fragment Offset: ", ip_frag & 0b111)  # & cu 111
print("Time to Live: ", ip_ttl)
print("Protocol nivel superior: ", ip_proto)
print("Checksum: ", ip_check)
print("Adresa sursa: ", socket.inet_ntoa(ip_saddr))
print("Adresa destinatie: ", socket.inet_ntoa(ip_daddr))

if ip_ihl_ver & (16 - 1) == 5:
    print("header-ul de IP nu are optiuni")
