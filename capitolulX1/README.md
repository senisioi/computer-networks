# Capitolul X1

## Configurarea unui router virtual

În acest capitol vom utiliza [vrnetlab](https://github.com/plajjan/vrnetlab), un framework pentru crearea de containere docker cu imagini de routere virtuale. Acest lucru ne permite să depășim configurațiile de rețele LAN cu care am lucrat până acum, să pornim un container care să funcționeze ca router, să putem configura device-ul și să înțelegem ce presupun acești pași.

Puteți urmări mai multe detalii despre vrnetlab și în acest film pe youtube: https://youtu.be/R_vCdGkGeSk?t=9m25s sau în acest [tutorial](https://www.brianlinkletter.com/vrnetlab-emulate-networks-using-kvm-and-docker/).

### Instalarea vrnetlab
Această unealtă se găsește ca submodul în reporitoy-ul de git (vezi fișierul gitmodules). Pentru a avea acces la cod, trebuie să rulați:
```bash
git submodule update --init --recursive
```

Posibil ca scripturile din repo să nu funcționeze fără BeautifulSoup și lxml, cel mai bine instalați-l pe host:
```bash
pip3 install beautifulsoup4 lxml
``` 

Vom folosi [openwrt](https://openwrt.org/) un firmare open source pentru embedded devices, în cazul nostru un router. Intrați în directorul corespunzător, downloadați imaginea openwrt și rulați comanda `make build`:

```bash
cd vrnetlab/openwrt
wget https://downloads.openwrt.org/releases/18.06.2/targets/x86/64/openwrt-18.06.2-x86-64-combined-ext4.img.gz
make build
cd ../..
```
Comanda execută un script în python care downloadează imaginile necesare și construiește imaginea pentru docker. În cazul în care comanda returnează erori, este posibil ca framework-ul BeautifulSoup să nu fie instalat, puteți să îl instalați cu `pip3 install bs4
`. 

În cele ce urmează trebuie să instalăm [vr-xcon](https://github.com/plajjan/vrnetlab/tree/master/vr-xcon) un program containerizat care permite crearea de legături bine definite între noduri și topologii de rețele.

```bash
# pull din docker registry https://hub.docker.com/
docker pull vrnetlab/vr-xcon

# retag images cu varianta simplificata
docker tag vrnetlab/vr-xcon:latest vr-xcon
docker tag vrnetlab/vr-openwrt:18.06.2 openwrt
```

### Pornirea și configurarea routerelor

În directorul vrnetlab se găsește un script care definește nișe funcții de shell ce pot fi utilizate pentru configurare ușoară. Pentru a acea acces în terminalul vostru la aceste comenzi, treubie să rulați:

```bash
cd vrnetlab
source vrnetlab.sh
```
Putem crea două routere OpenWRT cu următoarea topologie și să testăm conexiunea dintre ele folosind ping
![alt text](https://i1.wp.com/www.brianlinkletter.com/wp-content/uploads/2019/03/vrnetlab-002.png)

Putem porni routerele individual folosind `docker run` sau prin intermediul orchestratiei docker-compose.yml din capitolul4:
```bash
docker run -d --privileged --name openwrt1 openwrt
docker run -d --privileged --name openwrt2 openwrt
# sau
cd capitolul4
docker-compose up -d
```
Pentru a ne conecta la un router trebuie să folosim aplicația **telnet** pe portul 5000. Fie știm adresele IP ale containerelor din fisierul .yml sau le aflăm cu comanda: `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ID_CONTAINER` 


Conectarea la routerul openwrt1 se face prin telnet:
```bash
telnet 198.166.0.1 5000
# sau
vrcons capitolul4_openwrt1_1

Trying 198.166.0.1...
Connected to 198.166.0.1.
Escape character is '^]'.

Apasam Ctrl + ] si enter pentru a tasta comenzile urmatoare:
```

Conform documentației [openwrt](https://openwrt.org/docs/guide-user/base-system/basic-networking), configurația LAN se definește pe o interfață numită br-lan: `ifconfig br-lan`. Adresa IP a interfeței LAN este 10.0.0.15, dar configurația permanentă se definește prin:

```bash
uci show network.lan

# setam adresa IP pentru lan
uci set network.lan.ipaddr='10.0.0.15'

# configuram adresele IP pentru wan
uci show network.wan
uci set network.wan.proto='static'
uci set network.wan.ipaddr='10.10.10.1'
uci set network.wan.netmask='255.255.255.0'

# salvam modificarile retelei si dam restart
uci commit network
service network restart
```
Pentru a ieși din router tastăm `Ctrl+]` apoi `quit`.

Facem setări similare și pe routerul openwrt2:

```bash
telnet 198.166.0.2 5000

uci set network.lan.ipaddr='10.0.0.15'
uci set network.wan.proto='static'
uci set network.wan.ipaddr='10.10.10.2'
uci set network.wan.netmask='255.255.255.0'
uci commit network
service network restart
#  Ctrl+] apoi quit
```

### Conectarea routerelor
Comanda vrbridge este definită în scriptul vrnetlab/vrnetlab.sh și are ca rol pornirea unui container care prin vr-xcon care creează legăturile dintre cele două routere. Comanda are ca parametrii containerul1, interfața1, containerul2 și interfața 2:
```bash
vrbridge capitolul4_openwrt1_1 1 capitolul4_openwrt2_1 1
# echivalent cu:
docker run -d --privileged --name bridge-capitolul4_openwrt1_1-1-capitolul4_openwrt2_1-1 --net capitolul4_net --link capitolul4_openwrt1_1 --link capitolul4_openwrt2_1 vr-xcon --p2p capitolul4_openwrt1_1/1--capitolul4_openwrt2_1/1 --debug 
```

### Exercițiu - Testarea conexiunii 
Conectați-vă prin telnet la unul din routere și încercați să dați ping către celălalt router.
