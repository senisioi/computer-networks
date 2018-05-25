# Tema 2

## Informații temă
Tema aceasta poate fi rezolvată în echipe de câte 4 studenți și tot codul trebuie livrat sub forma unui link/URL de git care va fi discutat la o oră de laborator. În plus, pentru această temă puteți obține o notă peste 10, dacă alegeți să rezolvați toate cele 4 cerințe. Secțiunea din **[tema anterioară](https://github.com/senisioi/computer-networks/tree/master/tema1#git)** conține toate informațiile de care aveți nevoie pentru a crea un repository și pentru a uploada primele fișiere pe git. Pentru a vă downloada local ultimele modificări făcute de alți colegi, va trebui să rulați [git pull](https://github.com/SouthGreenPlatform/tutorials/wiki/Git-Beginner's-Guide-for-Dummies#pull) in repository. Pentru a face modificări și a le publica, trebuie să rulați o secventă de comenzi: git add FISIER, git commit -m "MESAJ", git push origin master, mai multe detalii [aici](https://github.com/SouthGreenPlatform/tutorials/wiki/Git-Beginner's-Guide-for-Dummies#file-add). Dacă întâmpinați orice fel de probleme sau erori, vă rog să-mi scrieți pe mail.

**Deadline**: oricand pană în săptămâna (~~22-24 mai~~) **29 mai - 1 iunie**, la orele fiecărei grupe. Prezentarea cu întârziere la o altă grupă se penalizeaza cu 3 puncte.

## Cerințe temă (1 p. oficiu)
Pentru rezolvarea temei, utilizați docker-compose.yml și Dockerfile din laborator3.

#### 1. Transfer reliable de date prin UDP (3p.)
Implementați un protocol la nivelul aplicației pentru rt1 și rt3 respectând următoarele cerințe:
- pe rt3 rulați un server UDP
- pe rt1 rulați un client UDP (puteți utiliza scapy sau doar funcții de python)
- clientul trimite numere între 1 și 10000 pe rețea astfel încât numerele să ajungă în aceeași ordine pe server
- pentru jumate de punctaj puteți implementa [Stop and Wait](https://www.isi.edu/nsnam/DIRECTED_RESEARCH/DR_HYUNAH/D-Research/stop-n-wait.html)
- pentru punctajul integral, puteți implementa un algoritm cu fereastra glisantă/[sliding window](http://www.ccs-labs.org/teaching/rn/animations/gbn_sr/)

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
În felul acesta putem interoga device-urile din rețea pentru adresa MAC corespunzătoarea gateway-ului. Putem trimite și un broadcast întregului subnet dacă setăm `pdst` cu valoarea subnetului `net`. Din containerul `rt1`, folosiți funcția `answered, unanswered = srp(eth/arp)` pentru a înregistra toate perechile IP-MAC de pe rețea și afișați-le pe ecran pe câte o linie cu forma: `IP -- MAC`.

#### 3. Handcrafted TCP (3p.)
Modificați tcp_server.py din laborator 2 astfel încat serverul să accepte o singură conexiune și să primească constant date de la aceasta. Serverul face recv(1) la cate un byte, îl printează și trimite înapoi un mesaj de un byte (preferabil o literă). De asemenea, puteți șterge partea în care serverul dă time.sleep (linia 20).

Pentru simplitate, puteți folosi containerele rt1 și mid1 din rețeaua net. Rulați în containerul `rt1` serverul vostru modificat (`python /elocal/laborator2/src/tcp_server_modificat.py`) iar pe `mid1` faceți [3-way handshake](https://github.com/senisioi/computer-networks/blob/master/laborator3/src/tcp_handshake.py) cu serverul și setați opțiunea [Maximum Segment Size](https://www.incapsula.com/blog/mtu-mss-explained.html) `MSS = 2` (vezi exemplu în [laborator3](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#tcp_options)). 
După acest pas, setați în headerul de IP:
- flag-ul [ECN](https://www.youtube.com/watch?v=-atBciuG53o) pe `11` 
- [flag-ul DSCP](https://www.youtube.com/watch?v=rNV8rzWEOeY) pe [valoarea AF33](https://en.wikipedia.org/wiki/Differentiated_services#Commonly_used_DSCP_values) pentru [video streaming](https://tools.ietf.org/html/rfc4594#page-19)
- vezi exemplu în [laborator3](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#ip_scapy).

Iar în headerul de TCP:
- flag-urile [CWR si ECE](http://blog.catchpoint.com/2015/10/30/tcp-flags-cwr-ece/)
- vezi exemplu în [laborator3](https://github.com/senisioi/computer-networks/blob/master/laborator3/README.md#tcp_scapy).

Faceți trei transmisii a câte un byte (o litera) folosind funcția `sr1` și afișați răspunsul pentru fiecare, apoi încercați să transmiteți 3 bytes. În cele din urmă, resetați conexiunea trimițând un RST. 
Pentru testare, și prezentare la laborator, tot procesul de la handhsake pâna la reset trebuie înregistrat cu `tcpdump -Snnt tcp` pe ambele containere. Pentru jumătate din punctaj, puteți prezenta/explica doar log-urile de `tcpdump` de la alți colegi la care funcționează codul.

#### 4. ARP Spoofing (3p.)
[ARP spoofing](https://samsclass.info/124/proj11/P13xN-arpspoof.html) presupune trimiterea unui pachet ARP de tip reply către o țintă pentru a-l informa greșit cu privire la adresa MAC pereche pentru un IP. [Aici](https://medium.com/@ismailakkila/black-hat-python-arp-cache-poisoning-with-scapy-7cb1d8b9d242) și [aici](https://www.youtube.com/watch?v=hI9J_tnNDCc) puteți urmări cum se execută un atac de otrăvire a tabelei cache ARP stocată pe diferite mașini. Puteți astfel să folosiți containerul mid1 din aceeași rețea cu rt1, care are setat ip forwarding = 1 (ca rt2) și îl va notifica constant pe rt1 că adresa fizică a gateway-ului este adresa fizică a sa, iar pe gateway îl va notifica că adresa fizică a lui rt1, este adresa fizică a sa. Rulați acest proces constant, cu un time.sleep de câteva secunde pentru a nu face flood de pachete. La prezentarea temei, puteți rula tcpdump pe mașina mid1 iar pe rt1, puteți face un `wget http://moodle.fmi.unibuc.ro`. Dacă totul a funcționat, mid1, ar trebui să fie capabil să intercepteze pachetele cerute de rt1 cu wget.
