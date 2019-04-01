# Tema 2

## Informații temă
Puteți lucra în echipe de 2 persoane.

Deadline: **25 aprilie 2019**, tema trebuie prezentată în timpul laboratorului


## Cerință
În directorul cu tema2 aveti un fisier docker-compose.yml în care sunt definite două servicii: tm1 și tm2. Acestea folosesc o imagine care se construieste pe baza fisierului `docker/Dockerfile-tema2`. Pentru a construi imaginea și porni containerele, puteți să rulați `docker-compose up -d` cu un terminal aflat in folderul tema2 sau, in cazul în care aplicația docker-compose nu este instalată în $PATH, puteți să executați aplicația din directorul superior: `../docker-compose up -d`

În directorul `src` aveți un server, un client udp și un fișier `util.py` cu o funcție care face conversia unui pachet UDP în șiruri de octeți pentru calculul sumei de control. 

1. (2p) citiți despre metoda de calcul a sumei de control pentru UDP; metoda este descrisă in [RFC1071](https://tools.ietf.org/html/rfc1071) din 1988 sau puteți vedea un exemplu [aici](https://www.securitynik.com/2015/08/calculating-udp-checksum-with-taste-of.html)
2. (2p) completați secțiunile TODO din fișierul src/util.py 
3. (2p) implementați funcția `calculeaza_checksum` din fișierul serverului de UDP
4. (2p) verificați corectitudinea implementării prin rularea serverului pe containerul tm2, tot pe tm2 rulați `tcpdump -i any -vvv -nn ip and udp` iar pe tm1 rulați clientul udp
5. (1p) modificați clientul UDP în așa fel încât și acesta să calculeze și să afișeze sumele de control pentru pachetele primite
6. (1p) modificați `docker-compose.yml` și adăugați command pentru a rula: clientul pe tm1, serverul și tcpdump pe tm2. Ca sa rulați mai multe comenzi, puteți folosi expresia: bash -c "comanda1 & comanda2". Puteți folosi `docker-compose up -d && docker-compose logs` pentru a vedea output-ul containerelor.

#### Exemplu tcpdump bad checksum:
```
	172.20.0.3.48977 > 172.20.0.2.10000: [bad udp cksum 0x5847 -> 0xc14e!] UDP, length 0
```
Valoarea corectă este 0xc14e iar mesajul brut conține doar header, cu payload de length 0.
Eroarea de la tcpdump apare datorită faptului că suma este calculată de către NIC prin [checksum offloading](https://wiki.wireshark.org/CaptureSetup/Offloading).
Pentru punctul 4. din temă, trebuie să vă asigurați că valoarea calculată de voi este identică cu valoarea corectă afișată de tcpdump.


