#!/bin/bash

# we need to drop the kernel reset of hand-coded tcp connections
# https://stackoverflow.com/a/8578541
# and redirect incoming traffic
# https://my.esecuredata.com/index.php?/knowledgebase/article/49/how-to-redirect-an-incoming-connection-to-a-different-ip-address-on-a-specific-port-using-iptables/
iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP && \
iptables -t nat -A POSTROUTING -j MASQUERADE 