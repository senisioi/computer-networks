#!/bin/bash

# add route to subnet 198.10.0.0/16 via IP 172.10.0.1
ip route add 198.10.0.0/16 via 172.10.0.1 && \
# we need to drop the kernel reset of hand-coded tcp connections
# https://stackoverflow.com/a/8578541
iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP && \
sleep infinity