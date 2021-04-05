#!/bin/bash
# script based on Fraida Fund's amazing blog post
# https://witestlab.poly.edu/blog/tcp-congestion-control-basics/


DST=${1:-198.10.0.2}
OUTPATH=${2:-/elocal/capitolul3/congestion}

mkdir -p ${OUTPATH}
OUTFILE_TXT=${OUTPATH}/socket_stats.txt
OUTFILE_CSV=${OUTPATH}/socket_stats.csv

touch ${OUTFILE_TXT}
rm -f ${OUTFILE_TXT}

cleanup ()
{
	# get timestamp
	ts=$(cat ${OUTFILE_TXT} |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "ESTAB"  |  grep "unacked" |  awk '{print $1}')

	# get sender
	sender=$(cat ${OUTFILE_TXT} |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "ESTAB"  | grep "unacked" | awk '{print $6}')


	# retransmissions - current, total
	retr=$(cat ${OUTFILE_TXT} |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "ESTAB"  |  grep -oP '\bunacked:.*\brcv_space'  | awk -F '[:/ ]' '{print $4","$5}' | tr -d ' ')


	# get cwnd, ssthresh
	cwn=$(cat ${OUTFILE_TXT} |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "ESTAB"    |  grep "unacked" | grep -oP '\bcwnd:.*(\s|$)\bbytes_acked' | awk -F '[: ]' '{print $2","$4}')

	# concatenate into one CSV
	echo "Timestamp,Sender,retr,retr.total,cwnd,ssthresh" > ${OUTFILE_CSV}
	paste -d ',' <(printf %s "$ts") <(printf %s "$sender") <(printf %s "$retr") <(printf %s "$cwn") >> ${OUTFILE_CSV}

	exit 0
}

trap cleanup SIGINT SIGTERM

while [ 1 ]; do 
	ss --no-header -ein dst $DST | ts '%.s' | tee -a ${OUTFILE_TXT} 
done
