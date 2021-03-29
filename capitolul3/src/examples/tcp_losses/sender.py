import os
import socket
import logging
import time
import sys

# TSO stands for TCP segmentation offload
# https://en.wikipedia.org/wiki/Large_send_offload

os.system("ethtool -K eth0 tso off")


logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

def get_pachete(n=1, MSS=1400):
    mesaj = ''
    for idx in range(0, n):
        mesaj += ''.join(MSS*[str(idx)])
    return mesaj.encode('utf-8')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
port = 10000
adresa = '198.10.0.2'
server_address = (adresa, port)
sock.connect(server_address)

sock.send(get_pachete(15))
'''
for i in range(0, 1000):
    sock.send(get_pachete(10, MSS=1500))
    time.sleep(1)
'''
#sock.close()


