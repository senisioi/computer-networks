## Laborator 1

### In Prealabil
Rulati comenzi de docker din README.md.

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

- *eht0* - placa de retea Ethernet virtuala care indica configuratia pentru stabilirea unei conexiuni de retea a containerului.
- *lo* - [local Loopback device](https://askubuntu.com/questions/247625/what-is-the-loopback-device-and-how-do-i-use-it) care defineste categoria de adrese care se mapeaza pe localhost.
- Ce este ether?
- Ce este inet?
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

### Ping
Este un tool de networking care se foloseste de [ICMP](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol) pentru a verifica daca un host este conectat la o retea prin IP.

```bash
ping localhost

ping 172.111.0.3

ping 127.0.0.1

ping 127.0.2.12

ping 198.13.13.1
```

1. Cand rulati ping, utilizati optiunea -R pentru a vedea si calea pe care o efectueaza pachetul.

2. Ce reprezinta adresa 127.0.2.12? De ce functioneaza ping catre aceasta?

3. Intr-un terminal nou, rulati comanda `docker network inspect computernetworks_dmz` pentru a vedea ce adrese au celelalte containere. Incercati sa trimiteti un ping catre adresele IP ale celorlalte containere.

4. Folositi `docker stop` pentru a opri un container, cum arata rezultatul comenzii `ping` catre adresa IP a containerului care tocmai a fost oprit?

5. Folositi optiunea `-c 10` pentru a trimite un numar fix de pachete.

6. Folositi optiunea `-s 1000` pentru a schimba dimensiunea pachetului ICMP

7. Reporniti toate containerele. Cum arata rezultatele pentru `ping -M do -s 30000 172.27.0.4` si pentru `ping -M do -s 30000 127.27.0.4`. Care este diferenta dintre cele doua? Care este rezultatul daca selectati dimensiunea 1500?

8. Optiunea `-f` este folosita pentru a face un flood de ping-uri.  Rulati un shell cu user root, apoi `ping -f 172.27.0.4`. Separat, intr-un alt terminal rulati `docker stats`. Ce observati?

