#!/bin/bash

# 50% loos on eth0 and eth1
tc qdisc add dev eth0 root netem loss 50% && \
tc qdisc add dev eth1 root netem loss 50% && \
sleep infinity