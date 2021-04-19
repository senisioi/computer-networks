# Capitolul 4 - Network Layer

## Cuprins
- [Requiremets](#intro)
- [IPv4 Datagram](#ipv4)
  - [IPv4 Raw Socket](#ip_raw_socket)
  - [IPv4 Scapy](#ip_scapy)
- [Subnetting, Routing, and other stuff](#ipv4routing)
- [IPv6 Datagram](#ipv6)
  - [IPv6 Socket](#ipv6_socket)
  - [IPv6 Scapy](#ipv6_scapy)
- [Internet Control Message Protocol (ICMP)](#scapy_icmp)
- [Exerciții](#exercitii)

<a name="intro"></a> 
## Introducere
**Important:** continuăm cu aceeași configurație ca în capitolul3 și urmărim secțiunea introductivă de acolo.
```
cd computer-networks

# ștergem toate containerele create default
docker-compose down

# ștergem rețelele create anterior ca să nu se suprapună cu noile subnets
docker network prune

# lucrăm cu docker-compose.yml din capitolul3
cd capitolul3
docker-compose up -d

# sau din directorul computer-networks: 
# docker-compose -f capitolul3/docker-compose.yml up -d
```



<a name="ipv4"></a> 
## [Internet Protocol Datagram v4 - IPv4](https://tools.ietf.org/html/rfc791#page-11)
```
  0               1               2               3              4 Offs.
  0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |Version|  IHL  |     DSCP  |ECN|          Total Length         |  1
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |         Identification        |Flags|      Fragment Offset    |  2
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |  Time to Live |    Protocol   |         Header Checksum       |  3
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                       Source Address                          |  4
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                    Destination Address                        |  5
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                    Options    (if IHL  > 5)                   |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                   Application + TCP data                      | 
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

```
Prima specificație a protocolului IP a fost în [RFC791](https://tools.ietf.org/html/rfc791) iar câmpurile sunt explicate foarte bine în aceste [note de curs](https://engineering.purdue.edu/kak/compsec/NewLectures/Lecture16.pdf#page=14).

#### Câmpurile antetului

- Version - 4 pentru ipv4
- IHL - similar cu Data offset de la TCP, ne spune care este dimnesiunea header-ului în multiplii de 32 de biți. Dacă nu sunt specificate opțiuni, IHL este 5.
- [DSCP](https://en.wikipedia.org/wiki/Differentiated_services) - în tcpdump mai apare ca ToS (type of service), acest camp a fost definit în [RFC2474](https://tools.ietf.org/html/rfc2474) și setează politici de retransmitere a pachetelor, ca [aici](https://en.wikipedia.org/wiki/Differentiated_services#Commonly_used_DSCP_values). Aici puteți găsi un [ghid de setare pentru DSCP](https://tools.ietf.org/html/rfc4594#page-19). Câmpul acesta are un rol important în prioritizarea pachetelor de tip video, voce sau streaming.
- ECN - definit în [RFC3186](https://tools.ietf.org/html/rfc3168) este folosit de către routere, pentru a notifica transmițătorii cu privire la existența unor congestionări pe rețea. Setarea flag-ului pe 11 (Congestion Encountered - CE), va determina layer-ul TCP să își seteze ECE, CWR și NS.
- Total length - lumgimea totală in octeti, cu header și date pentru întreg-ul datagram
- Identification - un id care este folosit pentru idenficarea pachetelor fragmentate
- [Flags](https://en.wikipedia.org/wiki/IPv4#Flags) - flag-uri de fragmentare, bitul 0 e rezervat, bitul 1 indică DF - don't fragment, iar bitul 2 setat, ne spune că mai urmează fragmente.
- Fragment Offset - offset-ul unui fragment curent în raport cu fragmentul inițial, măsurat în multiplu de 8 octeți (64 biți).
- Time to Live (TTL) -  numărul maxim de routere prin care poate trece IP datagram pâna în punctul în care e discarded
- Protocol - indică codul [protocolului](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers) din interiorul secvenței de date
- Header checksum - aceeași metodă de checksum ca la [TCP si UDP](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Checksum_computation), adică suma în complement 1, a fragmentelor de câte 16 biți, dar în cazul acesta se aplică **doar pentru header**. Această sumă este puțin redundantă având în vedere că se mai calculează o dată peste pseudoheader-ul de la TCP sau UDP.
- Source/Destination Address - adrese ip pe 32 de biți
- [Options](https://www.iana.org/assignments/ip-parameters/ip-parameters.xhtml) - sunt opțiuni la nivelul IP. Mai multe informații despre rolul acestora puteți găsi [aici](http://www.tcpipguide.com/free/t_IPDatagramOptionsandOptionFormat.htm), [aici](http://www.cc.ntut.edu.tw/~kwke/DC2006/ipo.pdf) și specificația completă [aici](http://www.networksorcery.com/enp/protocol/ip.htm#Options). Din [lista de 30 de optiuni](https://www.iana.org/assignments/ip-parameters/ip-parameters.xhtml), cel putin 11 sunt deprecated in mod oficial, 8 sunt experimentale/ putin documentate, din cele ramase, o buna parte sunt neimplementate de catre routere sau prezinta riscuri de securitate. Spre exemplu, optiunea [traceroute](https://networkengineering.stackexchange.com/questions/10453/ip-traceroute-rfc-1393), si optiunea [record route](https://networkengineering.stackexchange.com/questions/41886/how-does-the-ipv4-option-record-route-work) care nu au fost implementate, sau optiunile [source based routing](https://howdoesinternetwork.com/2014/source-based-routing) cu risc sporit de securitate, mai multe în [acest raport](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2005/EECS-2005-24.pdf). 

###### Wireshark IPv4 Options
Ca să captați cu [Wireshark](https://osqa-ask.wireshark.org/questions/25504/how-to-capture-based-on-ip-header-length-using-a-capture-filter) IP datagrams care conțin opțiuni, puteți folosi filtrul care verifică ultimii 4 biți ai primului octet: `ip[0] & 0xf != 5`. Veți putea observa pachete cu [protocolul IGMP](https://www.youtube.com/watch?v=2fduBqQQbps) care are setată [opțiunea Router Alert](http://www.rfc-editor.org/rfc/rfc6398.html) 


<a name="ip_raw_socket"></a> 
### IPv4 Object from Raw Socket
Folosim datele ca octeti din exemplul cu UDP Raw Socket de mai sus:
```python
import socket
import struct

data = b'E\x00\x00!\xc2\xd2@\x00@\x11\xeb\xe1\xc6\n\x00\x01\xc6\n\x00\x02\x08\xae\t\x1a\x00\r\x8c6salut'

# extragem headerul de baza de IP:
ip_header = struct.unpack('!BBHHHBBH4s4s', data[:20])
ip_ihl_ver, ip_dscp_ecn, ip_tot_len, ip_id, ip_frag, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr = ip_header

print("Versiune IP: ", ip_ihl_ver >> 4)
print("Internet Header Length: ", ip_ihl_ver & 0b1111) # & cu 1111 pentru a extrage ultimii 4 biti
print("DSCP: ", ip_dscp_ecn >> 6)
print("ECN: ", ip_dscp_ecn & 0b11) # & cu 11 pt ultimii 2 biti
print("Total Length: ", ip_tot_len)
print("ID: ", ip_id)
print("Flags: ",  bin(ip_frag >> 13))
print("Fragment Offset: ",  ip_frag & 0b111) # & cu 111
print("Time to Live: ",  ip_ttl)
print("Protocol nivel superior: ",  ip_proto)
print("Checksum: ",  ip_check)
print("Adresa sursa: ", socket.inet_ntoa(ip_saddr))
print("Adresa destinatie: ", socket.inet_ntoa(ip_daddr))

if ip_ihl_ver & (16 - 1) == 5:
  print ("header-ul de IP nu are optiuni")

Versiune IP:  4
Internet Header Length:  5
DSCP:  0
ECN:  0
Total Length:  33
ID:  49874
Flags:  0b10
Fragment Offset:  0
Time to Live:  64
Protocol nivel superior:  17
Checksum:  60385
Adresa sursa:  198.10.0.1
Adresa destinatie:  198.10.0.2
``` 



<a name="ip_scapy"></a> 
### IPv4 object in scapy
```python
ip = IP() 
ip.show()
###[ IP ]### 
  version= 4
  ihl= None
  tos= 0x0
  len= None
  id= 1
  flags= 
  frag= 0
  ttl= 64
  proto= hopopt
  chksum= None
  src= 127.0.0.1
  dst= 127.0.0.1
  \options\

# observăm că DSCP și ECN nu sunt înca implementate în scapy.
# daca vrem să le folosim, va trebui să setăm tos cu o valoare
# pe 8 biți care să reprezinte DSCP și ECN folosind: int('DSCP_BINARY_STR' + 'ECN_BINARY_STR', 2)
# pentru a seta DSCP cu cod AF32 pentru video streaming și ECN cu notificare de congestie: ip.tos = int('011100' + '11', 2)
```

#### Atacuri simple folosind IP
- [IP Spoofing](https://engineering.purdue.edu/kak/compsec/NewLectures/Lecture16.pdf#page=71)
- [IP Spoofing Mitigation](https://engineering.purdue.edu/kak/compsec/NewLectures/Lecture16.pdf#page=84)
- [Network Ingress Filtering: Defeating Denial of Service Attacks which employ IP Source Address Spoofing](https://tools.ietf.org/html/bcp38)



<a name="ipv4routing"></a> 
## Subnetting, Routing, and other stuff
Pe scurt, aici sunt link-urile cu informații esențiale despre rutare:
- mai întâi urmăriți în partea de curs informațiile de bază despre [curs forwarding](https://github.com/senisioi/computer-networks/tree/2021/curs#forwarding) și [curs rutare](https://github.com/senisioi/computer-networks/tree/2021/curs#routing)
- Fraida Fund are un tutorial foarte bun despre cum pot fi alocate [IP-uri subrețelelor](https://witestlab.poly.edu/blog/designing-subnets/); cu toate că nu aveți cont pe GINI, puteți replica întregul set-up pe docker modificând docker-compose.yml din capitolul3
- pentur [Distance Vector Routing](https://en.wikipedia.org/wiki/Distance-vector_routing_protocol#Example) există un exemplu foarte ușor de urmărit pe wikipedia, inclusiv cu [Split Horizon si Poison Reverse](https://en.wikipedia.org/wiki/Split_horizon_route_advertisement)
- [Link State Routing](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=397) este foarte bine explicat în cartea pentru curs
- OSPF
- un alt tutorial al Fraidei Fund, despre BGP este [cel de aici](https://witestlab.poly.edu/blog/a-peek-into-internet-routing/)
- [Autonomous Systems](https://www.cidr-report.org/as2.0/)
- [BGP looking glasses](https://www.bgp4.as/looking-glasses)
- [MPLS](https://www.youtube.com/watch?v=U1w-b9GIt0k) prezentat într-un scurt video


<a name="ipv6"></a> 
## [Internet Protocol Datagram v6 - IPv6](https://tools.ietf.org/html/rfc2460#page-4)
```
  0               1               2               3              4 Offs.
  0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |Version| Traffic Class |           Flow Label                  |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |         Payload Length        |  Next Header  |   Hop Limit   |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                                                               |
 -                                                               -
 |                                                               |
 -                         Source Address                        -
 |                                                               |
 -                                                               -
 |                                                               |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                                                               |
 -                                                               -
 |                                                               |
 -                      Destination Address                      -
 |                                                               |
 -                                                               -
 |                                                               |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
```
Prima specificație a protocolului IPv6 a fost în 1998 [rfc2460](https://tools.ietf.org/html/rfc2460) iar detaliile despre semnificația câmpurilor se găsesc în aceste [note de curs](https://engineering.purdue.edu/kak/compsec/NewLectures/Lecture16.pdf#page=23).

#### Câmpurile antetului IPv6

- Version - 6 pentru ipv6
- Traffic Class        8-bit [traffic class field](https://tools.ietf.org/html/rfc2460#section-7), similar cu [DSCP](https://en.wikipedia.org/wiki/Differentiated_services) 
- Flow Label           [20-bit flow label](https://tools.ietf.org/html/rfc2460#section-6), semantica definită [aici](https://tools.ietf.org/html/rfc2460#page-30), este folosit și în instanțierea socketului prin IPv6.
- Payload Length       16-bit unsigned integer care include si extra headerele adaugate
- Next Header          8-bit selector similar cu câmpul Protocol din IPv4
- Hop Limit            8-bit unsigned integer similar cu câmpul TTL din IPv4
- Source Address       128-bit addresă sursă
- Destination Address  128-bit addresă destinație
- Headerul poate fi extins prin adăugarea mai multor headere in payload, vezi [aici](https://tools.ietf.org/html/rfc2460#page-6)
- Pseudoheaderul pentru checksum-ul calculat de layerele de transport se formează diferit, vezi [aici](https://tools.ietf.org/html/rfc2460#page-27)
- Adresele sunt stocate in 8 grupuri de câte 16 biti: `fe80:cd00:0000:0000:1257:0000:0000:729c`
- Numărul total de adrese IPv6 este 340282366920938463463374607431768211456, suficient pentru toate device-urile existente
- Adresa IPv6 pentru loopback localhost este `::1/128` 
- Dublu `::` este o variantă prin care se prescurtează secventele continue cele mai din stânga de `0`, adresa de mai sus este prescurtată: `fe80:cd00::1257:0:0:729c`

<a name="ipv6_socket" ></a>
### IPv6 Socket
#### Server
```python
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
```

#### Client
```python
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
```

<a name="ipv6_scapy" ></a>
### IPv6 Scapy
```python
ip = IPv6()
ip.show()
###[ IPv6 ]### 
  version= 6
  tc= 0
  fl= 0
  plen= None
  nh= No Next Header
  hlim= 64
  src= ::1
  dst= ::1

ip.dst = '::1' # localhost
# trimitem la un server UDP care asteapta pe (::0, 8081, 0, 0)
udp = UDP(sport=1234, dport=8081)  
send(ip / udp / b'salut prin ipv6')

```

<a name="scapy_icmp"></a> 
### [Internet Control Message Protocol (ICMP)](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol#Control_messages)

Am discutat despre ICMP și ping pentru a verifica dacă două device-uri pot comunica unul cu altul. Principala funcție a protocolului ICMP este de [a raprota erori](https://www.cloudflare.com/learning/ddos/glossary/internet-control-message-protocol-icmp/) iar [mesajele de control](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol#Control_messages) pot varia de la faptul că un host, port sau protocol este inaccesibil până la notificarea că TTL a expirat în tranzit.

```python
ICMP().show()
###[ ICMP ]### 
  type= echo-request
  code= 0
  chksum= None
  id= 0x0
  seq= 0x0

# facem un pachet echo-request, ping
icmp = ICMP(type = 'echo-request')
ip = IP(dst = "137.254.16.101")
pachet = ip / icmp

# folosim sr1 pentru send și un reply
rec = sr1(pachet)
rec.show()

###[ IP ]### 
  version= 4
  ihl= 5
  tos= 0x0
  len= 28
  id= 48253
  flags= DF
  frag= 0
  ttl= 242
  proto= icmp
  chksum= 0x23e7
  src= 137.254.16.101
  dst= 1.15.3.1
  \options\
###[ ICMP ]### 
     type= echo-reply
     code= 0
     chksum= 0x0
     id= 0x0
     seq= 0x0
```


<a name="exercitii"></a> 
## Exerciții
1. Urmăriți mai multe exemple din scapy [aici](https://scapy.readthedocs.io/en/latest/usage.html#simple-one-liners)
2. Implementați un traceroute folosind ICMP.
3. Urmăriți opțiunile de sysctls din linux și încercați diferite valori pentru udp_mem, tcp_ecn, tcp_min_snd_mss, [ip_nonlocal_bind](https://www.cyberciti.biz/faq/linux-bind-ip-that-doesnt-exist-with-net-ipv4-ip_nonlocal_bind/), sau mtu în containere.
