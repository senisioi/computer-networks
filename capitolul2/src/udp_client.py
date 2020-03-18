# UDP client
import socket
import logging
import sys

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

port = 10000
adresa = 'localhost'
server_address = (adresa, port)
mesaj = sys.argv[1]

try:
    logging.info('Trimitem mesajul "%s" catre %s', mesaj, adresa)
    sent = sock.sendto(mesaj.encode('utf-8'), server_address)

    logging.info('Asteptam un raspuns...')
    data, server = sock.recvfrom(4096)
    logging.info('Content primit: "%s"', data)

finally:
    logging.info('closing socket')
    sock.close()
