# Laborator 2

## Cuprins
- [Introducere si IDE](https://github.com/senisioi/computer-networks/blob/master/laborator2/README.md#intro)
- [python 2.7 basics](https://github.com/senisioi/computer-networks/blob/master/laborator2/README.md#basics)
- [Exercitii python](https://github.com/senisioi/computer-networks/blob/master/laborator2/README.md#exercitii_python)
- [Socket API](https://github.com/senisioi/computer-networks/blob/master/laborator2/README.md#socket)
- [UDP](https://github.com/senisioi/computer-networks/blob/master/laborator2/README.md#udp)
- [Exercitii socket UDP](https://github.com/senisioi/computer-networks/blob/master/laborator2/README.md#exercitii_udp)

<a name="intro"></a> 
## Introducere
In cadrul acestui capitol vom lucra cu [python](http://www.bestprogramminglanguagefor.me/why-learn-python), un limbaj de programare foarte simplu pe care il vom folosi pentru a crea si trimite pachete pe retea.

Pentru debug si autocomplete, este bine sa avem un editor si [IDE pentru acest limbaj](https://wiki.python.org/moin/IntegratedDevelopmentEnvironments). In cadrul orelor vom lucra cu [wingdie](http://wingware.com/downloads/wing-personal), dar pe calculatoarele voastre personale puteti lucra cu orice alt editor. 
Pentru a instala wingdie fara permisiuni de administrator, putem rula:
```bash
wget https://gist.githubusercontent.com/senisioi/772b4b87b4fb52b96e6b83a22a4299b5/raw/d131f650bdf75701915809a52672e4e13b0bb926/wingdie-install.sh
bash wingdie-install.sh
```
[Scriptul](https://gist.github.com/senisioi/772b4b87b4fb52b96e6b83a22a4299b5) va instala editorul in directorul $HOME.


<a name="basics"></a> 
## [python 2.7 basics](https://www.tutorialspoint.com/python/python_variable_types.htm)
```python
# comment pentru hello world
variabila = 'hello "world"'
print variabila

# int:
x = 1 + 1

# str:
xs = str(x) + ' ' + variabila

# tuplu
tup = (x, xs)

# lista
l = [1, 2, 2, 3, 3, 4, x, xs, tup]
print l[2:]

# set
s = set(l)
print s
print s.intersection(set([4, 4, 4, 1]))

# dict:
d = {'grupa': 123, "nr_studenti": 10}
print d['grupa'], d['nr_studenti']
```

#### [for](https://www.tutorialspoint.com/python/python_for_loop.htm) si [while](https://www.tutorialspoint.com/python/python_while_loop.htm)
```python
lista = [1,5,7,8,2,5,2]
for element in lista:
    print lista

for idx, element in lista:
    print idx, element

for idx in range(0, len(lista)):
    print lista[idx]

idx = 0
while idx < len(lista):
    print lista[idx]
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
print x + y
if (x == 1 and y == 2) or (x==2 and y == 1):
    print " x e egal cu:", x, ' si y e egal cu: ', y
elif x == y:
    print 'sunt la fel'
else:
    print "nimic nu e adevarat"
```

#### [functii](https://www.tutorialspoint.com/python/python_functions.htm)
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
time.sleep(5)
print program_name
print exists('/usr/local/lib')
print os.path.join('usr', 'local', 'bin')
```

#### [main](https://stackoverflow.com/questions/4041238/why-use-def-main)
```python
def main():
    print "functia main"

# un if care verifica daca scriptul este importat sau apelat ca main
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
        print "da"
    def __metoda_privata(self):
        print 'nu'
    def metoda_publica(self):
        print "yes"


g = Grupa('222', '21')
print g.nume
print g.numar_studenti
print G.nume
```

<a name="exercitii_python"></a> 
### Exercitii
1. Creati un script de python care printeaza toate literele unui text, cate o litera pe secunda, folosind `time.sleep(1)`.
2. Rulati scriptul anterior intr-un container.
3. Folosind [command](https://docs.docker.com/compose/compose-file/compose-file-v2/#command), modificati docker-compose.yml pentru a lansa acel script ca proces al containerului.

<a name="Socket API"></a> 
## Socket API
![alt text](https://raw.githubusercontent.com/senisioi/computer-networks/master/laborator2/sockets.png)

Este un [API](https://www.youtube.com/watch?v=s7wmiS2mSXY) disponibil in mai toate limbajele de programare cu care putem implementa comunicarea pe retea la un nivel mai inalt. Semnificatia flag-urilor este cel mai bine explicata in tutoriale de [unix sockets](https://www.tutorialspoint.com/unix_sockets/socket_core_functions.htm) care acopera partea de C. In limbajul [python](https://docs.python.org/2/library/socket.html) avem la dispozitie exact aceleasi functii si flag-uri ca in C iar interpretarea lor nu tine de un limbaj de programare particular.

<a name="udp"></a> 
### [UDP](https://tools.ietf.org/html/rfc768)

Este un protocol simplu la [nivelul transport](http://www.erg.abdn.ac.uk/users/gorry/course/inet-pages/transport.html). Header-ul acestuia include portul sursa, portul destinatie, lungime si un checksum optional:
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
Cateva caracteristi ale protocolului sunt descrise [aici](https://en.wikipedia.org/wiki/User_Datagram_Protocol#Attributes).

Server-ul se instantiaza cu [AF_INET](https://stackoverflow.com/questions/1593946/what-is-af-inet-and-why-do-i-need-it) si SOCK_DGRAM (datagrams - connectionless, unreliable messages of a fixed maximum length) pentru UDP:
```python
# UDP socket 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port = 10000
adresa = 'localhost'
server_address = (adresa, port)
sock.bind(server_address)

data, address = sock.recvfrom(4096)
sent = sock.sendto(data, address)

sock.close()
```

Clientul trebuie sa stie la ce adresa ip si pe ce port sa comunice cu serverul:
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port = 10000
adresa = 'localhost'
server_address = (adresa, port)

sent = sock.sendto(mesaj, server_address)
data, server = sock.recvfrom(4096)

sock.close()
```

<a name="exercitii_udp"></a> 
### Exercitii
1. Pe acelasi container de docker rulati [udp_server.py](https://github.com/senisioi/computer-networks/blob/master/laborator2/src/udp_server.py), [udp_client.py](https://github.com/senisioi/computer-networks/blob/master/laborator2/src/udp_client.py). 
2. Care este portul destinatie pe care il foloseste server-ul pentru a trimite un mesaj clientului?
3. Modificati mesajul client-ului ca acesta sa fie citit ca parametru al scriptului (`sys.argv[1]`). Transmiteti mesaje de la un container la altul folosind *udp_server.py* si *udp_client.py*.
4. Utilizati `tcpdump -nvvX -i any udp port 10000` pentru a scana mesajele UDP care circula pe portul 10000.
