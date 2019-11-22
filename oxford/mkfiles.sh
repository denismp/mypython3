#!/bin/bash
#!/usr/bin/ksh
set -x
for ((i=0;i<9999;i++))
do
	echo $i
	cp filler.txt ./files/$i
done
exit 0
