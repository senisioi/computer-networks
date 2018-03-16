## Laborator 1

### In prealabil
Rulati comenzi de docker din https://github.com/senisioi/computer-networks.

Stergeti toate containerele create si resetati modificarile efectuate in branch-ul local de git.
```bash
# pentru a opri toate containerele
docker stop $(docker ps -a -q)
# pentru a sterge toate containerele
docker rm $(docker ps -a -q)
# pentru a sterge toate retelele care nu au containere alocate
yes | docker network prune

# pentru a sterge toate imaginile de docker (!!!rulati doar daca stiti ce face)
docker rmi $(docker images -a -q)

# pentru a suprascrie modificarile locale
git fetch --all
git reset --hard origin/master
```

### Comenzi de baza
```bash
# executati un shell in containerul rt1
docker-compose exec rt1 bash

# listati configuratiile de retea
ifconfig

### eth0 - Ethernet device to communicate with the outside  ###
# eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
#        inet 172.27.0.3  netmask 255.255.0.0  broadcast 0.0.0.0
#        ether 02:42:ac:1b:00:03  txqueuelen 0  (Ethernet)
# lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
#        inet 127.0.0.1  netmask 255.0.0.0
#        loop  txqueuelen 1000  (Local Loopback)
```

Comanda *ifconfig* ne indica doua device-uri care ruleaza pe containerul *rt1*:

- [*eht0*](http://www.tldp.org/LDP/nag/node67.html#SECTION007720000) - placa de retea Ethernet virtuala care indica configuratia pentru stabilirea unei conexiuni de retea a containerului.
- [*lo*](https://askubuntu.com/questions/247625/what-is-the-loopback-device-and-how-do-i-use-it) - local Loopback device defineste categoria de adrese care se mapeaza pe localhost.
- Ce reprezinta [ether](https://en.wikipedia.org/wiki/MAC_address) si [inet](https://en.wikipedia.org/wiki/IPv4)?
- Ce este [netmask](https://www.computerhope.com/jargon/n/netmask.htm)?
- Netmask si Subnet cu [prefix notation](https://www.ripe.net/about-us/press-centre/IPv4CIDRChart_2015.pdf)?
- Maximum Transmission Unit [MTU](https://en.wikipedia.org/wiki/Maximum_transmission_unit) dimensiunea in bytes a pachetului maxim

##### Exercitiu
Modificati docker-compose.yml pentru a adauga inca o retea si inca 3 containere atasate la reteaua respectiva. Modificati definitia container-ului rt1 pentru a face parte din ambele retele. 
Exemplu de retele:
```bash
networks:
    dmz:
        ipam:
            driver: default
            config:
                - subnet: 172.111.111.0/16 
                  gateway: 172.111.111.1
    net:
        ipam:
            driver: default
            config:
                - subnet: 198.13.13.0/16
                  gateway: 198.13.13.1
```
Ce se intampla daca constrangeti subnet-ul definit pentru a nu putea permite mai mult de 4 ip-uri intr-o retea.

### Ping
Este un tool de networking care se foloseste de [ICMP](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol) pentru a verifica daca un host este conectat la o retea prin IP.

```bash
# ping localhost and loopback
ping localhost

ping 127.0.0.1

ping 127.0.2.12

# ping neighbour from network dmz
ping 172.111.0.3

# ping neighbour from network net
ping 198.13.13.1
```

1. Cand rulati ping, utilizati optiunea -R pentru a vedea si calea pe care o efectueaza pachetul.

2. Ce reprezinta adresa 127.0.2.12? De ce functioneaza ping catre aceasta?

3. Intr-un terminal nou, rulati comanda `docker network inspect computernetworks_dmz` pentru a vedea ce adrese au celelalte containere. Incercati sa trimiteti un ping catre adresele IP ale celorlalte containere.

4. Folositi `docker stop` pentru a opri un container, cum arata rezultatul comenzii `ping` catre adresa IP a containerului care tocmai a fost oprit?

4. Retelele dmz si net au in comun containerul rt1. Un container din reteaua dmz primeste raspunsuri la ping de la containere din reteaua net?

5. Folositi optiunea `-c 10` pentru a trimite un numar fix de pachete.

6. Folositi optiunea `-s 1000` pentru a schimba dimensiunea pachetului ICMP

7. Reporniti toate containerele. Cum arata rezultatele pentru `ping -M do -s 30000 172.111.0.4` si pentru `ping -M do -s 30000 172.111.0.4`. Care este diferenta dintre cele doua? Care este rezultatul daca selectati dimensiunea 1500?

8. Optiunea `-f` este folosita pentru a face un flood de ping-uri.  Rulati un shell cu user root, apoi `ping -f 172.111.0.4`. Separat, intr-un alt terminal rulati `docker stats`. Ce observati?

9. De multe ori raspunsurile la ping [sunt dezactivate](https://superuser.com/questions/318870/why-do-companies-block-ping) pe servere. Pentru a dezactiva raspunsul la ping rulati userul root: `echo "1" > /proc/sys/net/ipv4/icmp_echo_ignore_all`. Intr-un container de docker nu aveti dreptul sa modificati acel fisier si veti primi o eroare. Putem, in schimb, modifica structura containerului din *docker-compose.yml* si-i putem adauga pe langa image, networks, volumes, tty, o optiune de [sysctls](https://docs.docker.com/compose/compose-file/compose-file-v2/#sysctls):
```
        sysctls:
          - net.ipv4.icmp_echo_ignore_all=1
```



### tcpdump
Este un tool care va permite monitorizarea traficului de pe containerul/masina pe care va aflati. Vom folosi *tcpdump* pentru a monitoriza traficul generat de comanda ping. Pentru a rula tcpdump, trebuie sa ne atasam unui container cu user **root** apoi putem rula:

```bash
tcpdump
```
Daca tcpdump nu exista ca aplicatie, va trebui sa modificati fisierul *Dockerfile* pentru a adauga comanda de instalare a acestei aplicatii. Reconstruiti imaginea folosind comanda docker build, distrugeti si reconstruiti containerele folosind `docker-compose down` si `docker-compose up -d`. Din cauza unui [bug de docker](https://github.com/moby/moby/issues/14140) e posibil ca aceasta comanda sa nu functioneze imediat dupa instalare, afisand eroarea:
```bash
tcpdump: error while loading shared libraries: libcrypto.so.1.0.0: cannot open shared object file: Permission denied
```
Pentru a remedia aceasta eroare, trebuie sa adaugati in Dockerfile:
```bash
# move tcpdump from the default location to /usr/local
RUN mv /usr/sbin/tcpdump /usr/local/bin
# add the new location to the PATH in case it's not there
ENV PATH="/usr/local/bin:${PATH}"
```
De asemenea, e posibil ca datorita unor schimbari recente in repository de kali linux, sa fie necesara reconstruirea imaginii, altfel nu vor putea fi instalate pachetele necesare. Pentru aceasta operatie, trebuie sa opriti toate containere, sa stergeti containerele create impreuna cu retelele create (vezi primele 4 comenzi de la inceputul fisierului). Apoi putem sterge toate imaginile folosind `docker rmi $(docker images -a -q)`. In urma stergerii imaginilor, trebuie sa reconstruim imaginea *baseimage* folosind `docker build -t baseimage ./docker/`.

Daca in urma rularii acestei comenzi nu apare nimic, inseamna ca in momentul acesta interfata data pe containerul respectiv nu executa operatii pe retea. Pentru a vedea ce interfete (device-uri) putem folosi pentru a capta pachete, putem rula:
```bash
tcpdump -D
```


##### Exercitii
1. In containerul rt1 rulati `tcpdump -n`. In containerul rt2 rulati `ping -c 1 rt1`. Ce trasaturi observati la pachetul ICMP? Ce observati daca rulati `ping -c 1 -s 2000 rt1`?

2. Rulati aceleasi ping-uri dar acum monitorizati pachetele cu `tcpdump -nvtS`. Ce detalii observati in plus? Dar daca adaugati optiunea `tcpdump -nvtSXX`?

3. Pentru a vedea si header-ul de ethernet, adaugati optiunea `-e` la tcpdump.

4. In rt1 monitorizati traficul cu `tcpdump -nevtSXX` Intr-un alt terminal, rulati un shell tot pe containerul rt1 apoi dati `ping -c 1 yahoo.com`. Ce adrese MAC si IP sunt folosite pentru a trimite requestul ICMP? Cate pachete sunt captate in total?

5. In loc de ultimul ping, generati trafic la nivelul aplicatie folosind `wget https://github.com/senisioi/computer-networks/`. Comparati continutul pachetului cu un request HTTP: `wget http://moodle.fmi.unibuc.ro`. Observati diferenta dintre HTTP si HTTPS la nivel de pachete.

6. Puteti deduce din output-ul lui tcpdump care este adresa IP a site-ului github.com sau moodle.fmi.unibuc.ro? Ce reprezinta adresa MAC din cadrul acelor request-uri?

7. Captand pachete, ati putut observa requesturi la o adresa de tipul 239.255.255.255? Mai multe detalii [aici](https://en.wikipedia.org/wiki/IP_multicast).


###### TCP/IP stack
```
                     ----------------------------
                     |    Application (HTTP+S)  |
                     |                          |
                     |...  \ | /  ..  \ | /  ...|
                     |     -----      -----     |
                     |     |TCP|      |UDP|     |
                     |     -----      -----     |
                     |         \      /         |
                     |         --------         |
                     |         |  IP  |         |
                     |  -----  -*------         |
                     |  |ARP|   |               |
                     |  -----   |               |
                     |      \   |               |
                     |      ------              |
                     |      |ENET|              |
                     |      ---@--              |
                     ----------|-----------------
                               |
         ----------------------o---------
             Ethernet Cable

                  Basic TCP/IP Network Node
```

Diferite optiuni pentru tcpdump:
```bash
# -c pentru a capta un numar fix de pachete
tcpdump -c 20

# -w pentru a salva pachetele intr-un fisier si -r pentru a citi fisierul
tcpdump -w pachete.pcap
tcpdump -r pachete.pcap

# pentru a afisa doar pachetele care vin sau pleaca cu adresa google.com
tcpdump host google.com

# folositi -XX pentru a afisa si continutul in HEX si ASCII
tcpdump -XX

# pentru un timestamp normal
tcpdump -t

# pentru a capta pachete circula verbose
tcpdump -vvv

# indica interfata pe care o folosim pentru a capta pachete, in cazul acesta eth0 
tcpdump -i

# afisarea headerului de ethernet
tcpdump -e

# afisarea valorilor numerice ale ip-urilo in loc de valorile date de nameserver
tcpdump -n

# numarul de secventa al pachetului 
tcpdump -S
```

 - Intrebare: este posibil sa captati pachetele care circula intre google.com si rt2 folosind masina rt1?
 - Pentru mai multe detalii puteti urmari acest [tutorial](https://danielmiessler.com/study/tcpdump/) sau [alte exemple](https://www.rationallyparanoid.com/articles/tcpdump.html)
 - Pentru exemple de filtrare mai detaliate, puteti urmari si [acest tutorial](https://forum.ivorde.com/tcpdump-how-to-to-capture-only-icmp-ping-echo-requests-t15191.html)

