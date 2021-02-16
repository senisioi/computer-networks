# Capitolul 0 - Getting familiarized


## Introducere Docker
Un container (sau serviciu) docker poate fi pornit (în mod asemănător cu o mașină virtuală) cu o imagine cu un sistem de operare. Un container seamănă mai mult cu un **proces** decât cu o mașină virtuală. Acesta nu emulează componente hardware, ci execută apeluri sistem cu dependințele necesare rulării unei aplicații. 

### Building a docker image
Pentru a construi imaginea explicit, putem folosi [docker build](https://docs.docker.com/engine/reference/commandline/build/). Comanda build utilizează fișierul [./docker/Dockerfile]() care definește ce sistem de operare va fi utilizat de container, ce aplicații vor fi pre-instalate și ce useri vor exista pe containerele care rulează acea imagine.
```bash
docker build -t retele:latest -f ./docker/Dockerfile .

# tag-ul imaginii (nume:versiune)
-t retele:latest

# calea catre fisierul dockerfile
-f ./docker/Dockerfile 

# contextul in care se executa docker build
.
```
Contextul este directorul în care se execută construcția imaginii. În fișierul Dockerfile se poate specifica [copierea explicită](https://docs.docker.com/engine/reference/builder/) a unor fișiere / date din directorul local, iar contextul reprezintă directorul în funcție de care se pot specifica căi relative în dockerfile.


### Orchestrate containers with docker-compose
Comanda [docker-compose up -d](https://docs.docker.com/compose/reference/up/), va citi fișierul **docker-compose.yml** din path-ul de unde rulăm comanda și va lansa containere după cum sunt definite în fișier în secțiunea *services*: rt1, rt2, etc..
Containere care sunt configurate să ruleze o imagine dată (în cazul nostru *baseimage*, imaginea construită la pasul anterior) sunt conectate la o rețea (în cazul nostru rețeaua *dmz*) sau și au definite [un mount point](https://unix.stackexchange.com/questions/3192/what-is-meant-by-mounting-a-device-in-linux) local.
Comanda docker-compose pe linux nu se instalează default cu docker, ci trebuie [să o instalăm separat](https://docs.docker.com/compose/install/). În cazul nostru, comanda se găsește chiar în directorul computer-networks, în acest repository. 

Aplicația docker-compose [va descărca din registry](https://hub.docker.com/repository/docker/snisioi/retele) imaginea corespunzătoare pentru acest laborator. Imaginea se numește retele și are tag-ul 2021, cu versiunea pentru acest an.
```bash
cd capitolul0
# start services defined in docker-compose.yml
docker-compose up -d
```

## Basic commands
```bash
# list your images
docker image ls
# sau
docker images

# stop services
docker-compose down

# see the containers running
docker ps
docker-compose ps

# kill a container
docker kill $CONTAINER_ID

# see the containers not running
docker ps --filter "status=exited"

# remove the container
docker rm $CONTAINER_ID

# list available networks
docker network ls

# inspect network
docker network inspect $NETWORK_ID

# inspect container
docker inspect $CONTAINER_ID

# see container ip
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID

# attach to a container
docker exec -it $CONTAINER_ID bash

# attach using docker-compose
docker-compose exec rt1 bash

# attach as root to a container
docker-compose exec --user root rt1 bash
```

<a name="clean_all"></a> 
### Remove images and containers

Ștergeți toate containerele create și resetați modificările efectuate în branch-ul local de git.
```bash
# pentru a opri toate containerele
docker stop $(docker ps -a -q)
# pentru a șterge toate containerele
docker rm $(docker ps -a -q)
# pentru a șterge toate rețelele care nu au containere alocate
docker network prune
# pentru a șterge containere si imagini
docker system prune

# pentru a șterge toate imaginile de docker (!!!rulați doar dacă știți ce face)
docker rmi $(docker images -a -q)
```


### Docker References
- [docker concepts](https://docs.docker.com/engine/docker-overview/#docker-engine)
- [docker-compose](http://docker-k8s-lab.readthedocs.io/en/latest/docker/docker-compose.html)
- [Compose Networking](https://runnable.com/docker/docker-compose-networking)
- [Designing Scalable, Portable Docker Container Networks](https://success.docker.com/article/Docker_Reference_Architecture-_Designing_Scalable,_Portable_Docker_Container_Networks)
- [Docker Networking Cookbook](https://github.com/TechBookHunter/Free-Docker-Books/blob/2020/book/Docker%20Networking%20Cookbook.pdf)




## NIC - Network Interface Controller (Placa de rețea)
```bash
# executați un shell în containerul rt1
docker-compose exec rt1 bash

# listați configurațiile de rețea
ifconfig

### eth0 - Ethernet device to communicate with the outside  ###
# eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
#        inet 172.27.0.3  netmask 255.255.0.0  broadcast 0.0.0.0
#        ether 02:42:ac:1b:00:03  txqueuelen 0  (Ethernet)
# lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
#        inet 127.0.0.1  netmask 255.0.0.0
#        loop  txqueuelen 1000  (Local Loopback)
```

Comanda *ifconfig* ne indică două device-uri care rulează pe containerul *rt1*:

- [*eht0*](http://www.tldp.org/LDP/nag/node67.html#SECTION007720000) - placa de rețea Ethernet virtuală care indică configurația pentru stabilirea unei conexiuni de rețea a containerului.
- [*lo*](https://askubuntu.com/questions/247625/what-is-the-loopback-device-and-how-do-i-use-it) - local Loopback device definește categoria de adrese care se mapează pe localhost.
- Ce reprezintă [ether](https://en.wikipedia.org/wiki/MAC_address) si [inet](https://en.wikipedia.org/wiki/IPv4)?
- Ce este [netmask](https://www.computerhope.com/jargon/n/netmask.htm)?
- Netmask și Subnet cu [prefix notation](https://www.ripe.net/about-us/press-centre/IPv4CIDRChart_2015.pdf)?
- Maximum Transmission Unit [MTU](https://en.wikipedia.org/wiki/Maximum_transmission_unit) dimensiunea în bytes a pachetului maxim

<a name="exercițiu1"></a>
### Exercițiu
Modificați docker-compose.yml pentru a adaugă încă o rețea și încă 3 containere atașate la rețeaua respectivă. Modificați definiția container-ului rt1 pentru a face parte din ambele rețele. 
Exemplu de rețele:
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
Ce se intamplă dacă constrângeți subnet-ul definit pentru a nu putea permite mai mult de 4 ip-uri într-o rețea.

<a name="ping"></a>
### Ping
Este un tool de networking care se foloseste de [ICMP](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol) pentru a verifica dacă un host este conectat la o rețea prin IP.

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

1. Când rulați ping, utilizați opțiunea -R pentru a vedea și calea pe care o efectuează pachetul.

2. Ce reprezintă adresa 127.0.2.12? De ce funcționează ping către aceasta?

3. Într-un terminal nou, rulați comanda `docker network inspect computernetworks_dmz` pentru a vedea ce adrese au celelalte containere. Încercați să trimiteți un ping către adresele IP ale celorlalte containere.

4. Folosiți `docker stop` pentru a opri un container, cum arată rezultatul comenzii `ping` către adresa IP a containerului care tocmai a fost oprit?

4. Rețelele dmz și net au în comun containerul rt1. Un container din rețeaua dmz primește răspunsuri la ping de la containere din rețeaua net?

5. Folosiți opțiunea `-c 10` pentru a trimite un număr fix de pachete.

6. Folosiți opțiunea `-s 1000` pentru a schimba dimensiunea pachetului ICMP

7. Reporniți toate containerele. Cum arată rezultatele pentru `ping -M do -s 30000 172.111.0.4` și pentru `ping -M do -s 30000 172.111.0.4`. Care este diferenta dintre cele două? Care este rezultatul dacă selectați dimensiunea 1500?

8. Opțiunea `-f` este folosită pentru a face un flood de ping-uri.  Rulați un shell cu user root, apoi `ping -f 172.111.0.4`. Separat, într-un alt terminal rulați `docker stats`. Ce observați?

<a name="ping_block"></a>
De multe ori răspunsurile la ping [sunt dezactivate](https://superuser.com/questions/318870/why-do-companies-block-ping) pe servere. Pentru a dezactiva răspunsul la ping rulați userul root: `echo "1" > /proc/sys/net/ipv4/icmp_echo_ignore_all`. Într-un container de docker nu aveți dreptul să modificați acel fișier și veți primi o eroare. Putem, în schimb, modifica structura containerului din *docker-compose.yml* și-i putem adăuga pe lângă image, networks, volumes, tty, o opțiune de [sysctls](https://docs.docker.com/compose/compose-file/compose-file-v2/#sysctls):
```
    rt1:
        ..........
        sysctls:
          - net.ipv4.icmp_echo_ignore_all=1
```


<a name="tcpdump_install"></a>
###  tcpdump
Este un tool care vă permite monitorizarea traficului de pe containerul/mașina pe care vă aflați. Vom folosi *tcpdump* pentru a monitoriza traficul generat de comanda ping. Pentru a rula tcpdump, trebuie să ne atașam unui container cu user **root** apoi putem rula:

```bash
tcpdump
```
Dacă tcpdump nu există ca aplicație, va trebui să modificați fișierul *Dockerfile* pentru a adaugă comanda de instalare a acestei aplicații. Reconstruiți imaginea folosind comanda docker build, distrugeți și reconstruiți containerele folosind `docker-compose down` și `docker-compose up -d`. Din cauza unui [bug de docker](https://github.com/moby/moby/issues/14140) e posibil ca această comandă să nu funcționeze imediat după instalare, afisând eroarea:
```bash
tcpdump: error while loading shared libraries: libcrypto.so.1.0.0: cannot open shared object file: Permission denied
```
Pentru a remedia această eroare, trebuie să adăugați în Dockerfile:
```bash
# move tcpdump from the default location to /usr/local
RUN mv /usr/sbin/tcpdump /usr/local/bin
# add the new location to the PATH in case it's not there
ENV PATH="/usr/local/bin:${PATH}"
```
De asemenea, e posibil ca datorită unor schimbări recente în repository de kali linux, să fie necesară reconstruirea imaginii, altfel nu vor putea fi instalate pachetele necesare. Pentru această operație, trebuie să opriți toate containere, să ștergeți containerele create împreună cu rețelele create (vezi [primele 4 comenzi de la începutul fișierului](#clean_all)). În urma ștergerii imaginilor, trebuie să reconstruim imaginea *baseimage* folosind `docker build -t baseimage ./docker/`.

Dacă în urma rulării acestei comenzi nu apare nimic, înseamnă că în momentul acesta interfața dată pe containerul respectiv nu execută operații pe rețea. Pentru a vedea ce interfețe (device-uri) putem folosi pentru a capta pachete, putem rula:
```bash
tcpdump -D
```

<a name="tcpdump_exer"></a>
### Exerciții
1. În containerul rt1 rulați `tcpdump -n`. În containerul rt2 rulați `ping -c 1 rt1`. Ce trasături observați la pachetul ICMP? Ce observați dacă rulați `ping -c 1 -s 2000 rt1`?

2. Rulați aceleasi ping-uri dar acum monitorizați pachetele cu `tcpdump -nvtS`. Ce detalii observați în plus? Dar dacă adăugați opțiunea `tcpdump -nvtSXX`?

3. Pentru a vedea și header-ul de ethernet, adăugați opțiunea `-e` la tcpdump.

4. În rt1 monitorizați traficul cu `tcpdump -nevtSXX` Într-un alt terminal, rulați un shell tot pe containerul rt1 apoi dați `ping -c 1 yahoo.com`. Ce adrese MAC și IP sunt folosite pentru a trimite requestul ICMP? Câte pachete sunt captate în total?

5. În loc de ultimul ping, generați trafic la nivelul aplicație folosind `wget https://github.com/senisioi/computer-networks/`. Comparați continutul pachetului cu un request HTTP: `wget http://moodle.fmi.unibuc.ro`. Observați diferența dintre HTTP si HTTPS la nivel de pachete.

6. Puteți deduce din output-ul lui tcpdump care este adresa IP a site-ului github.com sau moodle.fmi.unibuc.ro? Ce reprezintă adresa MAC din cadrul acelor request-uri?

7. Captând pachete, ați putut observa requesturi la o adresă de tipul 239.255.255.255? Mai multe detalii [aici](https://en.wikipedia.org/wiki/IP_multicast).


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

Diferite opțiuni pentru tcpdump:
```bash
# -c pentru a capta un numar fix de pachete
tcpdump -c 20

# -w pentru a salva pachetele într-un fișier și -r pentru a citi fișierul
tcpdump -w pachete.pcap
tcpdump -r pachete.pcap

# pentru a afișa doar pachetele care vin sau pleacă cu adresa google.com
tcpdump host google.com

# folosiți -XX pentru a afișa și conținutul în HEX și ASCII
tcpdump -XX

# pentru un timestamp normal
tcpdump -t

# pentru a capta pachete circula verbose
tcpdump -vvv

# indică interfața pe care o folosim pentru a capta pachete, în cazul acesta eth0 
tcpdump -i

# afișarea headerului de ethernet
tcpdump -e

# afișarea valorilor numerice ale ip-urilo în loc de valorile date de nameserver
tcpdump -n

# numărul de secvență al pachetului 
tcpdump -S
```

 - Întrebare: este posibil să captați pachetele care circulă între google.com și rt2 folosind mașina rt1?
 - Pentru mai multe detalii puteteți urmări acest [tutorial](https://danielmiessler.com/study/tcpdump/) sau [alte exemple](https://www.rationallyparanoid.com/articles/tcpdump.html)
 - Pentru exemple de filtrare mai detaliate, puteți urmări si [acest tutorial](https://forum.ivorde.com/tcpdump-how-to-to-capture-only-icmp-ping-echo-requests-t15191.html)
 - Trucuri de [filtare avansată](https://www.wains.be/pub/networking/tcpdump_advanced_filters.txt)
