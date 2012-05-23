#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Usage:" $0 "replay_result_dir"
    exit 1
fi

result_dir=$1

for trace_in in `ls $result_dir/*.order`
do
    rm /tmp/tmp.check
    trace_out=$trace_in.out
    python check_replay_responsed.py $trace_in $trace_out > /tmp/tmp.check
    F=`grep False /tmp/tmp.check | wc -l`
    T=`grep True /tmp/tmp.check | wc -l`
    echo "check for file:" $trace_out "False" $F "True" $T
done
