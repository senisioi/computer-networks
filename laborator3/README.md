# Laborator 3 

## Cuprins
- [Introducere](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#intro)
- [TCP segment](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#tcp)
- [IPv4 datagram](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#ip)
- [IPv6 datagram](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#ipv6)
- [Ethernet frame](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#ether)
- [Scapy tutorial](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#scapy)

<a name="intro"></a> 
## Introducere
Trebuie să avem pregătită o imagine care este deja configurată cu `USER root` și tcpdump.
```
cd computer-networks

# ștergem toate containerele create default
./docker-compose down

# ștergem rețelele create anterior ca să nu se suprapună cu noile subnets
docker network prune

# lucrăm cu ../docker-compose doar din laborator3
cd laborator3

# pentru a porni containerle, rulăm docker-compose din directorul superior cu:
../docker-compose up -d

# sau din directorul computer-networks: 
# ./docker-compose -f laborator3/docker-compose.yml up -d
```

Fișierul `docker-compose.yml` definește 4 containere `server, router, client, middle` având ip-uri fixe în subneturi diferite, iar `router` este un container care funcționează ca router între cele două subrețele. Observați în command pentru server: `ip route add 172.111.0.0/16 via 198.13.0.1` adăugarea unei rute către subnetul în care se află clientul via ip-ul containerului router.
Serviciile router și middle sunt setate să facă forwarding `net.ipv4.ip_forward=1`. Prin comanda comentată de la router, poate fi programat să renunțe la pachete cu o probabilitate de 50%: `tc qdisc add dev eth0 root netem loss 50% && tc qdisc add dev eth1 root netem loss 50%`. Puteți folosi această setare dacă doriți să verificați retransmiterea mesajelor în cazul TCP.
Nu în ultimul rând, pentru a putea face handshake programatic, trebuie să dezactivăm regula automată de reset a sistemului de operare: `iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP`.


<a name="tcp"></a> 
### [TCP Segment Header](https://tools.ietf.org/html/rfc793#page-15)
```
  0                   1                   2                   3   Offs.
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |          Source Port          |       Destination Port        |  1
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                        Sequence Number                        |  2
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                    Acknowledgment Number                      |  3
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 | Data  |0 0 0| |C|E|U|A|P|R|S|F|                               |
 |Offset | Res.|N|W|C|R|C|S|S|Y|I|            Window             |  4
 |       |     |S|R|E|G|K|H|T|N|N|                               |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |           Checksum            |         Urgent Pointer        |  5
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                    Options   (if data offset > 5)             | 
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                    Application data                           | 
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
```

Prima specificație a protocolului TCP a fost în [RFC793](https://tools.ietf.org/html/rfc793)
- Foarte bine explicat [aici](http://zwerd.com/2017/11/24/TCP-connection.html) si [aici](http://www.firewall.cx/networking-topics/protocols/tcp.html)
- [RFC2581](https://tools.ietf.org/html/rfc2581) conține informațiile cu privire la congestion control
- Source Port și Destination Port sunt porturile sursa și destinație pentru conexiunea curentă
- [Sequence și Acknowledgment](http://www.firewall.cx/networking-topics/protocols/tcp/134-tcp-seq-ack-numbers.html) sunt folosite pentru indicarea secvenței de bytes transmisă și notificarea că acea secvență a fost primită
- Data offset - dimensiunea header-ului în multipli de 32 de biți
- Res - 3 biți rezervați
- NS, CWR, ECE - biți pentru notificarea explicită a existenței congestionării [ECN](http://www.inacon.de/ph/data/TCP/Header_fields/TCP-Header-Field-ECN_OS_RFC-793_3540.htm), explicat mai bine și [aici](http://blog.catchpoint.com/2015/10/30/tcp-flags-cwr-ece/). NS e o sumă binară pentru sigurantă, CWR - indică necesitatea micsorării ferestrei de congestionare iar ECE este un bit de echo care indică prezența congestionarii.
- URG, ACK, PSH, RST, SYN, FIN - [flags](http://www.firewall.cx/networking-topics/protocols/tcp/136-tcp-flag-options.html)
- Window Size - folosit pentru [flow control](http://www.ccs-labs.org/teaching/rn/animations/flow/), exemplu [aici](http://www.inacon.de/ph/data/TCP/Header_fields/TCP-Header-Field-Window-Size_OS_RFC-793.htm)
- Urgent Pointer - mai multe detalii in [RFC6093](https://tools.ietf.org/html/rfc6093), pe scurt explicat [aici](http://www.firewall.cx/networking-topics/protocols/tcp/137-tcp-window-size-checksum.html).
- Opțiuni - o [listă completă de opțiuni se găsește aici](http://www.networksorcery.com/enp/Protocol/tcp.htm#Options). Probabil cele mai importante sunt prezentate pe scurt în [acest tutorial](http://www.firewall.cx/networking-topics/protocols/tcp/138-tcp-options.html): [Maximum Segment Size](http://fivedots.coe.psu.ac.th/~kre/242-643/L08/html/mgp00005.html), [Window Scaling](http://fivedots.coe.psu.ac.th/~kre/242-643/L08/html/mgp00009.html), Selective Acknowledgement, [Timestamps](http://fivedots.coe.psu.ac.th/~kre/242-643/L08/html/mgp00011.html) (pentru round-trip-time), și NOP (no option pentru separare între opțiuni). 
- Checksum - suma în complement fată de 1 a bucăților de câte 16 biți, complementatî cu 1, vezi mai multe detalii [aici](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Checksum_computation) și [RFC1071 aici](https://tools.ietf.org/html/rfc1071)
Se calculează din concatenarea: unui pseudo-header de IP [adresa IP sursă, IP dest (32 biti fiecare), placeholder (8 biti setati pe 0), [protocol](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers) (8 biti), și lungimea în bytes a întregii secțiuni TCP sau UDP (16 biti)], TCP sau UDP header cu checksum setat pe 0, și secțiunea de date. Pentru simplitate, mai jos este redată secțiunea pentru care calculăm checksum la UDP: IP pseudo-header + UDP header + Data.
```
  0                   1                   2                   3   
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |                       Source Address                          |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                    Destination Address                        | IP pseudo-header
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |  placeholder  |    protocol   |        UDP/TCP length         |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |          Source Port          |       Destination Port        |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-   UDP header
 |          Length               |              0                |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |                       payload/data                            |  Transport data
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
```

<a name="tcp_scapy"></a> 
##### TCP object in scapy:
```python
tcp_obj = TCP()
tcp_obj.show()
###[ TCP ]### 
  sport= 20
  dport= 80
  seq= 0
  ack= 0
  dataofs= None
  reserved= 0
  flags= S
  window= 8192
  chksum= None
  urgptr= 0
  options= {}

# tipurile de flag-uri acceptate:
print TCP.flags.names
FSRPAUECN
'FIN, SYN, RST, PSH, ACK, URG, ECE, CWR, NS'
# pentru a seta PSH si ACK, folosim un singur string:
tcp.flags = 'PA'

# opțiunile se pot seta folosind obiectul TCPOptions
print TCPOptions[1]
{'Mood': 25, 'MSS': 2, 'UTO': 28, 'SAck': 5, 'EOL': 0, 'WScale': 3, 'TFO': 34, 'AltChkSumOpt': 15, 'Timestamp': 8, 'NOP': 1, 'AltChkSum': 14, 'SAckOK': 4}

print TCPOptions[0]
{0: ('EOL', None), 1: ('NOP', None), 2: ('MSS', '!H'), 3: ('WScale', '!B'), 4: ('SAckOK', None), 5: ('SAck', '!'), 8: ('Timestamp', '!II'), 14: ('AltChkSum', '!BH'), 15: ('AltChkSumOpt', None), 25: ('Mood', '!p'), 28: ('UTO', '!H'), 34: ('TFO', '!II')}
```

<a name="tcp_options"></a> 
În scapy opțiunile pot fi setate printr-o listă tupluri: `[(Optiune1, Valoare1), ('NOP', None), ('NOP', None), (Optiune2, Valoare2), ('EOL', None)]`. TCPOptions[0] indica optiunile si indicele de accesare pentru TCPOptions[1]. Iar TCPOptions[1] indică formatul (sau pe cați biți) se regăseste fiecare opțiune. Formatul cu `!` ne spune că biții pe care îi setăm trebuie să fie în [Network Order (Big Endian)](https://stackoverflow.com/questions/13514614/why-is-network-byte-order-defined-to-be-big-endian) iar literele arată formatul pe care trebuie să îl folosim cu [struct.pack](https://docs.python.org/2/library/struct.html#format-characters). Spre exemplu, window scale are o dimensiune de 1 byte (`!B`) și valoarea trebuie setată corespunzător:
```python
import struct
optiune = 'WScale'
op_index = TCPOptions[1][optiune]
op_format = TCPOptions[0][op_index]
print op_format
# opțiunea window scale are o dimensiune de 1 byte (`!B`)
# ('WScale', '!B')
valoare = struct.pack(op_format[1], 15)
# valoarea 15 a fost împachetată într-un string de 1 byte
tcp.option = [(optiune, valoare)]
```

<a name="ip"></a> 
### [Internet Protocol Datagram v4 - IPv4](https://tools.ietf.org/html/rfc791#page-11)
```
  0                   1                   2                   3   Offs.
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
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
Prima specificație a protocolului IP a fost în: 
- [RFC791](https://tools.ietf.org/html/rfc791).
- Version - 4 pentru ipv4
- IHL - similar cu Data offset de la TCP, ne spune care este dimnesiunea header-ului în multiplii de 32 de biți. Dacă nu sunt specificate opțiuni, IHL este 5.
- [DSCP](https://en.wikipedia.org/wiki/Differentiated_services) - în tcpdump mai apare ca ToS (type of service), acest camp a fost definit în [RFC2474](https://tools.ietf.org/html/rfc2474) și setează politici de retransmitere a pachetelor, ca [aici](https://en.wikipedia.org/wiki/Differentiated_services#Commonly_used_DSCP_values). Aici puteți găsi un [ghid de setare pentru DSCP](https://tools.ietf.org/html/rfc4594#page-19).
- ECN - definit în [RFC3186](https://tools.ietf.org/html/rfc3168) este folosit de către routere, pentru a notifica transmițătorii cu privire la existența unor congestionări pe rețea. Setarea flag-ului pe 11 (Congestion Encountered - CE), va determina layer-ul TCP să își seteze ECE, CWR și NS.
- Total length - lumgimea totală in octeti, cu header și date pentru întreg-ul datagram
- Identification - un id care este folosit pentru idenficarea pachetelor fragmentate
- Flags - flag-uri de fragmentare, bitul 0 e rezervat, bitul 1 indică DF - don't fragment, iar bitul 2 setat, ne spune că mai urmează fragmente.
- Fragment Offset - offset-ul unui fragment curent în raport cu fragmentul inițial, măsurat în multiplu de 8 octeți (64 biți).
- Time to Live (TTL) -  numărul maxim de routere prin care poate trece IP datagram pâna în punctul în care e discarded
- Protocol - indică codul [protocolului](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers) din interiorul secvenței de date
- Header checksum - aceeași metodă de checksum ca la [TCP si UDP](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Checksum_computation), adică suma în complement 1, a fragmentelor de câte 16 biți, dar în cazul acesta se aplică **doar pentru header**. Această sumă este puțin redundantă având în vedere că se mai calculează o dată peste pseudoheader-ul de la TCP sau UDP.
- Source/Destination Address - adrese ip pe 32 de biți
- Options - prezintă diverse riscuri, [conform wikipedia](https://en.wikipedia.org/wiki/IPv4#Options) sau acestui [raport](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2005/EECS-2005-24.pdf). Mai multe informații despre rolul acestora puteți găsi [aici](http://www.tcpipguide.com/free/t_IPDatagramOptionsandOptionFormat.htm), [aici](http://www.cc.ntut.edu.tw/~kwke/DC2006/ipo.pdf) și specificația completă [aici](http://www.networksorcery.com/enp/protocol/ip.htm#Options).

<a name="ip_scapy"></a> 
##### IPv4 object in scapy:
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

<a name="ipv6"></a> 
### [Internet Protocol Datagram v6 - IPv6](https://tools.ietf.org/html/rfc2460#page-4)
```
  0                   1                   2                   3   Offs.
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
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
Prima specificație a protocolului IPv6 a fost în 1998 [rfc2460](https://tools.ietf.org/html/rfc2460): 
- Version - 6 pentru ipv6
- Traffic Class        8-bit [traffic class field](https://tools.ietf.org/html/rfc2460#section-7), similar cu [DSCP](https://en.wikipedia.org/wiki/Differentiated_services) 
- Flow Label           [20-bit flow label](https://tools.ietf.org/html/rfc2460#section-6), semantica definită [aici](https://tools.ietf.org/html/rfc2460#page-30)
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


```python
IPv6().show()
###[ IPv6 ]### 
  version= 6
  tc= 0
  fl= 0
  plen= None
  nh= No Next Header
  hlim= 64
  src= ::1
  dst= ::1
```

<a name="ether"></a> 
### [Ethernet Frame](https://en.wikipedia.org/wiki/Ethernet_frame#Structure)
```
    0    1    2    3    4    5    6    7    Octet nr.
 *----*----*----*----*----*----*----*----*
 |            Preabmle              | SF |
 *----*----*----*----*----*----*----*----*
 |          Source MAC         |
 *----*----*----*----*----*----*
 |     Destination MAC         |
 *----*----*----*----*----*----*
 | 802-1Q (optional) |
 *----*----*----*----*
 | EthType |
 *----*----*----*--------------------------------------------
 |   Application + TCP + IP data / payload (max 1500 octets)
 *----*----*----*--------------------------------------------
 |  32-bit CRC  |
 *----*----*----*----*----*----*----*-------
 |     Interpacket Gap  - interval de timp |
 *----*----*----*----*----*----*----*-------
 ```
La nivelurile legatură de date și fizic, avem standardele [IEEE 802](https://ieeexplore.ieee.org/browse/standards/get-program/page/series?id=68) care ne definesc structurile frame-urilor. Fiecare secventă de 4 liniuțe reprezintă un octet (nu un bit ca in diagramele anterioare). 
- [preambulul](https://networkengineering.stackexchange.com/questions/24842/how-does-the-preamble-synchronize-other-devices-receiving-clocks) are o dimensiune de 7 octeți, fiecare octet de forma 10101010, și este folosit pentru sincronizarea ceasului receiver-ului. Mai multe detalii despre ethernet în acest [clip](https://www.youtube.com/watch?v=5u52wbqBgEY).
- SF (start of frame) reprezinta un octet (10101011) care delimitează start of frame
- [adresele MAC](http://www.dcs.gla.ac.uk/~lewis/networkpages/m04s03EthernetFrame.htm), sursă și destinație, sunt reprezentate pe 6 octeți
- [802-1q](https://en.wikipedia.org/wiki/IEEE_802.1Q) este un header pentru rețele locale virtuale (VLAN). Lipsește din scapy, dar poate fi [adaugat manual](https://stackoverflow.com/questions/29133482/scapy-how-to-insert-a-new-layer-802-1q-into-existing-packet).
- EthType indică codul [protocolului](https://en.wikipedia.org/wiki/EtherType#Examples) din layer-ul superior acestui frame
- codul [CRC](https://en.wikipedia.org/wiki/Cyclic_redundancy_check#Computation) pentru [polinomul de Ethernet](https://xcore.github.io/doc_tips_and_tricks/crc.html#the-polynomial)
- [Interpacket Gap](https://en.wikipedia.org/wiki/Interpacket_gap) - nu face efectiv parte din frame, ci reprezintă un spațiu de inactivitate, mai bine explicat [aici](http://www.mplsvpn.info/2010/05/what-is-inter-packet-gap-or-inter-frame.html).

##### Ethernet object in scapy:
```python
e = Ether()       
e.show()
WARNING: Mac address to reach destination not found. Using broadcast.
###[ Ethernet ]### 
  dst= ff:ff:ff:ff:ff:ff
  src= 02:42:c6:0d:00:0e
  type= 0x9000

# preambulul, start of frame și interpacket gap sunt parte a nivelului fizic
# CRC-ul este calculat automat de către kernel
# singurele câmpuri de care trebuie să ținem cont sunt adresele și EthType
```


<a name="scapy"></a> 
### [Scapy](https://scapy.readthedocs.io/en/latest/usage.html#starting-scapy)
Este o unealtă de python pe care o putem folosi pentru a construi pachete și configura manual headerele mesajelor transmise. 
Presupunem că am deschis scapy în rt1 (`docker-compose exec --user root rt1 scapy`) și vrem să trimitem un mesaj prin UDP unui server care rulează pe rt3 și care ascultă pe portul 10000. 
```python
# presupunem că rulam serverul pe rt1 și scapy pe mid1

udp_layer = UDP()
udp_layer.sport = 54321
udp_layer.dport = 10000

ip_layer = IP()
ip_layer.src = '198.13.0.15'
ip_layer.dst = '198.13.0.14'

mesaj = Raw()
mesaj.load = "impachetat manual"

# folosim operatorul / pentru a stivui layerele
# sau pentru a adăuga layerul cel mai din dreapta
# în secțiunea de date/payload a layerului din stânga sa
pachet_complet = ip_layer / udp_layer / mesaj

# trimitem făra a aștepta un răspuns
send(pachet_complet)

# trimitem și înregristrăm răspunsurile
ans, unans = sr(pachet_complet, retry=3)
print ans
# <Results: TCP:0 UDP:1 ICMP:0 Other:0>

# ans conține o listă de tupluri [(request1, response1), (request2, response2)]
# răspunsul la primul requeste este mesajul primit de la server:
print ans[0][1]
# <IP  version=4L ihl=5L tos=0x0 len=38 id=44462 flags=DF frag=0L ttl=63 proto=udp chksum=0x1b80 src=172.111.0.14 dst=198.13.0.14 options=[] |<UDP  sport=10000 dport=54312 len=18 chksum=0x72bc |<Raw  load='am primit' |>>>

```

În scapy avem mai multe funcții de trimitere a pachetelor:
- `send()` - trimite un pachet pe rețea la nivelul network, iar secțiunea de ethernet este completată de către sistem
- `answered, unanswered = sr()` - send_receive - trimite pachete pe rețea în loop și înregistrează și răspunsurile primite
- `answer = sr1()` - send_receive_1 - trimite pe rețea ca sr1, dar înregistrează primul răspuns primit

Pentru a trimite pachete la nivelul legatură de date, completând manual câmpuri din secțiunea Ethernet, avem echivalentul funcțiilor de mai sus:
- `sendp()` - send_ethernet trimite un pachet la nivelul data-link, cu layer Ether custom
- `answered, unanswered = srp()` - send_receive_ethernet trimite pachete la layer 2 și înregistrează și răspunsurile
- `answer = srp1()` - send_receive_1_ethernet la fel ca srp, dar înregistreazî doar primul răspuns

###### Exemplu ping
```python
ICMP().show()
###[ ICMP ]### 
  type= echo-request
  code= 0
  chksum= None
  id= 0x0
  seq= 0x0

icmp = ICMP(type = 'echo-request')
ip = IP(dst = "137.254.16.101")
pachet = ip / icmp
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

###### Exemplu DNS request
```python
ip = IP(dst = '8.8.8.8')
transport = UDP(dport = 53)

dns = DNS(rd = 1)
dns_query = DNSQR(qname = 'fmi.unibuc.ro')
dns.qd = dns_query

answer = sr1(ip / transport / dns)
print (answer[DNS].summary())
```


### Exerciții
1. Folosiți exemplul de mai sus pentru a trimite mesaje între serverul pe UDP și scapy.
2. Rulați 3-way handshake între server și client folosind containerele definite în laborator3, astfel: containerul server va rula laborator2/tcp_server.py pe adresa '0.0.0.0', iar în containerul client rulați scapy (puteți folosi comanda: `docker-compose exec --user root mid1 scapy`) și configurați fișierul din [laborator3/src/tcp_handshake.py](https://github.com/senisioi/computer-networks/blob/master/laborator3/src/tcp_handshake.py) pentru a face 3-way handshake.
3. Configurați opțiunea pentru Maximum Segment Size (MSS) astfel încat să îl notificați pe server că segmentul maxim este de 1 byte. Puteți să-l configurați cu 0?
4. Trimiteți un mesaj serverului folosind flag-ul PSH.
5. Setați flag-urile ECN în IP și flag-ul ECE in TCP pentru a notifica serverul de congestionarea rețelei.
6. [TCP Syn Scanning](https://scapy.readthedocs.io/en/latest/usage.html#syn-scans) - folosiți scapy pentru a crea un pachet cu IP-ul destinație 193.226.51.6 (site-ul facultății) și un layer de TCP cu dport=(10, 500) pentru a afla care porturi sunt deschise comunicării cu TCP pe site-ul facultății.
7. Urmăriți mai multe exemple din scapy [aici](https://scapy.readthedocs.io/en/latest/usage.html#simple-one-liners)