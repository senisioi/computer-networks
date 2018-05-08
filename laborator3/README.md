# Laborator 3 

## Inainte de a incepe
Trebuie sa reconstruim imaginea folosind [Dockerfile din laborator3](https://github.com/senisioi/computer-networks/blob/master/laborator3/docker/Dockerfile) care are configurat deja `USER root` si instalarea pentru tcpdump.
```
cd computer-networks/laborator3
docker build --no-cache -t baseimage ./docker/
# pentru a porni containerle, rulam docker-compose din directorul superior cu ..:
../docker-compose up -d

# sau din directorul computer-networks: 
# ./docker-compose -f laborator3/docker-compose.yml up -d
```

## Cuprins
- [TCP segment](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#tcp)
- [IP datagram](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#ip)
- [Ethernet frame](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#ether)
- [Scapy tutorial](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#scapy)


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

Prima specificatie a protocolului TCP a fost in: 
- [RFC793](https://tools.ietf.org/html/rfc793).
- [RFC2581](https://tools.ietf.org/html/rfc2581) contine informatiile cu privire la congestion control
- Source Port si Destination Port sunt porturile sursa si destinatie pentru conexiunea curenta
- [Sequence si Acknowledgment](http://packetlife.net/blog/2010/jun/7/understanding-tcp-sequence-acknowledgment-numbers/) sunt folosite pentru indicarea secventei de bytes transmisa si notificarea ca acea secventa a fost primita
- Data offset - dimensiunea header-ului in multipli de 32 de biti
- Res - 3 biti rezervati
- NS, CWR, ECE - biti pentru notificarea explicita a existentei congestionarii [ECN](http://www.inacon.de/ph/data/TCP/Header_fields/TCP-Header-Field-ECN_OS_RFC-793_3540.htm), explicat mai bine si [aici](http://blog.catchpoint.com/2015/10/30/tcp-flags-cwr-ece/). NS e o suma binara pentru siguranta, CWR - indica necesitatea micsorarii ferestrei de congestionare iar ECE este un bit de echo care indica prezenta congestionarii.
- URG, ACK, PSH, RST, SYN, FIN - [flags](http://www.inacon.de/ph/data/TCP/Header_fields/TCP-Header-Field-Flags_OS_RFC-793_3540.htm)
- Window Size - folosit pentru [flow control](http://www.ccs-labs.org/teaching/rn/animations/flow/), exemplu [aici](http://www.inacon.de/ph/data/TCP/Header_fields/TCP-Header-Field-Window-Size_OS_RFC-793.htm)
- Urgent Pointer - mai multe detalii in [RFC6093](https://tools.ietf.org/html/rfc6093), pe scurt explicat [aici](http://packetlife.net/blog/2011/mar/2/tcp-flags-psh-and-urg/) si un exemplu de functionare [aici](https://osqa-ask.wireshark.org/questions/25929/tcp-urgent-pointer-and-urgent-data).
- Optiuni - sunt optionale, iar o [lista completa de optiuni se gaseste aici](http://www.networksorcery.com/enp/Protocol/tcp.htm#Options). Probabil cele mai importante sunt prezentate pe scurt in [acest tutorial](http://www.firewall.cx/networking-topics/protocols/tcp/138-tcp-options.html): [Maximum Segment Size](http://fivedots.coe.psu.ac.th/~kre/242-643/L08/html/mgp00005.html), [Window Scaling](http://fivedots.coe.psu.ac.th/~kre/242-643/L08/html/mgp00009.html), Selective Acknowledgement, [Timestamps](http://fivedots.coe.psu.ac.th/~kre/242-643/L08/html/mgp00011.html) (pentru round-trip-time), si NOP (no option pentru separare intre optiuni). 
- Checksum - suma in complement fata de 1 a bucatilor de cate 16 biti, complementata cu 1, vezi mai multe detalii [aici](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Checksum_computation) si [RFC1071 aici](https://tools.ietf.org/html/rfc1071)
Se calculeaza din concatenarea: unui pseudo-header de IP [adresa IP sursa, IP dest (32 biti fiecare), placeholder (8 biti setati pe 0), [protocol](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers) (8 biti), si lungimea in bytes a intregii sectiuni TCP sau UDP (16 biti)], TCP sau UDP header cu checksum setat pe 0, si sectiunea de date. Pentru simplitate, mai jos este redata sectiunea pentru care calculam checksum la UDP: IP pseudo-header + UDP header + Data.
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

# optiunie se pot seta folosind obiectul TCPOptions
print TCPOptions[1]
{'Mood': 25, 'MSS': 2, 'UTO': 28, 'SAck': 5, 'EOL': 0, 'WScale': 3, 'TFO': 34, 'AltChkSumOpt': 15, 'Timestamp': 8, 'NOP': 1, 'AltChkSum': 14, 'SAckOK': 4}

print TCPOptions[0]
{0: ('EOL', None), 1: ('NOP', None), 2: ('MSS', '!H'), 3: ('WScale', '!B'), 4: ('SAckOK', None), 5: ('SAck', '!'), 8: ('Timestamp', '!II'), 14: ('AltChkSum', '!BH'), 15: ('AltChkSumOpt', None), 25: ('Mood', '!p'), 28: ('UTO', '!H'), 34: ('TFO', '!II')}
```
In scapy optiunile pot fi setate printr-o lista tupluri: `[(Optiune1, Valoare1), ('NOP', None), ('NOP', None), (Optiune2, Valoare2), ('EOL', None)]`. TCPOptions[0] indica optiunile si indicele de accesare pentru TCPOptions[1]. Iar TCPOptions[1] indica formatul (sau pe cati biti) se regaseste fiecare optiune. Formatul cu `!` ne spune ca biti pe care ii setam trebuie sa fie in [Network Order (Big Endian)](https://stackoverflow.com/questions/13514614/why-is-network-byte-order-defined-to-be-big-endian) iar literele arata formatul pe care trebuie sa il folosim cu [struct.pack](https://docs.python.org/2/library/struct.html#format-characters). Spre exemplu, window scale are o dimensiune de 1 byte (`!B`) si valoarea trebuie setata corespunzator:
```python
import struct
optiune = 'WScale'
op_index = TCPOptions[1][optiune]
op_format = TCPOptions[0][op_index]
print op_format
# optiunea window scale are o dimensiune de 1 byte (`!B`)
# ('WScale', '!B')
valoare = struct.pack(op_format[1], 15)
# valoarea 15 a fost inpachetata intr-un string de 1 byte
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
Prima specificatie a protocolului IP a fost in: 
- [RFC791](https://tools.ietf.org/html/rfc791).
- Version - 4 pentru ipv4
- IHL - similar cu Data offset de la TCP, ne spune care este dimnesiunea header-ului in multiplii de 32 de biti. Daca nu sunt specificate optiuni, IHL este 5.
- [DSCP](https://en.wikipedia.org/wiki/Differentiated_services) - in tcpdump mai apare ca ToS (type of service), acest camp a fost definit in [RFC2474](https://tools.ietf.org/html/rfc2474) si seteaza politici de retransmitere a pachetelor, ca [aici](https://en.wikipedia.org/wiki/Differentiated_services#Commonly_used_DSCP_values).
- ECN - definit in [RFC3186](https://tools.ietf.org/html/rfc3168) este folosit de catre routere, pentru a notifica transmitatorii cu privire la existenta unor congestionari pe retea. Setarea flag-ului pe 11 (Congestion Encountered - CE), va determina layer-ul TCP sa isi seteze ECE, CWR si NS.
- Total length - lumgimea totala in octeti, cu header si date pentru intreg-ul datagram
- Identification - un id care este folosit pentru idenficarea pachetelor fragmentate
- Flags - flag-uri de fragmentare, bitul 0 e rezervat, bitul 1 indica DF - don't fragment, iar bitul 2 setat, ne spune ca mai urmeaza fragmente.
- Fragment Offset - offset-ul unui fragment current in raport cu fragmentul initial, masurat in multiplu de 8 octeti (64 biti).
- Time to Live (TTL) -  numarul maxim de routere prin care poate trece IP datagram pana in punctul in care e discarded
- Protocol - indica codul [protocolului](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers) din interiorul secventei de date
- Header checksum - aceeasi metoda de checksum ca la [TCP si UDP](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Checksum_computation), adica suma in complement 1, a fragmentelor de cate 16 biti, dar in cazul acesta se aplica doar pentru header. Aceasta suma este putin redundanta avand in vedere ca se mai calculeaza o data peste pseudoheader-ul de la TCP sau UDP.
- Source/Destination Address - adrese ip pe 32 de biti
- Options - prezinta diverse riscuri, [conform wikipedia](https://en.wikipedia.org/wiki/IPv4#Options) sau acestui [raport](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2005/EECS-2005-24.pdf). Mai multe informatii despre rolul acestora puteti gasi [aici](http://www.tcpipguide.com/free/t_IPDatagramOptionsandOptionFormat.htm), [aici](http://www.cc.ntut.edu.tw/~kwke/DC2006/ipo.pdf) si specificatia completa [aici](http://www.networksorcery.com/enp/protocol/ip.htm#Options).

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

# observam ca DSCP si ECN nu sunt inca implementate in scapy.
# daca vrem sa le folosim, va trebui sa setam tos cu o valoare
# pe 8 biti care sa reprezinte DSCP si ECN folosind: int('DSCP_BINARY_STR' + 'ECN_BINARY_STR', 2)
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
La nivelurile legatura de date si fizic, avem standardele [IEEE 802](https://ieeexplore.ieee.org/browse/standards/get-program/page/series?id=68) care ne definesc structurile frame-urilor. Fiecare secventa de 4 liniute reprezinta un octet (nu un bit ca in diagramele anterioare). 
- [preambulul](https://networkengineering.stackexchange.com/questions/24842/how-does-the-preamble-synchronize-other-devices-receiving-clocks) are o dimensiune de 7 octeti, fiecare octet de forma 10101010, si este folosit pentru sincronizarea ceasului receiver-ului. Mai multe detalii despre ethernet in acest [clip](https://www.youtube.com/watch?v=5u52wbqBgEY).
- SF (start of frame) reprezinta un octet (10101011) care delimiteaza start of frame
- [adresele MAC](http://www.dcs.gla.ac.uk/~lewis/networkpages/m04s03EthernetFrame.htm), sursa si destinatie, sunt reprezentate pe 6 octeti
- [802-1q](https://en.wikipedia.org/wiki/IEEE_802.1Q) este un header pentru retele locale virtuale (VLAN). Lipseste din scapy, dar poate fi [adaugat manual](https://stackoverflow.com/questions/29133482/scapy-how-to-insert-a-new-layer-802-1q-into-existing-packet).
- EthType indica codul [protocolului](https://en.wikipedia.org/wiki/EtherType#Examples) din layer-ul superior acestui frame
- codul [CRC](https://en.wikipedia.org/wiki/Cyclic_redundancy_check#Computation) pentru [polinomul de Ethernet](https://xcore.github.io/doc_tips_and_tricks/crc.html#the-polynomial)
- [Interpacket Gap](https://en.wikipedia.org/wiki/Interpacket_gap) - nu face efectiv parte din frame, ci reprezinta un spatiu de inactivitate, mai bine explicat [aici](http://www.mplsvpn.info/2010/05/what-is-inter-packet-gap-or-inter-frame.html).

##### Ethernet object in scapy:
```python
e = Ether()       
e.show()
WARNING: Mac address to reach destination not found. Using broadcast.
###[ Ethernet ]### 
  dst= ff:ff:ff:ff:ff:ff
  src= 02:42:c6:0d:00:0e
  type= 0x9000

# preambulul, start of frame si interpacket gap sunt parte a nivelului fizic
# CRC-ul este calculat automat de catre kernel
# singurele campuri de care trebuie sa tinem cont sunt adresele si EthType
```


<a name="scapy"></a> 
### [Scapy](https://scapy.readthedocs.io/en/latest/usage.html#starting-scapy)
Este o unealta de python pe care o putem folosi pentru a construi pachete si configura manual headerele mesajelor transmise. 
Presupunem ca am deschis scapy in rt1 (`docker-compose exec --user root rt1 scapy`) si vrem sa trimitem un mesaj prin UDP unui server care ruleaza pe rt3 si care asculta pe portul 10000. 
```python
# presupunem ca rulam serverul pe rt3 si scapy pe rt1

udp_layer = UDP()
udp_layer.sport = 54321
udp_layer.dport = 10000

ip_layer = IP()
ip_layer.src = '198.13.0.14'
ip_layer.dst = '172.111.0.14'

mesaj = Raw()
mesaj.load = "impachetat manual"

# folosim operatorul / pentru a stivui layerele
# sau pentru a adauga layerul cel mai din dreapta
# in sectiunea de date/payload a layerului din stanga sa
pachet_complet = i / u / mesaj

# trimitem fara a astepta un raspuns
send(pachet_complet)

# trimitem si inregristram raspunsurile
ans, unans = sr(pachet_complet, retry=3)
print ans
# <Results: TCP:0 UDP:1 ICMP:0 Other:0>

# ans contine o lista de tupluri [(request1, response1), (request2, response2)]
# raspunsul la primul requeste este mesajul primit de la server:
print ans[0][1]
# <IP  version=4L ihl=5L tos=0x0 len=38 id=44462 flags=DF frag=0L ttl=63 proto=udp chksum=0x1b80 src=172.111.0.14 dst=198.13.0.14 options=[] |<UDP  sport=10000 dport=54312 len=18 chksum=0x72bc |<Raw  load='am primit' |>>>

```

In scapy avem mai multe functii de trimitere a pachetelor:
- `send()` - trimite un pachet pe retea la nivelul network, iar sectiunea de ethernet este completata de catre sistem
- `answered, unanswered = sr()` - send_receive - trimite pachete pe retea in loop si inregistreaza si raspunsurile primite
- `answer = sr1()` - send_receive_1 - trimite pe retea ca sr1, dar inregistreaza primul raspuns primit

Pentru a trimite pachete la nivelul legatura de date, completand manual campuri din sectiunea Ethernet, avem echivalentul functiilor de mai sus:
- `sendp()` - send_ethernet trimite un pachet la nivelul data-link, cu layer Ether custom
- `answered, unanswered = srp()` - send_receive_ethernet trimite pachete la layer 2 si inregistreaza si raspunsurile
- `answer = srp1()` - send_receive_1_ethernet la fel ca srp, dar inregistreaza doar primul raspuns

### Exercitii
1. Folositi exemplul de mai sus pentru a trimite mesaje intre serverul pe UDP si scapy.
2. Rulati 3-way handshake intre rt1 si mid1 folosind containerele definite in laborator3, astfel: containerul rt1 va rula laborator2/tcp_server.py pe adresa '0.0.0.0', iar in containerul mid1 rulati scapy (puteti folosi comanda: `docker-compose exec --user root mid1 scapy`) si configurati fisierul din [laborator3/src/tcp_handshake.py](https://github.com/senisioi/computer-networks/blob/master/laborator3/src/tcp_handshake.py) pentru a face 3-way handshake.
3. Configurati optiunea pentru Maximum Segment Size (MSS) astfel incat sa il notificati pe server ca segmentul maxim este de 1 byte. Puteti sa-l configurati cu 0?
4. Trimiteti un mesaj serverului folosind flag-ul PSH.
5. Setati flag-urile ECN in IP si flag-ul ECE in TCP pentru a notifica serverul de congestionarea retelei.
6. [TCP Syn Scanning](https://scapy.readthedocs.io/en/latest/usage.html#syn-scans) - folositi scapy pentru a crea un pachet cu IP-ul destinatie 193.226.51.6 (site-ul facultatii) si un layer de TCP cu dport=(10, 500) pentru a afla care porturi sunt deschise comunicarii cu TCP pe site-ul facultatii.
