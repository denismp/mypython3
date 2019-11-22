#!/bin/bash
set -x
for ((i=0;i<10;i++))
do
	echo $i
	python oxclient.py -n $i -d -s -l /tmp/$i.log &
done
exit 0
