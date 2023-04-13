# Capitolul 3 - Transport Layer

## Cuprins
- [Introducere](#intro)
- [UDP Datagram](#udp)
  - [Exemplu de calcul pentru checksum](#checksum)
  - [UDP Socket](#udp_socket)
  - [UDP Raw Socket](#udp_raw_socket)
  - [UDP Scapy](#udp_scapy)
- [TCP Segment](#tcp)
  - [TCP Congestion Control](#tcp_cong)
  - [TCP Options](#tcp_options)
    - [Retransmissions Exercise](#tcp_retransmission)
    - [Congestion Control Exercise](#tcp_cong_ex)
  - [TCP Socket](#tcp_socket)
  - [TCP Raw Socket](#tcp_raw_socket)
  - [TCP Scapy](#tcp_scapy)
  - [TCP Options in Scapy](#tcp_options_scapy)
- [Exerciții](#exercitii)

<a name="intro"></a> 
## Introducere
```
cd computer-networks

# ștergem toate containerele create default
docker compose down

# ștergem rețelele create anterior ca să nu se suprapună cu noile subnets
docker network prune

# lucrăm cu docker compose.yml din capitolul3
cd capitolul3
docker compose up -d

# sau din directorul computer-networks: 
# docker compose -f capitolul3/docker compose.yml up -d
```

Fișierul `docker compose.yml` definește 4 containere `server, router, client, middle` având ip-uri fixe în subneturi diferite, iar `router` este un container care funcționează ca router între cele două subrețele. Observați în [command pentru server](https://github.com/senisioi/computer-networks/blob/2023/capitolul3/src/server.sh): `ip route add 172.10.0.0/16 via 198.10.0.1` adăugarea unei rute către subnetul în care se află clientul via ip-ul containerului router. De asemenea, în containerul client există o rută către server prin containerul router: `ip route add 198.10.0.0/16 via 172.10.0.1`.

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
În capitolul2 există exemple de [server](https://github.com/senisioi/computer-networks/blob/2023/capitolul2/src/udp_server.py) și [client](https://github.com/senisioi/computer-networks/blob/2023/capitolul2/src/udp_client.py) pentru protocolul UDP. Cele mai importante metode de socket udp sunt:
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
Există raw socket cu care putem citi sau trimite pachetele in formă binară. Explicații mai multe puteți găsi și [aici](https://opensourceforu.com/2015/03/a-guide-to-using-raw-sockets/). Pentru a instantia RAW Socket avem nevoie de acces cu drepturi de administrator. Deci este de preferat să lucrăm în containerele de docker: `docker compose exec server bash`

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
Într-un terminal dintr-un container rulați scapy: `docker compose exec client scapy`

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

network_layer = IP(dst='adresa_server')
pachet = network_layer / udp_obj

send(pachet)
```

#### Exercițiu
Porniți un UDP socket server pe un container iar pe containerul client rulați scapy pentru a trimite un pachet. 
Încercați același lucru și pe localhost. 
Captați pachetele pe localhost cu wireshark, ce adrese MAC sunt folosite?
Pe baza [explicațiilor de aici](https://stackoverflow.com/questions/41166420/sending-a-packet-over-physical-loopback-in-scapy), corectați problema trimiterii pachetelor de pe localhost.



<a name="tcp"></a> 
## [TCP Segment]()
### RFCs:
- [rfc9293, 2022](https://www.rfc-editor.org/rfc/rfc9293) - cea mai recentă specificație
- [rfc6528, 2012](https://www.rfc-editor.org/rfc/rfc6528) - Initial Seq Attack
- [rfc6691, 2012](https://www.rfc-editor.org/rfc/rfc6691) - Optiuni și MSS
- [rfc879, 2011](https://www.rfc-editor.org/rfc/rfc6093) - clarificări despre URG
- [rfc879, 1983](https://www.rfc-editor.org/rfc/rfc879) - MSS
- [rfc793, 1981](https://tools.ietf.org/html/rfc793) - specificația inițială

```
  0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |          Source Port          |       Destination Port        |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                        Sequence Number                        |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                    Acknowledgment Number                      |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |  Data |       |C|E|U|A|P|R|S|F|                               |
 | Offset| Rsrvd |W|C|R|C|S|S|Y|I|            Window             |
 |       |       |R|E|G|K|H|T|N|N|                               |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |           Checksum            |         Urgent Pointer        |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                           [Options]                           |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                                                               :
 :                             Data                              :
 :                                                               |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

        Note that one tick mark represents one bit position.
```

Prima specificație a protocolului TCP a fost în [RFC793](https://tools.ietf.org/html/rfc793)
- Foarte bine explicat [aici](http://zwerd.com/2017/11/24/TCP-connection.html), [aici](http://www.firewall.cx/networking-topics/protocols/tcp.html) sau în aceste [note de curs](https://engineering.purdue.edu/kak/compsec/NewLectures/Lecture16.pdf#page=25).
- [RFC2581](https://tools.ietf.org/html/rfc2581) conține informațiile cu privire la congestion control
- Source Port și Destination Port sunt porturile sursa și destinație pentru conexiunea curentă
- [Sequence și Acknowledgment](http://www.firewall.cx/networking-topics/protocols/tcp/134-tcp-seq-ack-numbers.html) sunt folosite pentru indicarea secvenței de bytes transmisă și notificarea că acea secvență a fost primită
- Data offset - dimensiunea header-ului în multipli de 32 de biți
- Res - 3 biți rezervați
- CWR, ECE - biți pentru notificarea explicită a existenței congestionării [ECN](https://www.juniper.net/documentation/us/en/software/junos/cos/topics/concept/cos-qfx-series-explicit-congestion-notification-understanding.html), explicat mai bine și [aici](http://blog.catchpoint.com/2015/10/30/tcp-flags-cwr-ece/).
<!-- NS e o sumă binară pentru sigurantă, CWR - indică necesitatea micsorării ferestrei de congestionare iar ECE este un bit de echo care indică prezența congestionarii. -->
- URG, ACK, PSH, RST, SYN, FIN - [flags](http://www.firewall.cx/networking-topics/protocols/tcp/136-tcp-flag-options.html)
- Window Size - folosit pentru [flow control](http://www.ccs-labs.org/teaching/rn/animations/flow/), exemplu [aici](http://www.inacon.de/ph/data/TCP/Header_fields/TCP-Header-Field-Window-Size_OS_RFC-793.htm)
- Urgent Pointer - mai multe detalii in [RFC6093](https://tools.ietf.org/html/rfc6093), pe scurt explicat [aici](http://www.firewall.cx/networking-topics/protocols/tcp/137-tcp-window-size-checksum.html). Conform ultimei specificații "New applications SHOULD NOT set the URGENT flag [39](https://www.rfc-editor.org/rfc/rfc9293#RFC6093) due to implementation differences and middlebox issues (SHLD-13)."
- Checksum - suma în complement fată de 1 a bucăților de câte 16 biți, complementatî cu 1, vezi mai multe detalii [aici](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Checksum_computation) și [RFC1071 aici](https://tools.ietf.org/html/rfc1071)
Se calculează din concatenarea: unui pseudo-header de IP [adresa IP sursă, IP dest (32 biti fiecare), placeholder (8 biti setati pe 0), [protocol](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers) (8 biti), și lungimea în bytes a întregii secțiuni TCP sau UDP (16 biti)], TCP sau UDP header cu checksum setat pe 0, și secțiunea de date.

<a name="tcp_cong"></a> 
### Controlul congestionării
Pe lângă proprietățile din antet, protocolul TCP are o serie de opțiuni (explicate mai jos) și o serie de euristici prin care se încearcă detectarea și evitarea congestionării rețeleleor.

Explicațiile pe această temă pot fi urmărite și în [capitolul din curs despre congesion control](https://github.com/senisioi/computer-networks/tree/2020/curs#congestion) sau în [notele de curs de aici](https://engineering.purdue.edu/kak/compsec/NewLectures/Lecture16.pdf#page=60). Un exemplu foarte clar este prezentat și [în acest tutorial](https://witestlab.poly.edu/blog/tcp-congestion-control-basics/)

Deși implementările mai noi de TCP pot să difere, principiile după care se ghidează euristicile de control al congestionării sunt aceleași, implementează principiul de creștere aditivă și descreștere multiplicativă și includ:

- [slow start & congestion avoidance](https://tools.ietf.org/html/rfc5681#page-4)
- [fast retransmit & fast recovery](https://tools.ietf.org/html/rfc5681#page-8)

TCP nu trimite pe rețea mai multe pachete decât variabila internă de congestion window cwnd și variabila din header-ul de la receiver (window) `min(cwnd, rwnd)`. 


**Slow start** presupune că începem cu o fereastră inițială în funcție de segmentul maxim. Apoi fereastra crește exponențial până apar pierderi pe rețea: `cwnd += min (N, MSS)`, unde N este numărul de octeți noi confirmați prin ultimul ACK (nu numărul total!). Acest lucru determină o creșterea exponențială a ferestrei de congestionare cwnd care mai este reprezentată ca o dublare. Codul de slow start poate fi verificat în [TCP Reno implementat în linux](https://github.com/torvalds/linux/blob/master/net/ipv4/tcp_cong.c#L383)


**Congestion avoidance** apare în momentul în care apar pierderi, se crește fereastra cu o fracțiune de segment `cwnd += MSS*MSS/cwnd` pentru evitarea blocării rețelei. Tot la pasul acesta se setează un prag Slow Start Thresh `ssthresh = max(FlightSize / 2, 2*MSS)`, unde FlightSize e dat de numărul de octeți trimiși și neconfirmați. Acest prag va fi folosit pe viitor pentru a trece din mecanismul de slow start (când pragul este atins) în mecanismul de evitare a congestiei. Implementarea din TCP Reno [este aici](https://github.com/torvalds/linux/blob/master/net/ipv4/tcp_cong.c#L403).

**Fast retransmit** se bazează pe faptul că un receptor trimite un ack duplicat atunci când primește un segment cu sequence number mai mare decât cel așteptat. Astfel, îl notifică pe emițător că a primit un segment out-of-order. Dacă un emițător primește 3 ack duplicate, atunci acesta trimite pachetul cu sequence number pornind de la valoarea acelui acknowledgement fără a mai aștepta după timeout (fast retransmit).

Algoritmul de fast recovery pornește ulterior pentru a crește artificial cwnd. Acesta se bazează pe presupunerea că receptorul totuși recepționează o serie de pachete din moment ce trimite confirmări duplicate iar pachetele pe care le recepționează pot fi cu număr de secvență mai mare. De asemenea după 3 confirmări duplicate, ssthreshold se recalculează ca fiind jumate din cwnd iar congestion window se înjumătățește de asemenea (descreștere multiplicativă) și se trece la congestion avoidance. 


Toate se bazează pe specificațiile din [RFC 2581](https://tools.ietf.org/html/rfc2581), [RFC5681](https://tools.ietf.org/html/rfc5681) sau [RFC 6582](https://tools.ietf.org/html/rfc6582) din 2012.

În toate cazurile de mai sus, TCP se bazează pe pierderi de pachete (confirmări duplicate sau timeout) pentru identificarea congestionării. Există și un mecanism de notificare explicită a congestionării care a fost adăugat [relativ recent](http://www.icir.org/floyd/ecn.html) și care nu a fost încă adoptat de toate implementările de TCP. Pentru asta avem flag-urile NS, CWR, ECE dar mai este necesară și implementarea la [nivelul IP](https://en.wikipedia.org/wiki/Explicit_Congestion_Notification#Operation_of_ECN_with_IP) a unui câmp pe care să-l folosească routerele atunci când devin congestionate, iar pentru asta sunt folosiți primii doi biți din ToS. Flag-urile din TCP sunt:

- [ECE (ECN-Echo)](https://tools.ietf.org/html/rfc3168) este folosit de către receptor pentru a-l notifica pe emițător să reducă fluxul de date.
- CWR (Congestion window reduced) e folosit de către emițător pentru a confirma notificarea ECE primită către receptor și că `cwnd` a scăzut.
<!---
- [NS](https://tools.ietf.org/html/draft-ietf-tsvwg-tcp-nonce-04) o sumă de control pe un bit care se calculează în funcție de sumele anterioare și care încearcă să prevină modificarea accidentală sau intenționată a pachetelor în tranzit.
-->


<a name="tcp_options"></a> 
### Optiuni TCP
O [listă completă de opțiuni se găsește aici](http://www.networksorcery.com/enp/Protocol/tcp.htm#Options) si [aici](https://www.iana.org/assignments/tcp-parameters/tcp-parameters.xhtml). Optiunile au coduri, dimensiuni si specificatii particulare.
Probabil cele mai importante sunt prezentate pe scurt în [acest tutorial](http://www.firewall.cx/networking-topics/protocols/tcp/138-tcp-options.html): 
  - [Maximum Segment Size (MSS)](http://fivedots.coe.psu.ac.th/~kre/242-643/L08/html/mgp00005.html) opțiune obligatorie definită [aici](https://www.rfc-editor.org/rfc/rfc9293#name-maximum-segment-size-option) seteaza dimensiunea maxima a segmentului pentru a se evita fragmetarea la nivelul Network.
  - [Window Scaling](https://cloudshark.io/articles/tcp-window-scaling-examples/) definit [aici](https://tools.ietf.org/html/rfc7323#page-8) - campul Window poate fi scalat cu valoarea Window * 2^WindowScaleOption; opțiune permite redimensionarea ferestrei până la (2^16 - 1) * 2^14. În linux si docker puteți dezactiva window scaling prin [sysctls](https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt) `net.ipv4.tcp_window_scaling=0`. 
  - [Selective Acknowledgment](https://packetlife.net/blog/2010/jun/17/tcp-selective-acknowledgments-sack/) 
definit [aici](https://tools.ietf.org/html/rfc2018#page-3) permite trimiterea unor ack selective in functie de secventa pachetelor pierdute
  - [Timestamps](http://fivedots.coe.psu.ac.th/~kre/242-643/L08/html/mgp00011.html) (pentru round-trip-time) definite [aici](https://tools.ietf.org/html/rfc7323#page-12) inregistreaza timpul de primire a confirmarilor. In felul acesta se verifica daca reteaua este congestionata sau daca fluxul de trimitere trebuie redus.
  - [No-Operation](https://tools.ietf.org/html/rfc793#page-18) - no operation este folosit pentru separare între opțiuni sau pentru alinierea octetilor.
  - [End of Option List](https://tools.ietf.org/html/rfc793#page-18) - defineste capatul listei de optiuni
  - [Multipath TCP (MPTCP)](https://datatracker.ietf.org/doc/draft-ietf-mptcp-rfc6824bis/) - extensie a protocolului TCP care este inca abordata ca zona de cercetare pentru a permite mai multe path-uri de comunicare pentru o sesiune TCP. Explicat [aici](https://www.slashroot.in/what-tcp-multipath-and-how-does-multipath-tcp-work) sau in acest [film](https://www.youtube.com/watch?v=k-5pGlbiB3U).
  - [Alte opțiuni TCP](https://www.rfc-editor.org/rfc/rfc9293#name-other-common-options) experimentale sau des întâlnite. 
  - [Packet Mood?](https://www.ietf.org/rfc/rfc5841.txt)

<a name="tcp_retransmission"></a>
### Exercițiu TCP Retransmission
TCP este un protocol care oferă siguranța transmiterii pachetelor, în cazul în care un stream de octeți este trimis, se așteaptă o confirmare pentru acea secvență de bytes. Dacă confirmarea nu este primită se încearcă retransmiterea. Pentru a observa retransmisiile, putem introduce un delay artificial sau putem ignora anumite pachete pe rețea. Folosim un tool linux numit [netem](https://www.cs.unm.edu/~crandall/netsfall13/TCtutorial.pdf), un tutorial este disponibil si [aici](https://www.excentis.com/blog/use-linux-traffic-control-impairment-node-test-environment-part-2).

Exemple netem:
```bash
# tc qdisc add/change/show/del
# introduce between 5% and 25% loss on eht0 interface
tc qdisc add dev eth0 root netem loss 5% 25%
# package corruption 5% probability on eth1 interface
tc qdisc add dev eth1 root netem corrupt 5%
# reorder packages on eth0 interface
tc qdisc add dev eth0 root netem reorder 25% 50%
# at a 10ms delay on eth1 interface
tc qdisc add dev eth1 root netem delay 10ms
# clean everything
tc qdisc del dev eth0 root

# to add multiple constraits, make a single command
tc qdisc add dev eth0 root netem loss 5% 25% corrupt 5% reorder 25% 50% delay 10ms
```

În containerul router, în [docker compose.yml](https://github.com/senisioi/computer-networks/blob/2023/capitolul3/docker compose.yml) exista o `command` care inițializează containerul router și care rulează `sleep infinity`. 
`router.sh` este copiat în directorul root `/` in container prin comanda `COPY src/*.sh /` din Dockerfile-lab3, deci modificarea lui locală nu afectează fișierul din container.

Introduceți în elocal un shell script `alter_packages.sh` care să execute comenzi de netem pe interfețele eth0 și eth1. Rulați-l în cadrul command după inițializarea routerului, dar înainte de sleep infinity.

Porniți TCP Server și TCP Client în containerul server, respectiv client și executați schimburi de mesaje. Cu `tcpdump -Sntv -i any tcp` sau cu Wireshark observați comportamentul protocolului TCP. Încercați diferite valori în netem.


<a name="tcp_cong_ex"></a>
### A) Exercițiu TCP Congestion Control
Pentru a observa fast retransmit, puteți executa în contanerul server `/elocal/capitolul3/src/examples/tcp_losses/receiver.py` și în containerul client `/elocal/capitolul3/src/examples/tcp_losses/sender.py`. Captați cu wireshark sau cu `tcpdump -Sntv` pachetele de pe containerul router, veți putea observa schimburile de mesaje. 
Pentru a observa fast retransmit, setați pe interfața eth1 din containerul router o regulă de reorder și loss `tc qdisc add dev eth1 root netem reorder 80% delay 100ms`

În docker compose.yml este setată opțiunea de a folosi TCP Reno din sysctls, care folosește exact acest [fișier de linux](https://github.com/torvalds/linux/blob/master/net/ipv4/tcp_cong.c)
```
        sysctls:
          - net.ipv4.tcp_congestion_control=reno
```
Adăugați în sysctls următoarea linie care adaugă capabilitatea de Explicit Congestion Notification.
```
          - net.ipv4.tcp_ecn=1 
```
Ce observați diferit la 3-way handshake?

<a name="tcp_cong_plots"></a>
### B) Plot Congestion Graphs
Exercițiul se bazează pe [tutorialul prezentat de Fraida Fund](https://witestlab.poly.edu/blog/tcp-congestion-control-basics/) în care sunt extragese informațiile despre cwnd folosind aplicația din linia de comandă ss (socket statistics): `ss -ein dst IP`. Citiți cu atenție tutorialul înainte de a începe rezolvarea și asigurați-vă că aveți aplicațiile `ss` și `ts` în containerul de docker (rulați `docker compose build` în directorul capitolul3).

Setați pe containerul router limitare de bandă cu netem, astfel încât să aveți un bottleneck de 1 Mbp/s și un buffer de 0.1 MB, în ambele direcții de comunicare:
```bash
docker compose exec router bash -c "/elocal/capitolul3/src/bottleneck.sh"
```

Rulați pe containerul server o aplicație server iperf3
```bash
docker compose exec server bash -c "iperf3 -s -1"
```

Rulați pe containerul client script-ul de shell care salvează valorile de timestamp și cwnd într-un csv.
```bash
docker compose exec client bash -c "/elocal/capitolul3/src/capture_stats.sh"
```

Rulați pe containerul client o aplicație client care să comunice cu serverul timp de 60 de secunde și care să folosească TCP Reno:
```bash
docker compose exec client bash -c "iperf3 -c 198.10.0.2 -t 60 -C reno"
```
După finalizarea transmisiunii, încetați execuția comenzii `capture_stats.sh` prin `Ctrl + C`.


La final veți putea vedea în directorul `capitolul3/congestion` un fișier `socket_stats.csv` care conține timestamp-ul și cwnd la fiecare transmisie. 

#### B1. Plot cwnd
Scrieți un script care citește fișierul csv și plotează (vezi matplotlib, seaborn sau pandas) cwnd în raport cu timestamp. Identificați fazele Slow Start, Congestion Avoidance, Fast Retransmit și Fast Recovery. 

#### B2. Plot cwnd pentru alte metode de control
Încercați și alte metode de congestion control schimbând `-C reno` în [vegas](https://en.wikipedia.org/wiki/TCP_Vegas), [BBR](https://en.wikipedia.org/wiki/TCP_congestion_control#TCP_BBR), [CUBIC](https://www.cs.princeton.edu/courses/archive/fall16/cos561/papers/Cubic08.pdf).


### C) Explicit Congestion Notification

Folosind netfilterque, pentru toate pachetele, introduceți în layer-ul de IP informația că rețeaua este congestionată și urmăriți pachetele dintre `receiver.py` și `sender.py`.
În [Capitolul 6](../capitolul6#scapy_nfqueue_basic) aveți un exemplu cu NFQUEUE care interceptează pachete și le modifică în tranzit. Încercați să setați flag-urile de explicit congestion notification pe fiecare pachet de la nivelul IP.


<a name="#tcp_socket"></a> 
### Socket TCP
În capitolul2 există exemple de [server](https://github.com/senisioi/computer-networks/blob/2023/capitolul2/src/tcp_server.py) și [client](https://github.com/senisioi/computer-networks/blob/2023/capitolul2/src/tcp_client.py) pentru protocolul TCP. Cele mai importante metode sunt:
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
Un exemplu de 3-way handshake facut cu Raw Socket este în directorul [capitolul3/src/examples/raw_socket_handshake.py](https://github.com/senisioi/computer-networks/blob/2023/capitolul3/src/examples/raw_socket_handshake.py)
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
Un exemplu de handshake se afla în `src/examples/tcp_handshake.py` din cadrul acestui capitol.
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

<a name="exercitii"></a> 
## Exerciții
1. Instanțiați un server UDP și faceți schimb de mesaje cu un client scapy.  (Este necesara schimbarea socket-ului de L3 pentru aplicatii locale ```python conf.L3socket=L3RawSocket```)
2. Rulați 3-way handshake între server și client folosind containerele definite în capitolul3, astfel: containerul `server` va rula `capitolul2/tcp_server.py` pe adresa '0.0.0.0', iar în containerul `client` configurați și rulați fișierul din [capitolul3/src/examples/tcp_handshake.py](https://github.com/senisioi/computer-networks/blob/2023/capitolul3/src/examples/tcp_handshake.py) pentru a face 3-way handshake.
3. Configurați opțiunea pentru Maximum Segment Size (MSS) astfel încat să îl notificați pe server că segmentul maxim este de 1 byte. Puteți să-l configurați cu 0?
4. Trimiteți mesaje TCP folosind flag-ul PSH și scapy.
5. Setați flag-urile ECN în IP și flag-ul ECE in TCP pentru a notifica serverul de congestionarea rețelei.
6. [TCP Syn Scanning](https://scapy.readthedocs.io/en/latest/usage.html#syn-scans) - folosiți scapy pentru a crea un pachet cu IP-ul destinație 193.226.51.6 (site-ul facultății) și un layer de TCP cu dport=(10, 500) pentru a afla care porturi sunt deschise comunicării cu TCP pe site-ul facultății.
7. Urmăriți mai multe exemple din scapy [aici](https://scapy.readthedocs.io/en/latest/usage.html#simple-one-liners)
