#!/bin/bash

# It waits until a deadline and start replayer
if [ $# -ne 5 ]; then
    echo "Usage: $0 deadline_epoch replayer_path r_input r_out r_err"
    exit 1
fi

deadline=$1
replayer_path=$2
r_input=$3
r_out=$4
r_err=$5

if [ ! $replayer_path ]
then
    echo $replayer_path "does not exist"
    exit 1
fi

now=`date +%s`
secs_to_wait=`echo "${now} - ${deadline}" | bc`

sleep $secs_to_wait

$replayer_path $r_input > $r_out 2> $r_err &
