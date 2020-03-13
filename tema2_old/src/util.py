import struct
import socket
import logging
logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO)


def compara_endianness(numar):
    '''
    https://en.m.wikipedia.org/wiki/Endianness#Etymology
        numarul 16 se scrie in binar 10000 (2^4)
        pe 8 biti, adaugam 0 pe pozitiile mai mari: 00010000
        pe 16 biti, mai adauga un octet de 0 pe pozitiile mai mari: 00000000 00010000
        daca numaratoarea incepe de la dreapta la stanga:
            reprezentarea Big Endian (Network Order) este: 00000000 00010000
                - cel mai semnificativ bit are adresa cea mai mica
            reprezentarea Little Endian este: 00010000 00000000
                - cel mai semnificativ bit are adresa cea mai mare 
    '''
    print ("Numarul: ", numar)
    print ("Network Order (Big Endian): ", [bin(ord(byte)) for byte in struct.pack('!H', numar)])
    print ("Little Endian: ", [bin(ord(byte)) for byte in struct.pack('<H', numar)])



'''
Structura unui mesaj UDP brut pentru calcularea sumei de control:
  0                   1                   2                   3   
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |                       Source Address                          |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |                    Destination Address                        | IP pseudo-header
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
 |  placeholder  |    protocol   |        UDP length             |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |          Source Port          |       Destination Port        |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-   UDP header
 |          Length               |              0                |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |                       payload/data                            |  Transport data
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------

UDP length si Length sunt acelasi lucru de doua ori
'''


def construieste_mesaj_raw(ip_src, ip_dst, port_s, port_d, mesaj, protocol = socket.IPPROTO_UDP):
    '''
        1. porturi pe 16 biti
        pentru a converti porturile in numere pe 16 biti, trebuie sa folosim
        struct.pack care face conversii in tipuri de date din C
        https://docs.python.org/2/library/struct.html#format-characters
        '!' cere sa se faca conversia in network order (big endian)
        'H' reprezinta 'unsigned short' pe 16 biti
        -----------------------------------------
        apelati functia compara_endianness(10000) pentru a vedea exemple
    '''
    port_s_bytes = struct.pack('!H', port_s)
    port_d_bytes = struct.pack('!H', port_d)

    '''
        2. adrese IP in format binar
        inet_aton - https://linux.die.net/man/3/inet_aton
        face conversia din string IP ('127.0.0.1') in siruri de bytes
    '''
    ip_src_bytes = socket.inet_aton(ip_src)
    ip_dst_bytes = socket.inet_aton(ip_dst)
    
    logging.info("IP sursa string: %s ", ip_src)
    for idx, octet in enumerate(ip_src_bytes):
        logging.debug("IP sursa byteul %i - %d in binar: %s ", idx, ord(octet), bin(ord(octet)))

    logging.info("IP destinatie string: %s ", ip_src)
    for idx, octet in enumerate(ip_dst_bytes):
        logging.debug("IP sursa octetul %i - %d in binar: %s ", idx, ord(octet), bin(ord(octet)))

    '''
        3. codul protocoluli de transport pe 1 byte (unsigned char)
        https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers
    '''
    protocol_byte = struct.pack('!B', protocol)

    '''
        4. placeholder care nu contine nimic
    '''
    placeholder_byte = struct.pack('!B', 0)

    '''
        5. lenght = nr de bytes din header-ul UDP + nr de bytes din mesaj 
        TODO: completati campul length  
    '''
    length = ...
    length_bytes = struct.pack('!H', length)

    '''
        6. concatenam octetii pseudoheaderului de la protocolul IP
    '''
    ip_pseudo_header = ip_src_bytes + ip_dst_bytes + placeholder_byte + \
                    protocol_byte + length_bytes 

    '''
        7. concatenam octetii din headerul UDP cu checksum setat pe 0
    '''
    checksum_byte = struct.pack('!B', 0)
    udp_header = port_s_bytes + port_d_bytes + length_bytes + checksum_byte
    
    '''
        8. TODO: codificati un mesaj in format de bytes si adaugati-l in calculul 
        sumei de control
    '''

    mesaj_binar =  ip_pseudo_header + udp_header + checksum_byte # + mesaj_bytes

    return mesaj_binar



if __name__ == '__main__':
    compara_endianness(16)