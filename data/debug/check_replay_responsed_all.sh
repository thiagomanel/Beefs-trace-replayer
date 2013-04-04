#!/bin/bash

if [ $# -ne 3 ]
then
    echo "Usage:" $0 "machine_file traces_file replay_result_dir"
    exit 1
fi

machines=$1
traces=$2
result_dir=$3


num_machines=`cat $machines | wc -l`

for i in `seq $num_machines`
do
    ip=`sed -n ${i}p $machines`
    trace=`sed -n ${i}p $traces`
    for trace_out in `ls $result_dir/$ip*replay.out`
    do
        total=`cat $trace_out | wc -l`
        rm /tmp/tmp.check
        python check_replay_responsed.py $trace.expected $trace_out > /tmp/tmp.check
        F=`grep False /tmp/tmp.check | wc -l`
        T=`grep True /tmp/tmp.check | wc -l`
        echo "check for file:" $trace_out "total" $total "False" $F "True" $T
    done
done
