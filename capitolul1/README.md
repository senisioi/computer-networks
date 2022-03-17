# Capitolul 1 - Programming Basics

## Cuprins
- [Network Stacks](#stacks)
- [Introducere și IDE](#intro)
  - [utils](#utils)
  - [python3 basics](#basics)
  - [Exerciții python](#exercitii_python)
- [Big Endian (Network Order) vs. Little Endian](#endianness)
- [Python Bytes as C Types](#ctypes)
- [Funcția sniff și în scapy](#scapy_sniff)


<a name="stacks"></a> 
## Network Stacks
Stiva OSI:
![OSI7](https://www.cloudflare.com/img/learning/ddos/what-is-a-ddos-attack/osi-model-7-layers.svg)

Stiva TCP IP:
![alt text](https://raw.githubusercontent.com/senisioi/computer-networks/2020/capitolul3/layers.jpg)


<a name="utils"></a>
## netcat
netcat este un utilitar de retea folosit pentru a trimite/citi mesaje pe conexiuni. Exemplul urmator este pentru a simula o comunicare de baza server / client.
Se instaleaza folosind `[sudo] apt-get install netcat`.

### Server
`nc -l 8081`

Aceasta comanda va deschide un socket pe portul 8081 si asculta pentru noi conexiuni.
Noul proces se poate vedea folosind comanda `lsof -i -P | grep LISTEN` avand un output asemanator cu acesta: 
```
nc      2527 ubuntu    3u  IPv4  69208      0t0  TCP *:8081 (LISTEN)
```
Ni se specifica numele executabilului, process ID-ul iar in final protocolul de la nivelul transport si port-ul pe care asculta.

### Client
`echo "salut" | nc 127.0.0.1 8080`
Clientul va trimite folosind un pipe "|" (o metoda de a redirectiona output-ul unui proces catre input-ul altui proces in linux) mesajul "salut" catre ip-ul de loopback pe portul pe care ruleaza si serverul. In terminalul in care ruleaza serverul vom observa ca acesta a primit mesajul.


## traceroute
Este un utilitar pentru a vizualiza drumul pe care un pachet il parcurge pentru a ajunge la destinatie si a descoperi eventualele intarzieri. 
Se foloseste dand ca input un domeniu
```
ubuntu@ubun2004:~$ traceroute www.google.ro
traceroute to www.google.ro (142.250.185.163), 30 hops max, 60 byte packets
 1  _gateway (192.168.13.2)  0.399 ms  0.366 ms  0.328 ms
 2  192.168.100.2 (192.168.100.2)  0.667 ms  0.644 ms  0.820 ms
 3  StamAcasa.rdsnet.ro (10.0.0.1)  2.802 ms  2.782 ms  2.749 ms
 4  TotulVaFiBine.rdsnet.ro (172.19.211.1)  4.249 ms  4.229 ms  4.217 ms
 5  10.220.153.20 (10.220.153.20)  19.676 ms * *
 6  72.14.216.212 (72.14.216.212)  19.615 ms  19.753 ms  17.989 ms
 7  * 74.125.242.227 (74.125.242.227)  17.081 ms 10.23.192.126 (10.23.192.126)  19.847 ms
 8  216.239.41.57 (216.239.41.57)  32.737 ms  32.715 ms 72.14.233.180 (72.14.233.180)  17.316 ms
 9  108.170.226.2 (108.170.226.2)  33.542 ms  33.990 ms  33.970 ms
10  108.170.251.193 (108.170.251.193)  36.129 ms * 108.170.236.247 (108.170.236.247)  31.870 ms
11  209.85.252.215 (209.85.252.215)  32.228 ms 142.250.210.197 (142.250.210.197)  33.306 ms 142.250.210.209 (142.250.210.209)  32.633 ms
12  108.170.252.65 (108.170.252.65)  34.098 ms fra16s51-in-f3.1e100.net (142.250.185.163)  31.214 ms 108.170.252.65 (108.170.252.65)  32.272 ms
```
Mesajele trec prin mai multe routere sau servere chiar daca totul se intampla foarte repede. Internetul este format dintr-o multime de retele interconectate intre ele prin routere care stiu sa ghideze pachetele dupa IP destinatie.

## Adresele IP

O adresa IP este compusa din 4 campuri a cate un byte de exemplu `192.168.5.1` avand reprezentarea binara `11000000.10101000.00000101.00000001`. Fiecare retea, fie ea publica sau privata, are o adresa de retea si o masca care desparte un IP intr-un prefix de retea si un sufix de host. Se noteaza `192.168.5.0/24` si inseamana ca primii 24 de biti din IP sunt fixi iar ceilalti poti fi folositi pentru a atribui IP-uri dispozitivelor din retea. Retaua aceasta are urmatorul range `192.168.5.1 - 192.168.5.255` 
Masca poate fi reprezentata si de forma unei adrese IP dupa urmatoarea regula: toti bitii fixi au valoarea 1, restul au valoarea 0. Masca de 24 ar avea reprezentarea binara `11111111.11111111.11111111.00000000` si in format human readable `255.255.255.0`.

### Exercitii
- Care este intervalul de IP-uri al adresei de retea `64.183.234.9/15`
- Cate IP-uri pot fi atribuite in reteaua `192.168.0.0/16`
- Care este ultimul IP din reteaua `164.88.24.37/29`

### Observatii
- Utlimul IP din orice retea este cel de broadcast
- IP-ul retelei nu poate fi atribuit

<a name="intro"></a> 
## Introducere și IDE
În cadrul acestui capitol vom lucra cu [python](http://www.bestprogramminglanguagefor.me/why-learn-python), un limbaj de programare simplu pe care îl vom folosi pentru a crea și trimite pachete pe rețea. Pentru debug și autocomplete, este bine să avem un editor și [IDE pentru acest limbaj](https://wiki.python.org/moin/IntegratedDevelopmentEnvironments). În cadrul orelor vom lucra cu [Visual Studio Code](https://code.visualstudio.com/), dar puteți lucra cu orice alt editor. 

<a name="basics"></a> 
### [python3 basics](https://www.tutorialspoint.com/python/python_variable_types.htm)
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
    if (a == 1 and b == 2) or (a==2 and b == 1):
        return 1
    elif a == b:
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
        self.numar_studenti = numar_studenti
    def _metoda_protected(self):
        print ("da")
    def __metoda_privata(self):
        print ('nu')
    def metoda_publica(self):
        print ("yes")


g = Grupa('222', '21')
print (g.nume)
print (g.numar_studenti)
print (Grupa.nume)
```

<a name="exercitii_python"></a>
### Exerciții python
1. Creați un script de python care printează toate literele unui text, câte o literă pe secunda, folosind `time.sleep(1)`.
2. Rulați scriptul anterior într-un container.
3. Folosind [command](https://docs.docker.com/compose/compose-file/compose-file-v2/#command), modificați docker-compose.yml din capitolul0 pentru a lansa acel script ca proces al containerului.



<a name="endianness"></a>
## [Big Endian (Network Order) vs. Little Endian](https://en.m.wikipedia.org/wiki/Endianness#Etymology)

Numarul 16 se scrie in binar: `10000 (2^4)`, deci numărăm biții de la dreapta la stânga. 
Dacă numărul ar fi stocat într-un tip de date pe 8 biți, s-ar scrie: `00010000`
Dacă ar fi reprezentat pe 16 biți, s-ar scrie: `00000000 00010000`, completând cu 0 pe pozițiile mai mari până obținem 16 biți.

În calculatoare există două tipuri de reprezentare a ordinii octeților în funcție de [adresele stocate ca octeți](https://en.wikipedia.org/wiki/Endianness#Overview):
- **Big Endian** este: 00000000 00010000
  - ordinea bitilor este intuitivă, crescând de la dreapta la stânga
  - **big bit** is at the **end** of the address space
  - cel mai **semnificativ bit** are adresa cea mai **mică**, adresa 0: 00010000, adresa 1: 00000000
- **Little Endian** este: 00010000 00000000
  - ordinea adreselor este intuitivă, crescând de la dreapta la stânga
  - **little bit** is at the **end** of the address space
  - cel mai **nesemnificativ bit** are adresa cea mai **mică**, adresa 0: 00000000, adresa 1: 00010000

Pe rețea mesajele transmise trebuie să fie reprezentate într-un mod standardizat, independent de reprezentarea octeților pe mașinile de pe care sunt trimise, și acest standard este dat de Big Endian sau **Network Order**.

Pentru a verifica ce endianness are calculatorul vostru puteti rula din python:
```python
import sys
print(sys.byteorder)
```


<a name="ctypes"></a> 
## Python Bytes as C Types
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


### Exemple

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


operator = '+'.encode('utf-8')
# encode 12+13 as byte string
# 32-bit network order integers and 1 byte-char operator
octeti = struct.pack('!IcI', 12, operator, 13)
print(octeti)
# b'\x00\x00\x00\x0c+\x00\x00\x00\r'
valori = struct.unpack('!IcI', octeti)
print(valori)
# (12, b'+', 13)

# Atentie!
# accesarea unui singur octet returneaza valoarea lui ca numar
print(octeti[4]) # 43 echivalent cu codul ascii pt '+'
# slicing returneaza stringul de bytes
print(octeti[4:5]) # b'+' echivalent cu codul ascii pt '+'
```


<a name="scapy_sniff"></a> 
## Funcția sniff în scapy
[scapy](https://github.com/secdev/scapy) este o librărie care acoperă o serie mare de funcționalități ce pot fi implementate programatic. Principalele features sunt cele de creare și manipulare a pachetelor, dar și aceea de a capta pachetele care circulă pe rețea. Pentru a scana pachetele care circulă, similar cu tcpdump, există funcția `sniff`. Pentru a instala librăria, folosim pipy:
```bash
pip install --pre scapy[complete]
```

Captarea pachetelor se face folosind **sniff**:
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


Funcția `sniff()` ne permite să captăm pachete în cod, la fel cum am face cu [wireshark](https://www.wireshark.org/) sau tcpdump. De asemenea putem salva captura de pachete în format .pcap cu tcpdump: 
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
# presupunem ca avem octetii corespunzatorui unui pachet UDP in python:
raw_socket_date = b'E\x00\x00!\xc2\xd2@\x00@\x11\xeb\xe1\xc6\n\x00\x01\xc6\n\x00\x02\x08\xae\t\x1a\x00\r\x8c6salut'

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

