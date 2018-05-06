# inainte de toate trebuie adaugata o regula de ignorare 
# a pachetelor RST pe care ni le livreaza kernelul automat
# iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP
from scapy.all import *

ip = IP()
ip.src = ''
ip.dst = ''


tcp = TCP()
tcp.sport = 54321
tcp.dport = 10000

## SYN ##
tcp.seq = 100
tcp.flags = 'S' # flag de SYN
raspuns_syn_ack = sr1(ip/tcp)

tcp.seq += 1
tcp.ack = raspuns_syn_ack.seq + 1
tcp.flags = 'A'
ACK = ip / tcp

send(ACK)

for ch in "salut, lume":
    tcp.flags = 'PA'
    tcp.ack = raspuns_syn_ack.seq + 1
    rcv = sr1(ip/tcp/ch)
    rcv
    tcp.seq += 1
