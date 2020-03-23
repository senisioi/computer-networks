# Capitolul 3 

## Cuprins
- [Introducere](#intro)
  - [Network Stacks](#stacks)
  - [Big Endian (Network Order) vs. Little Endian](#endianness)
  - [Network Stacks](#stacks)
- [UDP Datagram](#udp)
  - [UDP Socket](#udp_socket)
  - [UDP Raw Socket](#udp_raw_socket)
  - [UDP Scapy](#udp_scapy)
- [TCP Segment](#tcp)
  - [TCP Retransmissions](#tcp_retransmission)
  - [TCP Socket](#tcp_socket)
  - [TCP Raw Socket](#tcp_raw_socket)
  - [TCP Scapy](#tcp_scapy)
  - [TCP Options](#tcp_options)
- [IPv4 Datagram](#ipv4)
  - [IPv4 Raw Socket](#ip_raw_socket)
  - [IPv4 Scapy](#ip_scapy)
- [IPv6 Datagram](#ipv6)
- [Ethernet Frame](#ether)
  - [Ethernet Object in Scapy](#ether_scapy)
- [Scapy Tutorial](#scapy)
  - [Exemplu ICMP ping](#scapy_ping)
  - [Exemplu DNS](#scapy_dns)
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
|`l`|long|integer|64||
|`L`|unsigned long|integer|64||
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

<a name="#udp_raw_socket"></a> 
### Raw Socket UDP
Există raw socket cu care putem citi sau trimite pachetele in formă binară. Explicații mai multe puteți găsi și [aici](https://opensourceforu.com/2015/03/a-guide-to-using-raw-sockets/). Pentru a instantia RAW Socket avem nevoie de acces cu drepturi de administrator. Deci este de preferat să lucrăm în containerele de docker: `docker-compose exec server bash`

```python
import socket

# instantierea obiectului cu SOCK_RAW si IPPROTO_UDP
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto=socket.IPPROTO_UDP)

# recvfrom citeste din buffer 16 octeti indiferent de port
date, adresa = s.recvfrom(16)
# daca in buffer sunt mai mult de 16 bytes, recvfrom va citi doar 16 iar restul vor fi discarded


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
Se calculează din concatenarea: unui pseudo-header de IP [adresa IP sursă, IP dest (32 biti fiecare), placeholder (8 biti setati pe 0), [protocol](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers) (8 biti), și lungimea în bytes a întregii secțiuni TCP sau UDP (16 biti)], TCP sau UDP header cu checksum setat pe 0, și secțiunea de date.


<a name="tcp_retransmission"></a>
### Exercițiu TCP retransmission
TCP este un protocol care oferă siguranța transmiterii pachetelor, în cazul în care un stream de octeți este trimis, se așteaptă o confirmare pentru acea secvență de bytes. Dacă confirmarea nu este primită se încearcă retransmiterea. Pentru a observa retransmisiile, putem introduce un delay artificial sau putem ignora anumite pachete pe rețea. Folosim un tool linux numit [netem](https://wiki.linuxfoundation.org/networking/netem) sau mai pe scurt [aici](https://stackoverflow.com/questions/614795/simulate-delayed-and-dropped-packets-on-linux).

În containerul router, în [docker-compose.yml](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/docker-compose.yml) este commented comanda pentru [/drop_packages.sh](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/src/drop_packages.sh). Fisierul respectiv este copiat în directorul root `/` in container prin comanda `COPY src/*.sh /` din Dockerfile-lab3. 
Prin scriptul comentat, routerul poate fi programat să renunțe la pachete cu o probabilitate de 50%: `tc qdisc add dev eth0 root netem loss 50% && tc qdisc add dev eth1 root netem loss 50%`. Puteți folosi această setare dacă doriți să verificați retransmiterea mesajelor în cazul TCP.


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
Un exemplu de 3-way handshake facut cu Raw Socket este în directorul [capitolul3/src/raw_socket_handshake.py](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/src/raw_socket_handshake.py)


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

<a name="ip_raw_socket"></a> 
### IPv4 Object from Raw Socket
Cel mai simplu este să citim headerul de IP dintr-un pachet UDP raw socket:
```python
import socket

# instantierea obiectului cu SOCK_RAW si IPPROTO_UDP
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto=socket.IPPROTO_UDP)

# recvfrom citeste din buffer 16 octeti indiferent de port
date, adresa = s.recvfrom(16)
# daca in buffer sunt mai mult de 16 bytes, recvfrom va citi doar 16 iar restul vor fi discarded


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

# extragem headerul de IP:
ip_header = struct.unpack('!BBHHHBBH4s4s', data[:20])
ip_ihl_ver, ip_dscp_ecn, ip_tot_len, ip_id, ip_frag, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr = ip_header

print(socket.inet_ntoa(ip_saddr))
'198.10.0.1'

print(socket.inet_ntoa(ip_daddr))
'198.10.0.2'
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
La nivelurile legatură de date și fizic, avem standardele [IEEE 802](https://ieeexplore.ieee.org/browse/standards/get-program/page/series?id=68) care ne definesc structurile frame-urilor. Pentru nivelul data link, puteti găsi și [aici mai multe detalii explicate](https://notes.shichao.io/tcpv1/ch3/).

Fiecare secventă de 4 liniuțe reprezintă un octet (nu un bit ca in diagramele anterioare) iar headerul cuprinde:
- [preambulul](https://networkengineering.stackexchange.com/questions/24842/how-does-the-preamble-synchronize-other-devices-receiving-clocks) are o dimensiune de 7 octeți, fiecare octet de forma 10101010, și este folosit pentru sincronizarea ceasului receiver-ului. Mai multe detalii despre ethernet în acest [clip](https://www.youtube.com/watch?v=5u52wbqBgEY).
- SF (start of frame) reprezinta un octet (10101011) care delimitează start of frame
- [adresele MAC](http://www.dcs.gla.ac.uk/~lewis/networkpages/m04s03EthernetFrame.htm), sursă și destinație, sunt reprezentate pe 6 octeți
- [802-1q](https://en.wikipedia.org/wiki/IEEE_802.1Q) este un header pentru rețele locale virtuale (VLAN). Lipsește din scapy, dar poate fi [adaugat manual](https://stackoverflow.com/questions/29133482/scapy-how-to-insert-a-new-layer-802-1q-into-existing-packet).
- EthType indică codul [protocolului](https://en.wikipedia.org/wiki/EtherType#Examples) din layer-ul superior acestui frame
- codul [CRC](https://en.wikipedia.org/wiki/Cyclic_redundancy_check#Computation) pentru [polinomul de Ethernet](https://xcore.github.io/doc_tips_and_tricks/crc.html#the-polynomial)
- [Interpacket Gap](https://en.wikipedia.org/wiki/Interpacket_gap) - nu face efectiv parte din frame, ci reprezintă un spațiu de inactivitate, mai bine explicat [aici](http://www.mplsvpn.info/2010/05/what-is-inter-packet-gap-or-inter-frame.html).


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


<a name="scapy"></a> 
## [Tutorial Scapy](https://scapy.readthedocs.io/en/latest/usage.html#starting-scapy)
Este o unealtă de python pe care o putem folosi pentru a construi pachete și configura manual headerele mesajelor transmise. 
Presupunem că am deschis scapy în client (`docker-compose exec client scapy`) și vrem să trimitem un mesaj prin UDP unui server și care ascultă pe portul 10000. 
```python
# presupunem că rulam serverul pe server

udp_layer = UDP()
udp_layer.sport = 54321
udp_layer.dport = 10000

ip_layer = IP()
ip_layer.src = '172.10.0.2'
ip_layer.dst = '198.10.0.2'

mesaj = Raw()
mesaj.load = "payload manual"

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
# <IP  version=4L ihl=5L tos=0x0 len=38 id=44462 flags=DF frag=0L ttl=63 proto=udp chksum=0x1b80 src=172.10.0.2 dst=198.10.0.14 options=[] |<UDP  sport=10000 dport=54312 len=18 chksum=0x72bc |<Raw  load='am primit' |>>>

```

În scapy avem mai multe funcții de trimitere a pachetelor:
- `send()` - trimite un pachet pe rețea la nivelul network, iar secțiunea de ethernet este completată de către sistem
- `answered, unanswered = sr()` - send_receive - trimite pachete pe rețea în loop și înregistrează și răspunsurile primite
- `answer = sr1()` - send_receive_1 - trimite pe rețea ca sr1, dar înregistrează primul răspuns primit

Pentru a trimite pachete la nivelul legatură de date, completând manual câmpuri din secțiunea Ethernet, avem echivalentul funcțiilor de mai sus:
- `sendp()` - send_ethernet trimite un pachet la nivelul data-link, cu layer Ether custom
- `answered, unanswered = srp()` - send_receive_ethernet trimite pachete la layer 2 și înregistrează și răspunsurile
- `answer = srp1()` - send_receive_1_ethernet la fel ca srp, dar înregistreazî doar primul răspuns


<a name="scapy_ping"></a> 
### Exemplu ping
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

<a name="scapy_dns"></a> 
### Exemplu DNS request
```python
ip = IP(dst = '8.8.8.8')
transport = UDP(dport = 53)

dns = DNS(rd = 1)
dns_query = DNSQR(qname = 'fmi.unibuc.ro')
dns.qd = dns_query

answer = sr1(ip / transport / dns)
print (answer[DNS].summary())
```


<a name="exercitii"></a> 
## Exerciții
1. Folosiți exemplul de mai sus pentru a trimite mesaje între serverul pe UDP și scapy.
2. Rulați 3-way handshake între server și client folosind containerele definite în capitolul3, astfel: containerul server va rula capitolul2/tcp_server.py pe adresa '0.0.0.0', iar în containerul client rulați scapy (puteți folosi comanda: `docker-compose exec --user root mid1 scapy`) și configurați fișierul din [capitolul3/src/tcp_handshake.py](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/src/tcp_handshake.py) pentru a face 3-way handshake.
3. Configurați opțiunea pentru Maximum Segment Size (MSS) astfel încat să îl notificați pe server că segmentul maxim este de 1 byte. Puteți să-l configurați cu 0?
4. Trimiteți un mesaj serverului folosind flag-ul PSH.
5. Setați flag-urile ECN în IP și flag-ul ECE in TCP pentru a notifica serverul de congestionarea rețelei.
6. [TCP Syn Scanning](https://scapy.readthedocs.io/en/latest/usage.html#syn-scans) - folosiți scapy pentru a crea un pachet cu IP-ul destinație 193.226.51.6 (site-ul facultății) și un layer de TCP cu dport=(10, 500) pentru a afla care porturi sunt deschise comunicării cu TCP pe site-ul facultății.
7. Urmăriți mai multe exemple din scapy [aici](https://scapy.readthedocs.io/en/latest/usage.html#simple-one-liners)