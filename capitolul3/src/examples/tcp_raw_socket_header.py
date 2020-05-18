#!/usr/bin/env python3

import socket
import struct

# instantierea obiectului cu SOCK_RAW si IPPROTO_TCP
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto=socket.IPPROTO_TCP)
data, adresa = s.recvfrom(65535)

# daca din router apelam catre server: sock.connect(('server', 2222)), acesta va primi:
(b'E\x00\x00<;\xb9@\x00@\x06r\xeb\xc6\n\x00\x01\xc6\n\x00\x02\xb1\x16\x08\xae;\xde\x84\xca\x00\x00\x00\x00\xa0\x02\xfa\xf0\x8cF\x00\x00\x02\x04\x05\xb4\x04\x02\x08\nSJ\xb6$\x00\x00\x00\x00\x01\x03\x03\x07', ('198.10.0.1', 0))

tcp_part = data[20:]
# ignoram headerul de IP de 20 de bytes si extrage header TCP fara optiuni
tcp_header_fara_optiuni = struct.unpack('!HHLLHHHH', tcp_part[:20])
source_port, dest_port, sequence_nr, ack_nr, doff_res_flags, window, checksum, urgent_ptr = tcp_header_fara_optiuni

print("Port sursa: ", source_port)
print("Port destinatie: ", dest_port)
print("Sequence number: ", sequence_nr)
print("Acknowledgment number: ", ack_nr)
data_offset = doff_res_flags >> 12
print("Data Offset: ", data_offset) # la cate randuri de 32 de biti sunt datele

offset_in_bytes = (doff_res_flags >> 12) * 4
if doff_res_flags >> 12 > 5:
  print("TCP header are optiuni, datele sunt abia peste  ", offset_in_bytes, " bytes")

NCEUAPRSF = doff_res_flags & 0b111111111 # & cu 9 de 1
print("NS: ", (NCEUAPRSF >> 8) & 1 )
print("CWR: ", (NCEUAPRSF >> 7) & 1 )
print("ECE: ", (NCEUAPRSF >> 6) & 1 )
print("URG: ", (NCEUAPRSF >> 5) & 1 )
print("ACK: ", (NCEUAPRSF >> 4) & 1 )
print("PSH: ", (NCEUAPRSF >> 3) & 1 )
print("RST: ", (NCEUAPRSF >> 2) & 1 )
print("SYN: ", (NCEUAPRSF >> 1) & 1 )
print("FIN: ", (NCEUAPRSF & 1))

print("Window: ", window)
print("Checksum: ", checksum)
print("Urgent Pointer: ", urgent_ptr)

optiuni_tcp = tcp_part[20:offset_in_bytes]

# urmarim documentul de aici: https://www.iana.org/assignments/tcp-parameters/tcp-parameters.xhtml


option = optiuni_tcp[0]
print (option) 
# option 2 inseamna MSS, Maximum Segment Size
'''
https://tools.ietf.org/html/rfc793#page-18
'''
option_len = optiuni_tcp[1]
print(option_len)
# MSS are dimensiunea 4
# valoarea optiunii este de la 2 la option_len
option_value = optiuni_tcp[2:option_len]
# MSS e pe 16 biti:
print(struct.unpack('!H', option_value))
# MSS similar cu MTU

# continuam cu urmatoarea optiune
optiuni_tcp = optiuni_tcp[option_len:]
option = optiuni_tcp[0]
print (option) 
# option 4 inseamna SACK Permitted
'''
https://tools.ietf.org/html/rfc2018#page-3
https://packetlife.net/blog/2010/jun/17/tcp-selective-acknowledgments-sack/
+---------+---------+
| Kind=4  | Length=2|
+---------+---------+
'''
option_len = optiuni_tcp[1]
print(option_len)
# SACK Permitted are dimensiunea 2
# asta inseamna ca e un flag boolean fara alte valori aditionale

# continuam cu urmatoarea optiune
optiuni_tcp = optiuni_tcp[option_len:]
option = optiuni_tcp[0]
print (option) 
# option 8 inseamna Timestamps
'''
https://tools.ietf.org/html/rfc7323#page-12
+-------+-------+---------------------+---------------------+
|Kind=8 |Leng=10|   TS Value (TSval)  |TS Echo Reply (TSecr)|
+-------+-------+---------------------+---------------------+
    1       1              4                     4
'''
option_len = optiuni_tcp[1]
print(option_len)
# Timestamps are dimensiunea 10 bytes
# are doua valori stocate fiecare pe cate 4 bytes
valori = struct.unpack('!II', optiuni_tcp[2:option_len])
print (valori)
(1397405220, 0) # valorile Timestamp

# continuam cu urmatoarea optiune
optiuni_tcp = optiuni_tcp[option_len:]
option = optiuni_tcp[0]
print (option) 
# option 1 inseamna No-Operation
'''
asta inseamna ca nu folosim optiunea si trecem mai departe
https://tools.ietf.org/html/rfc793#page-18
'''

# continuam cu urmatoarea optiune
optiuni_tcp = optiuni_tcp[1:]
option = optiuni_tcp[0]
print (option) 
# option 3 inseamna Window Scale
'''
https://tools.ietf.org/html/rfc7323#page-8
+---------+---------+---------+
| Kind=3  |Length=3 |shift.cnt|
+---------+---------+---------+
'''
option_len = optiuni_tcp[1]
print(option_len)
# lungime 3, deci reprezentarea valorii este pe un singur byte
valoare = struct.unpack('!B', optiuni_tcp[2:option_len])
print(valoare)
# Campul Window poate fi scalat cu valoarea Window * 2^WindowScaleOption
