# 2022-2023 Computer Networks [in progress]


<a href="https://teams.microsoft.com/l/team/19%3awA2tGLn96SH2G_cNGKwPe8orFahlzuCYOLqhL30Uvao1%40thread.tacv2/conversations?groupId=e5a51008-8327-4111-89e8-0a128bfbd7ea&tenantId=08a1a72f-fecd-4dae-8cec-471a2fb7c2f1">
<img src="https://upload.wikimedia.org/wikipedia/commons/c/c9/Microsoft_Office_Teams_%282018%E2%80%93present%29.svg" alt="drawing" width="25"/>
Canalul cursului pe Teams
</a>




## Things to Checkout
- [Materiale de Curs](https://senisioi.github.io/computer-networks/)
- [Programul Masteral în Procesarea Limbajului Natural](https://nlp.unibuc.ro/master)
- [DefCamp](https://def.camp/) the most important annual conference on Hacking & Information Security in Central Eastern Europe
- [Defcon](https://www.defcon.org/) hacker comunity conference


## Înainte de a începe cursul
Acesta este un curs practic pe parcursul căruia vom învăța despre Internet, ce protocoale există în rețele și cum putem scrie programe pentru a interacționa cu rețelele.

O mare parte din exemplele de cod pot fi executate direct pe calculatoarele voastre (pe host). 
O parte din exemple utilizează containere de docker pentru a reproductibilitate. Așadar, ca să puteți reproduce toate experimentele și demonstratoarele de la curs, veți avea de:
- [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
- [docker compose](https://docs.docker.com/compose/install/linux/)
- de preferat să fie instalate pe Linux sau MacOS


## Materiale
Acesta este un repository de git, site-ul generat poate fi accesat la acest [URL](https://senisioi.github.io/computer-networks/)


### [Bibliografie curs](curs/)

### Capitolul 0
- [Introducere](capitolul0/)
- [Comenzi docker](capitolul0#docker)
- [NIC, ifconfig, iproute2](capitolul0#nic)
- [Exercițiu](capitolul0#exercitiu1)
- [Ping](capitolul0#ping)
- [tcpdump, wireshark](capitolul0#tcpdump_install)
- [Suport Video - Chapter 1: Computer Networks and the Internet](https://gaia.cs.umass.edu/kurose_ross/videos/1/)

### Capitolul 1
- [Introducere](capitolul1/)
- [Stivele de Rețea (OSI, TCP/IP)](capitolul1#stacks)
- [python concepte de bază](capitolul1#intro)
- [Big Endian (Network Order) vs. Little Endian](capitolul1#endianness)
- [Python Bytes as C Types](capitolul1#ctypes)
- [Funcția sniff în scapy](capitolul1#scapy_sniff)
- [Suport Video - Chapter 1: Computer Networks and the Internet](https://gaia.cs.umass.edu/kurose_ross/videos/1/)

### Capitolul 2
- [Introducere](capitolul2#intro)
- [Domain Name System](capitolul2#dns)
- [HTTP/S Requests](capitolul2#https)
- [HTTP Server](capitolul2#https_server)
  - [Exercițiu HTTPS + DNS](capitolul2#https_dns)
- [UDP](capitolul2#udp)
  - [Exerciții socket UDP](capitolul2#exercitii_udp)
- [TCP](capitolul2#tcp)
  - [Exerciții socket TCP](capitolul2#exercitii_tcp)
- [TCP 3-way handshake](capitolul2#shake)
- [Suport Video - Chapter 2: The Application Layer](https://gaia.cs.umass.edu/kurose_ross/videos/2/)

### Capitolul 3
- [Introducere](capitolul3#intro)
- [Funcțiile send(p), sr(p), sr(p)1 în scapy](capitolul3#scapy_send)
- [UDP Datagram](capitolul3#udp)
  - [Exemplu de calcul pentru checksum](capitolul3#checksum)
  - [UDP Socket](capitolul3#udp_socket)
  - [UDP Scapy](capitolul3#udp_scapy)
- [TCP Segment](capitolul3#tcp)
  - [TCP Congestion Control](capitolul3#tcp_cong)
  - [TCP Options](capitolul3#tcp_options)
  - [Exercițiu Retransmisii](capitolul3#tcp_retransmission)
  - [Exercițiu Controlul Congestionării](capitolul3#tcp_cong_ex)
  - [TCP Socket](capitolul3#tcp_socket)
  - [TCP Raw Socket](capitolul3#tcp_raw_socket)
  - [TCP Scapy](capitolul3#tcp_scapy)
- [Exerciții](capitolul3#exercitii)
- [Suport Video - Chapter 3: The Transport Layer](https://gaia.cs.umass.edu/kurose_ross/videos/3/)

### Capitolul 4
- [Introducere](capitolul4#intro)
- [IPv4 Datagram](capitolul4#ipv4)
  - [IPv4 Raw Socket](capitolul4#ip_raw_socket)
  - [IPv4 Scapy](capitolul4#ip_scapy)
- [Subnetting, Routing](capitolul4#ipv4routing)
- [IPv6 Datagram](capitolul4#ipv6)
  - [IPv6 Socket](capitolul4#ipv6_socket)
  - [IPv6 Scapy](capitolul4#ipv6_scapy)
- [Internet Control Message Protocol (ICMP)](capitolul4#scapy_icmp)
- [Exerciții](capitolul4#exercitii)
- [Suport Video - Chapter 4: The Network Layer: the Data Plane](https://gaia.cs.umass.edu/kurose_ross/videos/4/)
- [Suport Video - Chapter 5: The Network Layer: the Control Plane](https://gaia.cs.umass.edu/kurose_ross/videos/5/)


### Capitolul 5
- [Introducere](capitolul5#intro)
- [Ethernet Frame](capitolul5#ether)
  - [Ethernet Scapy](capitolul5#ether_scapy)
- [Address Resolution Protocol](capitolul5#arp)
  - [ARP Scapy](capitolul5#arp_scapy)
- [Exerciții](capitolul5#exercitii)
- [Suport Video - Chapter 6: The Link Layer](https://gaia.cs.umass.edu/kurose_ross/videos/6/)


### Capitolul 6
- [Requrements](capitolul6#intro)
- [Interceptarea Pachetelor](capitolul6#scapy_nfqueue)
    - [Blocare Pachete](capitolul6#scapy_nfqueue_block)
- [DHCP și BOOTP](capitolul6#scapy)
- [Domain Name System (DNS)](capitolul6#scapy_dns)
    - [DNS Request](capitolul6#scapy_dns_request)
    - [Micro DNS Server](capitolul6#scapy_dns_server)
    - [DNS Spoofing](capitolul6#scapy_dns_spoofing)
    - [Suport Video - DNS](https://youtu.be/6lRcMh5Yphg)
- [Exerciții](#exercitii)

### Capitol extra 1
-  [Configurarea unui router virtual](capitolulX1)

### Capitol extra 2
- [IPSec, QUIC, MPTCP, HTTP, SSL peste scapy](capitolulX2)