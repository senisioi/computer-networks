# Tema 2

## Informatii tema
Tema aceasta poate fi rezolvata in echipe de cate 4 studenti si tot codul trebuie livrat sub forma unui link/URL de git care va fi discutat la o ora de laborator. In plus, pentru aceasta tema puteti obtine o nota peste 10, daca alegeti sa rezolvati toate cele 4 cerinte. Sectiunea din **[tema anterioara](https://github.com/senisioi/computer-networks/tree/master/tema1#git)** contine toate informatiile de care aveti nevoie pentru a crea un repository si pentru a uploada primele fisiere pe git. Pentru a va downloada local ultimele modificari facute de alti colegi, va trebui sa rulati [git pull](https://github.com/SouthGreenPlatform/tutorials/wiki/Git-Beginner's-Guide-for-Dummies#pull) in repository. Pentru a face modificari si a le publica, trebuie sa rulati o secventa de comenzi: git add FISIER, git commit -m "MESAJ", git push origin master, mai multe detalii [aici](https://github.com/SouthGreenPlatform/tutorials/wiki/Git-Beginner's-Guide-for-Dummies#file-add). Daca intampinati orice fel de probleme sau erori, va rog sa-mi scrieti pe mail.

**Deadline**: pentru fiecare grupa separat, la orele din saptamana **22-24 mai**. Prezentarea la o grupa din alta zi se penalizeaza cu un punct.

## Cerinte tema (1 p. oficiu)
Pentru rezolvarea temei, utilizati docker-compose.yml si Dockerfile din laborator3.

#### 1. Transfer reliable de date prin UDP (3p.)
Implementati un protocol la nivelul aplicatiei pentru rt1 si rt3 respectand urmatoarele cerinte:
- pe rt3 rulati un server UDP
- pe rt1 rulati un client UDP
- clientul trimite numere intre 1 si 10000 pe retea astfel incat numerele sa ajunga in aceeasi ordine pe server
- pentru jumate de punctaj puteti implementa [Stop and Wait](https://www.isi.edu/nsnam/DIRECTED_RESEARCH/DR_HYUNAH/D-Research/stop-n-wait.html)
- pentru punctajul integral, puteti implementa un algoritm cu fereastra glisanta

#### 2. [Address Resolution Protocol](http://www.erg.abdn.ac.uk/users/gorry/course/inet-pages/arp.html) (3p.)
[ARP](https://www.youtube.com/watch?v=QPi5Nvxaosw) este un protocol care face maparea intre protocolul de retea (IP-uri) si adresele hardware/fizice (adrese MAC) de pe o retea locala.
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
Pentru a afla adresa MAC corespunzatoare unui IP caruia vrem sa ii trimitem un pachte, putem sa facem un request de tip broadcast catre ff:ff:ff:ff:ff:ff cu operatia de request si IP-ul destinatie pentru care cautam adresa fizica:
```
eth = Ether(dst = "ff:ff:ff:ff:ff:ff")
arp = ARP(pdst = '198.13.13.1')
answered = srp1(eth / arp)
print answered[1].hwsrc
print answered[1].psrc
```
Toate device-urile din retea care primesc acest request, vor raspunde automat cu adresa lor MAC. Din containerul `rt1`, folositi functia `srp` si setati `pdst` cu valoarea subnetului `net`, pentru a inregistra toate raspunsurile si afisati pe ecran toate adresele MAC ale containerelor care se gasesc pe retea.

#### 3. Handcrafted TCP (3p.)
Modificati tcp_server.py din laborator 2 astfel incat serverul sa accepte o singura conexiune si sa primeasca constant date de la aceasta. Pentru fiecare pachet primit, il printeaza si trimite inapoi un mesaj de un byte (preferabil o litera). De asemenea, puteti sterge partea in care serverul da time.sleep (linia 20).

Pentru simplitate, puteti folosi containerele rt1 si mid1 din reteaua net. Rulati pe un container /elocal/laborator2/src/tcp_server.py iar pe un alt container faceti [3-way handshake](https://github.com/senisioi/computer-networks/blob/master/laborator3/src/tcp_handshake.py). Dupa acest pas, setati window=0, flag-ul [ECN](https://tools.ietf.org/html/rfc3168) in datagram-ul de IP si flagurile CWR si ECE in segmentul TCP. Faceti trei transmisii a cate un byte (o litera) folosind functia sr1, apoi setati window = 1. In cele din urma resetati conexiunea trimitand un RST. Pentru testare, si prezentare la laborator, tot procesul trebuie inregistrat cu `tcpdump -Snnt tcp` pe ambele containere.

#### 4. ARP Spoofing (3p.)
[ARP spoofing](https://samsclass.info/124/proj11/P13xN-arpspoof.html) presupune trimiterea unui pachet ARP de tip reply catre o tinta pentru a-l informa gresit cu privire la adresa MAC pereche pentru un IP. [Aici](https://medium.com/@ismailakkila/black-hat-python-arp-cache-poisoning-with-scapy-7cb1d8b9d242) puteti urmari cum se executa un atac de otravire a tabelei cache ARP stocata pe diferite masini. Puteti astfel sa folositi containerul mid1 din aceiasi retea cu rt1, care are setat ip forwarding = 1 (ca rt2) si il va notifica constant pe rt1 ca adresa fizica a gateway-ului este adresa fizica a sa, iar pe gateway il va notifica ca adresa fizica a lui rt1, este adresa fizica a sa. Rulati acest proces constant, cu un time.sleep de cateva secunde pentru a nu face flood de pachete. La prezentarea temei, puteti rula tcpdump pe masina mid1 iar pe rt1, puteti face un `wget http://moodle.fmi.unibuc.ro`. Daca totul a functionat, mid1, ar trebui sa fie capabil sa intercepteze pachetele cerute de rt1 cu wget.
