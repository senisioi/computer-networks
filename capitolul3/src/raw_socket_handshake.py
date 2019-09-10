'''
Example code for 3-way handshake in tcp using raw socket
'''
import sys
import socket
import struct
 
def checksum(msg):
    suma = 0 
    # every two bytes
    for i in range(0, len(msg), 2):
        cuvant = ord(msg[i]) + (ord(msg[i+1]) << 8)
        suma = suma + cuvant
    # restul peste 16 se aduna cu numarul trimmed la 16 biti and-ul face un 111 de 16 biti iar in rest pune 0
    while (suma >> 16):
        suma = (suma >> 16) + (suma & 0xffff)
    # complementare si trim la 16 biti    
    return ~suma & 0xffff     
 
try:
    # raw socket to provide tcp and ip headers
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
except socket.error , msg:
    print ('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    
packet = ''

source_ip = '198.13.0.1'
dest_ip = '198.13.0.2' 

# IP HEADER
ip_ihl = 5
ip_ver = 4
ip_dscp = 38
ip_ecn = 3
ip_tos = 0
ip_tot_len = 0  # kernel will fill the correct total length
ip_id = 54321   # id
ip_frag_flag = 0
ip_frag_offset = 0
ip_ttl = 64
ip_proto = socket.IPPROTO_TCP
ip_check = 0    # kernel will fill the correct checksum
# aton converts string of bytes to network order
ip_saddr = socket.inet_aton(source_ip)
ip_daddr = socket.inet_aton(dest_ip)

ip_ihl_ver = (ip_ver << 4) + ip_ihl
ip_dscp_ecn = (ip_dscp << 2) + ip_ecn
ip_frag = (ip_frag_flag << 13) + ip_frag_offset

# the ! in the pack format string means network order
ip_header = struct.pack('!BBHHHBBH4s4s' , ip_ihl_ver, ip_dscp_ecn, ip_tot_len, ip_id, ip_frag, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
 
# tcp header fields
tcp_source = 55051   # source port
tcp_dest = 10000   # destination port
tcp_seq = 15
tcp_ack_seq = 0
tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes

#tcp flags
tcp_ns = 0
tcp_cwr = 0
tcp_ece = 0
tcp_urg = 0
tcp_ack = 0
tcp_psh = 0
tcp_rst = 0
tcp_syn = 1
tcp_fin = 0

tcp_window = socket.htons(5840)    #   maximum allowed window size
tcp_check = 0
tcp_urg_ptr = 0
 
tcp_res_ns = tcp_ns
tcp_offset_res = (tcp_doff << 4) + tcp_res_ns
tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5) + (tcp_ece << 6) + (tcp_cwr << 7)

# the ! in the pack format string means network order
tcp_header = struct.pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
 
user_data = ''
 
# pseudo header fields
source_address = socket.inet_aton(source_ip)
dest_address = socket.inet_aton(dest_ip)
placeholder = 0
protocol = socket.IPPROTO_TCP
tcp_length = len(tcp_header) + len(user_data)

psh = struct.pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length)
psh = psh + tcp_header + user_data
 
tcp_check = checksum(psh)
#print (tcp_checksum)
 
# make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
tcp_header = struct.pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + struct.pack('H' , tcp_check) + struct.pack('!H' , tcp_urg_ptr)
 
# final full packet - syn packets dont have any data
packet = ip_header + tcp_header + user_data
#print (packet)
 
#SYN
s.sendto(packet, (dest_ip, 0))

#SYN-ACK
packet = s.recvfrom(1500)
packet = packet[0]

######## DATA Unpacking #########"

ip_data = packet[0:20]
ip_header_data = struct.unpack('!BBHHHBBH4s4s', ip_data) 
ip_version = ip_header_data[0] >> 4

#Now to get the header lenght we use "and" operation to make the
#Ip versional bits equal to zero, in order to the the desired data
IHL = ip_header_data[0] & 0x0F

#Diferentiated services doesn't need any magic opperations,
#so we jus grab it from the tuple
diff_services = ip_header_data[1]

total_length = ip_header_data[2]
id_ = ip_header_data[3]

#The "Flags" and Fragment Offset are situated in a sinle
#element from the forth element of the tuple.
#Flag is 3 bits (Most significant), so we make "and" with 1110 0000 0000 0000(=0xE000)
#to leave 3 most significant bits and then shift them right 13 positions
flags = ip_header_data[4] & 0xE000 >> 13

#The next elements are easy to get
TTL      = ip_header_data[5]
protocol = ip_header_data[6]
recv_checksum = ip_header_data[7]
source   = ip_header_data[8]
destinat = ip_header_data[9]

s_addr = socket.inet_ntoa(source);
d_addr = socket.inet_ntoa(destinat);

print ('Version : ' + str(ip_version) + ' IP Header Length : ' + str(IHL) + ' TTL : ' + str(TTL) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr))


payload = packet[20:]
tcp_data = payload[:20]

print (len(tcp_data))
tcp_header = struct.unpack('!HHLLBBHHH', tcp_data)

source_port = tcp_header[0]
dest_port = tcp_header[1]
sequence = tcp_header[2]
acknowledgement = tcp_header[3]
doff_reserved = tcp_header[4]
tcph_length = doff_reserved >> 4

print ('Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Sequence Number : ' + str(sequence) + ' Acknowledgement : ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length))

#################### DATA pack again to prepare the final ACK  #########################

# tcp header fields
tcp_source = 55051   # source port
tcp_dest = 10000   # destination port
tcp_seq = 16
tcp_ack_seq = sequence+1
tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes

#tcp flags
tcp_ns = 0
tcp_cwr = 0
tcp_ece = 0
tcp_urg = 0
tcp_ack = 1
tcp_psh = 0
tcp_rst = 0
tcp_syn = 0
tcp_fin = 0

tcp_window = socket.htons(5840)    #   maximum allowed window size
tcp_check = 0
tcp_urg_ptr = 0
 
tcp_res_ns = tcp_ns
tcp_offset_res = (tcp_doff << 4) + tcp_res_ns
tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5) + (tcp_ece << 6) + (tcp_cwr << 7)

# the ! in the pack format string means network order
tcp_header = struct.pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
 
user_data = ''
 
# pseudo header fields
source_address = socket.inet_aton(source_ip)
dest_address = socket.inet_aton(dest_ip)
placeholder = 0
protocol = socket.IPPROTO_TCP
tcp_length = len(tcp_header) + len(user_data)

psh = struct.pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length)
psh = psh + tcp_header + user_data
 
tcp_check = checksum(psh)
 
# make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
tcp_header = struct.pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + struct.pack('H' , tcp_check) + struct.pack('!H' , tcp_urg_ptr)
 
# final full packet - syn packets dont have any data
packet = ip_header + tcp_header + user_data
#print (packet)
 
#Send the packet finally - the port specified has no effect
s.sendto(packet, (dest_ip, 0))