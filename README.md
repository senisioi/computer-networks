# 2022-2023 Computer Networks [in progress]


<a href="https://teams.microsoft.com/l/team/19%3awA2tGLn96SH2G_cNGKwPe8orFahlzuCYOLqhL30Uvao1%40thread.tacv2/conversations?groupId=e5a51008-8327-4111-89e8-0a128bfbd7ea&tenantId=08a1a72f-fecd-4dae-8cec-471a2fb7c2f1">
<img src="https://upload.wikimedia.org/wikipedia/commons/c/c9/Microsoft_Office_Teams_%282018%E2%80%93present%29.svg" alt="drawing" width="25"/>
Canalul cursului pe Teams
</a>




## Things to Checkout
- [Programul Masteral în Procesarea Limbajului Natural](https://nlp.unibuc.ro/master)
- [DefCamp](https://def.camp/) the most important annual conference on Hacking & Information Security in Central Eastern Europe
- [Defcon](https://www.defcon.org/) hacker comunity conference

## Structura
Cel mai ok se vede accesând acest [URL](https://senisioi.github.io/computer-networks/)

### [Bibliografie curs](curs/)
### Capitolul 0
- [Introducere](capitolul0/)
- [Comenzi docker](capitolul0#docker)
- [NIC, ifconfig, iproute2](capitolul0#nic)
- [Exercițiu](capitolul0#exercitiu1)
- [Ping](capitolul0#ping)
- [tcpdump, wireshark](capitolul0#tcpdump_install)

### Capitolul 1
- [Introducere](capitolul1/)
- [Stivele de Rețea (OSI, TCP/IP)](capitolul1#stacks)
- [python concepte de bază](capitolul1#intro)
- [Big Endian (Network Order) vs. Little Endian](capitolul1#endianness)
- [Python Bytes as C Types](capitolul1#ctypes)
- [Funcția sniff în scapy](capitolul1#scapy_sniff)

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

### Capitolul 3
- [Introducere](capitolul3#intro)
- [Funcțiile send(p), sr(p), sr(p)1 în scapy](capitolul3#scapy_send)
- [UDP Datagram](capitolul3#udp)
  - [Exemplu de calcul pentru checksum](capitolul3#checksum)
  - [UDP Socket](capitolul3#udp_socket)
  - [UDP Raw Socket](capitolul3#udp_raw_socket)
  - [UDP Scapy](capitolul3#udp_scapy)
- [TCP Segment](capitolul3#tcp)
  - [TCP Congestion Control](capitolul3#tcp_cong)
  - [TCP Options](capitolul3#tcp_options)
  - [Exercițiu Retransmisii](capitolul3#tcp_retransmission)
  - [Exercițiu Controlul Congestionării](capitolul3#tcp_cong_ex)
  - [TCP Socket](capitolul3#tcp_socket)
  - [TCP Raw Socket](capitolul3#tcp_raw_socket)
  - [TCP Scapy](capitolul3#tcp_scapy)
  - [TCP Options in Scapy](capitolul3#tcp_options_scapy)
- [Exerciții](capitolul3#exercitii)

### [Capitolul4](capitolul4/)
### [Capitolul5](capitolul5/)





## Înainte de a începe cursul
Pentru curs, vom avea nevoie de:
- [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
- [docker compose](https://docs.docker.com/compose/install/linux/)
- după instalarea docker, trebuie să adăugați userul cu care lucrăm în grupul de docker `sudo usermod -aG docker $USER`

