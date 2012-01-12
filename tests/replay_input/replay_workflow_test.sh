#!/bin/bash

replayer_path=$1
workload_input=$2
verbose=$3

strace -f -e trace=open,close,read,write,mkdir,stat64  $replayer_path $workload_input 2> strace.output
sed -i 's/stat64/stat/g' strace.output
python match_syscalls.py $verbose strace.output $workload_input
