# TCP Server
import socket
import logging
import time

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 10000
adresa = 'localhost'
server_address = (adresa, port)
sock.bind(server_address)
logging.info("Serverul a pornit pe %s si portnul portul %d", adresa, port)
sock.listen(5)
while True:
    logging.info('Asteptam conexiui...')
    conexiune, address = sock.accept()
    logging.info("Handshake cu %s", address)
    time.sleep(15)
    data = conexiune.recv(1024)
    logging.info('Content primit: "%s"', data)
    conexiune.send(b"Server - OK")
    conexiune.close()
sock.close()
