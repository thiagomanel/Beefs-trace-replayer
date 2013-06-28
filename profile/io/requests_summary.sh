#!/bin/bash
# summarise the block output (iolatency)

outfile=$1

function summary_thread
{
	local outpath=$1
	local execname=$2
	local log_type=$3
	local device=$4
	local request_type=$5

	#log_type = ["request", merge", "complete"]
	#request_type= ["R", "W"]
	grep $execname $outpath | grep $log_type | grep $device | grep "rw="$request_type | cut -d" " -f2,3 | sort | uniq -c
}


echo "### top 10 requesters ###"
cut -d" " -f4 $outfile | sort | uniq -c | sort -n | tail -n 10

echo ""

total=`cat $outfile | wc -l`
beefs=`grep beefs_replayer $outfile | wc -l`
echo "total" $total "beefs" $beefs

echo ""

echo "### beefs by request type ###"
grep beefs_replayer $outfile | cut -d" " -f1 | sort | uniq -c

echo ""

echo "### beefs dispatched requests by device ###"
grep beefs_replayer $outfile | grep request | cut -d" " -f5 | sort | uniq -c

echo ""

echo "### beefs merged requests by device ###"
grep beefs_replayer $outfile | grep merge | cut -d" " -f5 | sort | uniq -c

echo ""

echo "### beefs completed requests by device ###"
grep beefs_replayer $outfile | grep complete | cut -d" " -f5 | sort | uniq -c

echo ""
echo "### beefs summary per thread ###"

for log_type in request merge complete
do
    for device in sda sdb
    do
	for request_type in R W
	do
	    echo $log_type $device $request_type
	    summary_thread $outfile "beefs_replayer" $log_type $device $request_type
	done
    done
    echo ""
done

echo ""
echo "### non-beefs on sdb by request type ###"
grep -v beefs_replayer $outfile | grep sdb | cut -d" " -f1 | sort | uniq -c

echo ""

echo "### top 10 non-beefs requesters on sdb ###"
grep -v beefs_replayer $outfile | grep sdb | cut -d" " -f4 | sort | uniq -c | sort -n | tail -n 10
