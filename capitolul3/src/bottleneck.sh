#!/bin/bash

# run this on container router

# remove previously added rules
# tc qdisc del dev eth0 root 
# tc qdisc del dev eth1 root  

# add hierarchical token bucket queue
# https://en.wikipedia.org/wiki/Token_bucket#Hierarchical_token_bucket
tc qdisc add dev eth0 root handle 1: htb default 3 
tc class add dev eth0 parent 1: classid 1:3 htb rate 1Mbit  
tc qdisc add dev eth0 parent 1:3 handle 3: bfifo limit 0.1MB

tc qdisc add dev eth1 root handle 1: htb default 3  
tc class add dev eth1 parent 1: classid 1:3 htb rate 1Mbit  
tc qdisc add dev eth1 parent 1:3 handle 3: bfifo limit 0.1MB