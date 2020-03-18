# TCP client
import socket
import logging
import time
import sys

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)

port = 10000
adresa = 'localhost'
server_address = (adresa, port)
mesaj = sys.argv[1]

try:
    logging.info('Handshake cu %s', str(server_address))
    sock.connect(server_address)
    time.sleep(3)
    sock.send(mesaj.encode('utf-8'))
    data = sock.recv(1024)
    logging.info('Content primit: "%s"', data)

finally:
    logging.info('closing socket')
    sock.close()
