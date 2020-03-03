# Capitolul 5


### [DHCP](http://www.ietf.org/rfc/rfc2131.txt) si [BOOTP](https://tools.ietf.org/html/rfc951)
- [bootstrap protocol](https://en.wikipedia.org/wiki/Bootstrap_Protocol) a fost înlocuit de [Dynamic Host Configuration Protocol](https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol#Operation) pentru asignarea de adrese IPv4 automat device-urilor care se conectează pe rețea
- pentru cerere de IP flow-ul include pașii pentru discover, offer, request și ack
- container de docker [aici](https://github.com/networkboot/docker-dhcpd)

### [Parctical routing attacks](https://microlab.red/2018/04/06/practical-routing-attacks-1-3-rip/)
- protocoale de rutare și câteva exemple de vulnerabilități ale acestora

### [IPSec](http://www.firewall.cx/networking-topics/protocols/870-ipsec-modes.html)
- criptare si securizarea datelor la nivelul IP
- puteti urmări [aici un exemplu](https://into.synaptics.ro/2019/scapy-examples-/-usage/) cu scapy

### [TLS/SSL folosind scapy](https://github.com/tintinweb/scapy-ssl_tls)
- [ce este TLS/SSL?](https://www.cloudflare.com/learning/ssl/what-happens-in-a-tls-handshake/)
- pe scurt [un video how SSL works](https://www.youtube.com/watch?v=iQsKdtjwtYI)
- [un tutorial aici](https://blog.talpor.com/2015/07/ssltls-certificates-beginners-tutorial/)
- util pentru testarea și manipularea pachetelor folosind SSL/TLS
- [aici](https://github.com/tintinweb/scapy-ssl_tls), un exemplu pentru [heartbleed](http://heartbleed.com/)
- un atac de hijacking sesiune TLS [prezentat aici](http://www.cs.virginia.edu/~dgg6b/book/ssl-tls-session-attacks.html)

### [Quick UDP Internet Connections](https://en.wikipedia.org/wiki/QUIC#cite_note-LWN-1)
- un protocol reliable, cu congestion control și criptare la nivelul transport
- documentația completă este prezentată [aici](https://docs.google.com/document/d/1RNHkx_VvKWyWg6Lr8SZ-saqsQx7rFV-ev2jRFUoVD34/edit)
-  [HTTP2 si QUIC video](https://www.youtube.com/watch?v=wCa5nylzJCo) și prezentare [vulnerabilitati](https://www.blackhat.com/docs/us-16/materials/us-16-Pearce-HTTP2-&-QUIC-Teaching-Good-Protocols-To-Do-Bad-Things.pdf) 
- [analiză comparativă vulnerabilități](https://www.ietf.org/proceedings/96/slides/slides-96-irtfopen-1.pdf)

### [HTTP layer folosind scapy](https://github.com/invernizzi/scapy-http)
- protocolul [HTTP](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods) se regăsește la nivelul aplicație
- puteți folosi scapy pentru a crea requesturi complete către servicii web
- [HTTP2](https://github.com/secdev/scapy/blob/master/doc/notebooks/HTTP_2_Tuto.ipynb) notebook with scapy
 

### [MultiPath TCP]
- [potential issues](https://www.youtube.com/watch?v=Ss2zmwzKG3k) and [presentation](https://www.blackhat.com/docs/us-14/materials/us-14-Pearce-Multipath-TCP-Breaking-Todays-Networks-With-Tomorrows-Protocols.pdf) 
- [scapy tools for MPTCP](https://github.com/Neohapsis/mptcp-abuse)
- [basics](http://www.diva-portal.org/smash/get/diva2:934158/FULLTEXT01.pdf)