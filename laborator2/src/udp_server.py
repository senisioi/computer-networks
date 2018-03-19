# UDP Server
import socket
import logging

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port = 10000
adresa = 'localhost'
server_address = (adresa, port)
sock.bind(server_address)
logging.info("Serverul a pornit pe %s si portnul portul %d", adresa, port)

while True:
    logging.info('Asteptam mesaje...')
    data, address = sock.recvfrom(4096)
    
    logging.info("Am primit %s octeti de la %s", len(data), address)
    logging.info('Content primit: "%s"', data)
    
    if data:
        sent = sock.sendto(data, address)
        logging.info('Am trimis %d octeti inapoi la %s', sent, address)