#!/bin/bash
set -x
# add route to subnet 198.10.0.0/16 via IP 172.10.0.1
ip route add 172.10.0.0/16 via 198.10.0.1
# add 8.8.8.8 nameserver
echo "nameserver 8.8.8.8" >> /etc/resolv.conf

# we need to drop the kernel reset of hand-coded tcp connections
# https://stackoverflow.com/a/8578541
iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP

# and redirect incoming traffic
# https://my.esecuredata.com/index.php?/knowledgebase/article/49/how-to-redirect-an-incoming-connection-to-a-different-ip-address-on-a-specific-port-using-iptables/
iptables -t nat -A POSTROUTING -j MASQUERADE 
