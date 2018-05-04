# inainte de toate trebuie adaugata o regula de ignorare 
# a pachetelor RST pe care ni le livreaza kernelul automat
# iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP
from scapy.all import *

ip = IP()
ip.src = # ip-ul nostru
ip.dst = # ip-ul serverului 
tcp = TCP()
tcp.sport = # un port la alegere
tcp.dport = # portul destinatie pe care ruleaza serverul
tcp.seq = # un sequence number la alegere
tcp.flags = 'S' # flag de SYN

SYN = ip/tcp
raspuns_SYN_ACK = sr1(SYN)
rasp_ack = raspuns_SYN_ACK.seq + 1
rasp_seq = tcp.seq + 1

tcp.seq = rasp_seq
tcp.ack = rasp_ack
tcp.flags = 'A'

ACK= ip / tcp
send (ACK)

