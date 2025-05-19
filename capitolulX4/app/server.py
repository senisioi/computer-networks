import socket

UDP_IP = "0.0.0.0"  # Asculta pe toate interfețele disponibile
UDP_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

print(f"Server UDP pornind pe {UDP_IP}:{UDP_PORT}...")

while True:
    data, addr = sock.recvfrom(1024) # Buffer size 1024 bytes
    print(f"Primit mesaj: {data.decode()} de la {addr}")