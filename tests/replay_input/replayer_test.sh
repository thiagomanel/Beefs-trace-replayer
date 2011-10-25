#!/bin/bash

replayer_path=$1
workload_input=$2


strace $replayer_path $workload_input 2> strace.output
python match_syscalls.py strace.output $workload_input
