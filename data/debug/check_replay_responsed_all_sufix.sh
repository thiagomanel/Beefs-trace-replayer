#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Usage:" $0 "replay_result_dir"
    exit 1
fi

result_dir=$1

for trace_in in `ls $result_dir/*.order`
do
    trace_out=$trace_in.out
    python check_replay_responsed.py $trace_in $trace_out > $trace_in.check
    F=`grep False ${trace_in}.check | wc -l`
    T=`grep True ${trace_in}.check | wc -l`
    proportion=`echo "scale=5 ; ($F)/($F + $T)" | bc`
    echo "check for file:" $trace_out "False" $F "True" $T "F proportion" $proportion
done
