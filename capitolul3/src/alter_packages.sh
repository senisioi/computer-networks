#!/bin/bash

# more here https://www.cs.unm.edu/~crandall/netsfall13/TCtutorial.pdf
# more here https://www.excentis.com/blog/use-linux-traffic-control-impairment-node-test-environment-part-2
# we can put that on eth1 too:
tc qdisc add dev eth0 root netem \ 
								delay 100ms 10ms 25% \
								loss 5% 25% \
								corrupt 10% \
								reorder 25% 50% && \
sleep infinity


# between 5% and 25% loss
#tc qdisc change dev eth0 root2 netem loss 5% 25%  && \
# package corruption 5% proba
#tc qdisc change dev eth2 root netem corrupt 5% && \
# reorder packages
#tc qdisc change dev eth2 root netem delay 10ms reorder 25% 50% && \

# clean everything
# tc qdisc del dev eth0 root