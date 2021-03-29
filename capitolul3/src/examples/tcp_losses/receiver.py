import os
import socket
import logging
import time

# TSO stands for TCP segmentation offload
# https://en.wikipedia.org/wiki/Large_send_offload
os.system("ethtool -K eth0 tso off")

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
port = 10000
adresa = '0.0.0.0'
server_address = (adresa, port)
sock.bind(server_address)
logging.info("Serverul a pornit pe %s si portnul portul %d", adresa, port)
sock.listen(1)
logging.info('Asteptam conexiui...')
conexiune, address = sock.accept()
logging.info("Handshake cu %s", address)
MSS = 1400
try:
    while True:
        data = conexiune.recv(MSS)
        logging.info('Content primit: "%s"', data)
        time.sleep(1)
finally:
    conexiune.close()
    sock.close()
