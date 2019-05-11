# Tema 3

## Informații temă
Tema aceasta poate fi rezolvată în echipe de maxim 3 studenți, fiecare trebuie să prezinte individual câte un punct.

**Deadline**: **28 - 29 mai**, la orele fiecărei grupe. 

## Cerințe temă (1 p. oficiu)
Pentru rezolvarea temei, utilizați containerele definite în docker-compose.yml din laborator3.

#### 1. Handcrafted TCP (3p.)
Modificați tcp_server.py din laborator 2 astfel încat serverul să accepte o singură conexiune pe care să o mențină deschisă și să afișeze constant tot ce primește. Serverul face recv(1) la cate un byte, îl printează și trimite înapoi litera 'Q'. Puteți șterge partea în care serverul execută time.sleep (linia 20).

Pentru simplitate, puteți folosi containerele server și middle din rețeaua net. Rulați în containerul `server` serverul vostru modificat.

- (1p) pe `middle` faceți [3-way handshake](https://github.com/senisioi/computer-networks/blob/master/laborator3/src/tcp_handshake.py) cu serverul, setați opțiunea [Maximum Segment Size](https://www.incapsula.com/blog/mtu-mss-explained.html) `MSS = 2` (vezi exemplu în [laborator3](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#tcp_options)). 
- (1p) faceți trei transmisii a câte un byte (o literă) folosind funcția `sr1` și afișați răspunsul pentru fiecare, apoi transmiteți 3 bytes
- (1p) în cele din urmă, inițializați finalizarea conexiunii FIN, FIN-ACK, ACK din codul scapy

Pentru testare, și prezentare la laborator, tot procesul de la handhsake pâna la finalizare trebuie înregistrat cu `tcpdump -Snnt tcp` pe ambele containere.


#### 2. [Address Resolution Protocol](http://www.erg.abdn.ac.uk/users/gorry/course/inet-pages/arp.html) (3p.)
[ARP](https://www.youtube.com/watch?v=QPi5Nvxaosw) este un protocol care face maparea între protocolul de rețea (IP-uri) și adresele hardware/fizice (adrese MAC) de pe o rețea locală.
```python
>>> ls(ARP)
hwtype     : XShortField                         = (1)                     # ce tip de adresă fizică, 1 pt MAC-uri
ptype      : XShortEnumField                     = (2048)                  # protocolul folosit, similar cu EthType 
hwlen      : ByteField                           = (6)                     # dimensiunea adresei MAC (6 octeti)
plen       : ByteField                           = (4)                     # dimensiunea adresei IP (pentru v4, 4 octeti)
op         : ShortEnumField                      = (1)                     # operațiunea 1 pentru request, 0 pentru reply   
hwsrc      : ARPSourceMACField                   = (None)                  # adresa MAC sursă
psrc       : SourceIPField                       = (None)                  # adresa IP sursă
hwdst      : MACField                            = ('00:00:00:00:00:00')   # adresa MAC destinație
pdst       : IPField                             = ('0.0.0.0')             # adresa IP destinație (poate fi și un subnet)
```
Pentru a afla adresa MAC corespunzătoare unui IP căruia vrem să îi trimitem un pachet, putem să facem un request de tip broadcast către ff:ff:ff:ff:ff:ff cu operația de request și IP-ul destinație pentru care căutam adresa fizică:
```
eth = Ether(dst = "ff:ff:ff:ff:ff:ff")
arp = ARP(pdst = '198.13.13.1')
answered = srp1(eth / arp)
print answered[1].hwsrc
print answered[1].psrc
```
În felul acesta putem interoga device-urile din rețea pentru adresa MAC corespunzătoarea gateway-ului. Putem trimite și un broadcast întregului subnet dacă setăm `pdst` cu valoarea subnetului `net`. 

**Cerință:** din containerul `server`, folosiți funcția `answered, unanswered = srp(eth/arp)` pentru a înregistra toate perechile IP-MAC de pe subnet și afișați-le pe ecran pe câte o linie cu forma: `IP -- MAC`.

#### 3. ARP Spoofing (3p.)
[ARP spoofing](https://samsclass.info/124/proj11/P13xN-arpspoof.html) presupune trimiterea unui pachet ARP de tip reply către o țintă pentru a-l informa greșit cu privire la adresa MAC pereche pentru un IP. [Aici](https://medium.com/@ismailakkila/black-hat-python-arp-cache-poisoning-with-scapy-7cb1d8b9d242) și [aici](https://www.youtube.com/watch?v=hI9J_tnNDCc) puteți urmări cum se execută un atac de otrăvire a tabelei cache ARP stocată pe diferite mașini. 

Puteți astfel să folosiți containerul `middle` din aceeași rețea cu `server`, care are setat ip forwarding = 1 (la fel ca containerul `router`) și care să execute un atac de otrăvire către router și server.

###### (1p) Construiți atacul
Scrieti un script care să trimită pachete `ARP` cu operația `reply` în loop cu time.sleep de 2 secunde:
1. către `server` să-l informeze că adresa fizică pentru `router` este adresa fizică a sa (adresa lui `middle`)
2. către `router` să-l informeze că adresa fizică pentru `server` este adresa fizică a sa
3. către `server` să-l informeze că adresa fizică a sa este una falsă (creați voi o adresă fizică fictivă)
3. către `router` să-l informeze că adresa fizică a sa este una falsă (creați voi o adresă fizică fictivă)

###### (1p) Rulați atacul pe middle și monitorizați pachetele dintre server și client
1. adăgați la command pentru containerul `middle` să execute operațiile de mai sus și să lanseze `tcpdump -SnntXX tcp`, puteți rula tcpdump in foreground folosind operatorul `&`
2. adăugați la command pentru containerul `server` să execute tcp_server.py din laborator2, modificat astfel încât să asculte pentru conexiuni din exterior
3. adăugați la command pentru containerul `client` să execute tcp_client.py din laborator2, modificat astfel încât să se conecteze la server și să trimită un mesaj

###### (1p) Prezentați rezultatul din logs
1. rulați totul folosind `docker-compose up -d` și prezentați output-ul din `docker-compose logs`

