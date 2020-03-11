# Capitolul 2

## Cuprins
- [Introducere și IDE](#intro)
- [python 3 basics](#basics)
  - [Exerciții python](#exercitii_python)
- [HTTP/S requests](#https)
  - [DNS over HTTPS](#doh)
  - [Exerciții HTTP](#exercitii_http)
- [Socket API](#socket)
- [UDP](#udp)
  - [Exerciții socket UDP](#exercitii_udp)
- [TCP](#tcp)
  - [Exerciții socket TCP](#exercitii_tcp)


<a name="intro"></a> 
## Introducere
În cadrul acestui capitol vom lucra cu [python](http://www.bestprogramminglanguagefor.me/why-learn-python), un limbaj de programare simplu pe care îl vom folosi pentru a crea și trimite pachete pe rețea. De asemenea, in cadrul acestui capitol folosim orchestratia de containere definită [aici](https://github.com/senisioi/computer-networks/blob/2020/capitolul2/docker-compose.yml). Pentru a rula această orchestrație, este suficient să:
```bash
cd computer-networks/
docker-compose down
yes | docker network prune

# pentru a suprascrie modificările locale
git fetch --all
git reset --hard origin/2020

cd capitolul2

# ../ este optional daca nu exista aplicatia docker-compose in $PATH
../docker-compose up -d
```

Pentru debug și autocomplete, este bine să avem un editor și [IDE pentru acest limbaj](https://wiki.python.org/moin/IntegratedDevelopmentEnvironments). În cadrul orelor vom lucra cu [wingide](http://wingware.com/downloads/wing-personal), dar pe calculatoarele voastre personale puteți lucra cu orice alt editor. 
Pentru a instala wingide făra permisiuni de administrator, putem rula:
```bash
wget https://gist.githubusercontent.com/senisioi/7d3d8a223f23d8bc9a21464dbe5f7e47/raw/e6657e66c441e2554fb8d3777783ca0eb6a2c985/install-wing.sh
bash install-wing.sh
```
[Scriptul](https://gist.github.com/senisioi/772b4b87b4fb52b96e6b83a22a4299b5) va instala editorul în directorul $HOME. 
Pentru a lansa wingide, putem să rulam în terminal:
```bash
wing-personal
```
Dacă aplicația nu există, puteți să o adăugați în path sau puteți încerca să o instalați din nou.

Pentru a face editorul să arate mai bine, rulați din linia de comandă:
```bash
cat <<EOF >> ~/.wingpersonal6/preferences
[user-preferences]
edit.show-line-numbers = 1
gui.qt-color-palette = u'one-dark'
gui.use-palette-throughout-ui = True
EOF
```

<a name="basics"></a> 
## [python 3 basics](https://www.tutorialspoint.com/python/python_variable_types.htm)
```python
# comment pentru hello world
variabila = 'hello "world"'
print (variabila)

# int:
x = 1 + 1

# str:
xs = str(x) + ' ' + variabila

# tuplu
tup = (x, xs)

# lista
l = [1, 2, 2, 3, 3, 4, x, xs, tup]
print (l[2:])

# set
s = set(l)
print (s)
print (s.intersection(set([4, 4, 4, 1])))

# dict:
d = {'grupa': 123, "nr_studenti": 10}
print (d['grupa'], d['nr_studenti'])
```

#### [for](https://www.tutorialspoint.com/python/python_for_loop.htm) și [while](https://www.tutorialspoint.com/python/python_while_loop.htm)
```python
lista = [1,5,7,8,2,5,2]
for element in lista:
    print (element)

for idx, element in enumerate(lista):
    print (idx, element)

for idx in range(0, len(lista)):
    print (lista[idx])

idx = 0
while idx < len(lista):
    print (lista[idx])
    idx += 1 
```

#### [if else](https://www.tutorialspoint.com/python/python_if_else.htm)
```python
'''
   comment pe
   mai multe
   linii
'''
x = 1
y = 2
print (x + y)
if (x == 1 and y == 2) or (x==2 and y == 1):
    print (" x e egal cu:", x, ' si y e egal cu: ', y)
elif x == y:
    print ('sunt la fel')
else:
    print ("nimic nu e adevarat")
```

#### [funcții](https://www.tutorialspoint.com/python/python_functions.htm)
```python
def functie(param = 'oooo'):
    '''dockblock sunt comments in care explicam
    la ce e buna functia
    '''
    return "whooh " + param + "!"

def verifica(a, b):
    ''' aceasta functie verifica
    o ipoteza interesanta
    '''
    if (x == 1 and y == 2) or (x==2 and y == 1):
        return 1
    elif x == y:
        return 0
    return -1
```

#### [module](https://www.tutorialspoint.com/python/python_modules.htm)
```python
import os
import sys
import logging
from os.path import exists
import time

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)
logging.info("Mesaj de informare")
logging.warn("Mesaj de warning")
logging.error("Mesaj de eroare")
try:
    1/0
except:
    logging.exception("Un mesaj de exceptie!")

program_name = sys.argv[0]
print (program_name)
print ("Exista '/elocal'?", exists('/elocal'))
print (os.path.join('usr', 'local', 'bin'))

for element in "hello world":
    sys.stdout.write(element)
    sys.stdout.flush()
    time.sleep(1)
```

#### [main](https://stackoverflow.com/questions/4041238/why-use-def-main)
```python
def main():
    print ("functia main")

# un if care verifică dacă scriptul este importat sau apelat ca main
if __name__ == '__main__':
    main()
 ```

#### [clase](https://www.tutorialspoint.com/python/python_classes_objects.htm)
```python
class Grupa:
    nume = 'grp'
    def __init__(self, nume, numar_studenti):
        self.nume = nume
        self.numar_student = numar_studenti
    def _metoda_protected(self):
        print ("da")
    def __metoda_privata(self):
        print ('nu')
    def metoda_publica(self):
        print ("yes")


g = Grupa('222', '21')
print (g.nume)
print (g.numar_studenti)
print (G.nume)
```

<a name="exercitii_python"></a>
### Exerciții python
1. Creați un script de python care printează toate literele unui text, câte o literă pe secunda, folosind `time.sleep(1)`.
2. Rulați scriptul anterior într-un container.
3. Folosind [command](https://docs.docker.com/compose/compose-file/compose-file-v2/#command), modificați docker-compose.yml pentru a lansa acel script ca proces al containerului.

<a name="https"></a>
## HTTP/S requests
Intrati in  browser si apasati tasta F12. Accesati pagina http://fmi.unibuc.ro/ro si urmariti in tabul Network
request-urile HTTP.
- Protocolul [HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [Metode HTTP](http://httpbin.org/#/HTTP_Methods)
- Protocolul [HTTPS](https://robertheaton.com/2014/03/27/how-does-https-actually-work/)
- Video despre HTTPS [aici](https://www.youtube.com/watch?v=T4Df5_cojAs)

```python
import requests
from bs4 import BeautifulSoup

# dictionar cu headerul HTTP sub forma de chei-valori
headers = {
    "Accept": "text/html",
    "Accept-Language": "en-US,en",
    "Cookie": "__utmc=177244722",
    "Host": "fmi.unibuc.ro",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"
}

response = requests.get('http://fmi.unibuc.ro/ro', headers=headers)
print (response.text[:200])

# proceseaza continutul html
supa = BeautifulSoup(response.text)

# cauta div cu class cst2
div = supa.find('div', {'class': 'cst2'})
paragraph = div.find('p')

print (paragraph.text)
```
<a name="doh"></a>
### [DNS over HTTPS](https://datatracker.ietf.org/doc/rfc8484/?include_text=1)
Pentru securitare și privacy, sunt dezvoltate metode noi care encriptează cererile către DNS.
DNS over HTTPS sau DoH este explicat in detaliu [aici](https://hacks.mozilla.org/2018/05/a-cartoon-intro-to-dns-over-https/). 
Privacy-ul oferit de DoH poate fi exploatat și de [malware](https://www.zdnet.com/article/first-ever-malware-strain-spotted-abusing-new-doh-dns-over-https-protocol/) iar mai multe detalii despre securitatea acestuia pot fi citite [aici](https://secure64.com/wp-content/uploads/2019/06/doh-dot-investigation-6.pdf).

<a name="exercitii_http"></a>
### Exerciții HTTP/S
1. Cloudflare are un serviciu DoH care ruleaza pe IP-ul [1.1.1.1](https://blog.cloudflare.com/announcing-1111/). Urmăriți [aici documentația](https://developers.cloudflare.com/1.1.1.1/dns-over-https/json-format/) pentru request-uri de tip GET către cloudflare-dns și scrieți o funcție care returnează adresa IP pentru un nume dat ca parametru. Indicații: setați header-ul cu {'accept': 'application/dns-json'}. 
2. Executati pe containerul `rt1` scriptul 'simple_flask.py' care deserveste API HTTP pentru GET si POST. Daca accesati in browser [http://localhost:8001](http://localhost:8001) ce observati?
3. Conectați-vă la containerul `docker-compose exec rt2 bash`. Testati conexiunea catre API-ul care ruleaza pe rt1 folosind curl: `curl -X POST http://rt1:8001/post  -d '{"value": 10}' -H 'Content-Type: application/json'`. Scrieti o metoda POST care ridică la pătrat un numărul definit în `value`. Apelați-o din cod folosind python requests.
4. Urmăriți alte exemple de request-uri pe [HTTPbin](http://httpbin.org/)


<a name="socket"></a> 
## Socket API
Este un [API](https://www.youtube.com/watch?v=s7wmiS2mSXY) disponibil în mai toate limbajele de programare cu care putem implementa comunicarea pe rețea la un nivel mai înalt. Semnificația flag-urilor este cel mai bine explicată în tutoriale de [unix sockets](https://www.tutorialspoint.com/unix_sockets/socket_core_functions.htm) care acoperă partea de C. În limbajul [python](https://docs.python.org/2/library/socket.html) avem la dispoziție exact aceleași funcții și flag-uri ca în C iar interpretarea lor nu ține de un limbaj de programare particular.

<a name="udp"></a> 
### User Datagram Protocol - [UDP](https://tools.ietf.org/html/rfc768)

Este un protocol simplu la [nivelul transport](https://www.youtube.com/watch?v=hi9BVTNvl4c&list=PLfgkuLYEOvGMWvHRgFAcjN_p3Nzbs1t1C&index=50). Header-ul acestuia include portul sursă, portul destinație, lungime și un checksum opțional:
```
  0      7 8     15 16    23 24    31
  +--------+--------+--------+--------+
  |     Source      |   Destination   |
  |      Port       |      Port       |
  +--------+--------+--------+--------+
  |                 |                 |
  |     Length      |    Checksum     |
  +--------+--------+--------+--------+
  |
  |          data octets ...
  +---------------- ...
```
Câteva caracteristi ale protocolului sunt descrise [aici](https://en.wikipedia.org/wiki/User_Datagram_Protocol#Attributes) iar partea de curs este acoperită în mare parte [aici](https://www.youtube.com/watch?v=Z1HggQJG0Fc&index=51&list=PLfgkuLYEOvGMWvHRgFAcjN_p3Nzbs1t1C).

Server-ul se instanțiază cu [AF_INET](https://stackoverflow.com/questions/1593946/what-is-af-inet-and-why-do-i-need-it) și SOCK_DGRAM (datagrams - connectionless, unreliable messages of a fixed maximum length) pentru UDP:

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port = 10000
adresa = 'localhost'
server_address = (adresa, port)
sock.bind(server_address)

data, address = sock.recvfrom(4096)

print(data, address)

sent = sock.sendto(data, address)

sock.close()
```

Clientul trebuie să știe la ce adresă ip și pe ce port să comunice cu serverul:
```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port = 10000
adresa = 'localhost'
server_address = (adresa, port)

sent = sock.sendto('mesaj'.encode('utf-8'), server_address)
data, server = sock.recvfrom(4096)

print(data, server)

sock.close()
```

O diagramă a procesului anterior este reprezentată aici:
![alt text](https://raw.githubusercontent.com/senisioi/computer-networks/2020/capitolul2/UDPsockets.jpg)


<a name="exercitii_udp"></a> 
### Exerciții
1. Pe container-ul rt1 rulați [udp_server.py](https://github.com/senisioi/computer-networks/blob/2020/capitolul2/src/udp_server.py), [udp_client.py](https://github.com/senisioi/computer-networks/blob/2020/capitolul2/src/udp_client.py). 
2. Încercați să folosiți udp_client.py pentru a vă conecta de pe sistemul host la container-ul rt1. Verificați documentația de la [ports](https://docs.docker.com/compose/compose-file/compose-file-v2/#ports)
3. Care este portul destinație pe care ăl folosește server-ul pentru a trimite un mesaj clientului?
4. Modificați mesajul client-ului ca acesta să fie citit ca parametru al scriptului (`sys.argv[1]`). Transmiteți mesaje de la un container la altul folosind *udp_server.py* și *udp_client.py*.
5. Utilizați `tcpdump -nvvX -i any udp port 10000` pentru a scana mesajele UDP care circulă pe portul 10000.


<a name="tcp"></a> 
### Transmission Control Protocol - [TCP](https://tools.ietf.org/html/rfc793#page-15)

Este un protocol mai avansat de la [nivelul transport](http://www.erg.abdn.ac.uk/users/gorry/course/inet-pages/transport.html). 
Header-ul acestuia este mai complex:
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


Câteva caracteristici ale protocolului sunt descrise [aici](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#TCP_segment_structure) iar partea de curs este acoperită în mare parte [aici](https://www.youtube.com/watch?v=c6gHTlzy-7Y&list=PLfgkuLYEOvGMWvHRgFAcjN_p3Nzbs1t1C&index=52).

Server-ul se instanțiază cu [AF_INET](https://stackoverflow.com/questions/1593946/what-is-af-inet-and-why-do-i-need-it) și SOCK_STREAM (fiindcă TCP operează la nivel de [byte streams](https://softwareengineering.stackexchange.com/questions/216597/what-is-a-byte-stream-actually))

```python
# TCP socket 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 10000
adresa = 'localhost'
server_address = (adresa, port)
sock.bind(server_address)

sock.listen(5)
while True:
   conexiune, addr = sock.accept()
   time.sleep(30)
   #conexiune.send("Hello from TCP!")
   conexiune.close()

sock.close()
```

Clientul trebuie să știe la ce adresă ip și pe ce port să comunice cu serverul:
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 10000
adresa = 'localhost'
server_address = (adresa, port)

sock.connect(server_address)
#data = sock.recv(1024)

sock.close()
```

O diagramă a procesului anterior este reprezentată aici:
![alt text](https://raw.githubusercontent.com/senisioi/computer-networks/2020/capitolul2/TCPsockets.png)


<a name="exercitii_tcp"></a> 
### Exerciții TCP
1. În containerul rt1 rulați `tcpdump -Snnt tcp` și tot în rt1 rulați un server tcp. Din container-ul rt2, creați o conexiune. Urmăriți [three-way handshake](https://www.geeksforgeeks.org/computer-network-tcp-3-way-handshake-process/) și închiderea conexiunii la nivel de pachete.
2. Pentru a observa retransmisiile, putem introduce un delay artificial sau putem ignora anumite pachete pe rețea. Pentru asta, folosim un tool linux numit [netem](https://wiki.linuxfoundation.org/networking/netem) sau mai pe scurt [aici](https://stackoverflow.com/questions/614795/simulate-delayed-and-dropped-packets-on-linux). Aplicați o regulă de ignorare a 1% din pachetele care circulă pe eth0 folosind: `tc qdisc add dev eth0 root netem loss 0.1%`. Rulați comanda `tc -s qdisc` pentru a vedea filtrul adăugat pe eth0. Puteți modifica filtrul prin `tc qdisc change dev eth0 root netem loss 75%` sau puteți să ștergeți regulile folosind: `tc qdisc del dev eth0 root netem`. Puteți rula *netem* pornind un nou bash shell cu user root pe rt1, păstrați deschise tcpdump și server-ul. Conectați client-ul și observați pachetele care circulă pe eth0.

<a name="shake"></a> 
### 3-way handshake
```
tcpdump -Snn tcp

SYN:
   IP 172.111.0.14.59004 > 198.13.0.14.10000: Flags [S], seq 2416620956, win 29200, options [mss 1460,sackOK,TS val 897614012 ecr 0,nop,wscale 7], length 0

SYN-ACK:
   IP 198.13.0.14.10000 > 172.111.0.14.59004: Flags [S.], seq 409643424, ack 2416620957, win 28960, options [mss 1460,sackOK,TS val 2714984427 ecr 897614012,nop,wscale 7], length 0

ACK:
   IP 172.111.0.14.59004 > 198.13.0.14.10000: Flags [.], ack 409643425, win 229, length 0

Trimite un octet cu PSH și intervalul de secventă de dimensiune 1:
   IP 172.111.0.14.59004 > 198.13.0.14.10000: Flags [P.], seq 2416620957:2416620958, ack 409643425, win 229, length 1

ACK cu sequence capătul intervalului care semnifică: am primit octeți pana la 2416620957, aștept de la 2416620958 înainte:
    IP 198.13.0.14.10000 > 172.111.0.14.59004: Flags [.], ack 2416620958, win 227, length 0
```
