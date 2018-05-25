# Laborator 4 (extra)

### [DNS](https://en.wikipedia.org/wiki/Domain_Name_System#RFC_documents)
- server prin UDP, pe portul 53
- permite conversia din nume de domeniu în adresa ip

### [DHCP](http://www.ietf.org/rfc/rfc2131.txt) si [BOOTP](https://tools.ietf.org/html/rfc951)
- [bootstrap protocol](https://en.wikipedia.org/wiki/Bootstrap_Protocol) a fost înlocuit de [Dynamic Host Configuration Protocol](https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol#Operation) pentru asignarea de adrese IPv4 automat device-urilor care se conectează pe rețea
- pentru cerere de IP flow-ul include pașii pentru discover, offer, request și ack
- container de docker [aici](https://github.com/networkboot/docker-dhcpd)

### [HTTP folosind scapy](https://github.com/invernizzi/scapy-http)
- protocolul [HTTP](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods) se regăsește la nivelul aplicație
- puteți folosi scapy pentru a crea requesturi complete către servicii web

### [TLS/SSL folosind scapy](https://github.com/tintinweb/scapy-ssl_tls)
- pe scurt [how SSL works](https://www.youtube.com/watch?v=iQsKdtjwtYI)
- mai multe [aici](https://blog.talpor.com/2015/07/ssltls-certificates-beginners-tutorial/)
- util pentru testarea și manipularea pachetelor folosind SSL/TLS
- [aici](https://github.com/tintinweb/scapy-ssl_tls), un exemplu pentru [heartbleed](http://heartbleed.com/)

### [Quick UDP Internet Connections](https://en.wikipedia.org/wiki/QUIC#cite_note-LWN-1)
- un protocol reliable, capabil de control al congestionării, și codificare la nivelul transport
- documentația completă este prezentată [aici](https://docs.google.com/document/d/1RNHkx_VvKWyWg6Lr8SZ-saqsQx7rFV-ev2jRFUoVD34/edit)
-  [HTTP2 si QUIC video](https://www.youtube.com/watch?v=wCa5nylzJCo) și prezentare [vulnerabilitati](https://www.blackhat.com/docs/us-16/materials/us-16-Pearce-HTTP2-&-QUIC-Teaching-Good-Protocols-To-Do-Bad-Things.pdf) 
- [analiză comparativă vulnerabilități](https://www.ietf.org/proceedings/96/slides/slides-96-irtfopen-1.pdf)


