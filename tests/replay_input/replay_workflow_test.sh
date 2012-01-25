#!/bin/bash

replayer_path=$1
workload_input=$2
verbose=$3

usage_msg="Usage: $0 replayer_path workload_input -v [optional]"

pre_replay()
{
    if [ -f $workload_input.pre ]
    then 
        echo "Running setup $workload_input.pre"
        $workload_input.pre
    fi
}

replay()
{
    strace -ttt -f -e trace=open,close,read,write,mkdir,stat64 -o strace.output $replayer_path $workload_input
    sed -i 's/stat64/stat/g' strace.output
    python match_syscalls.py $verbose strace.output $workload_input
}

post_replay()
{
    if [ -f $workload_input.post ]
    then 
        echo "Running tear down $workload_input.post"
        $workload_input.post
    fi
}

if [ ! -f $replayer_path ]
then 
    echo "Missing replayer_path parameter"
    echo $usage_msg
    exit 1
fi

if [ ! -f $workload_input ]
then 
    echo "Missing workload_input parameter"
    echo $usage_msg
    exit 1
fi

#setup env. e.g create files and directories
pre_replay

replay

#tear down env e.g delete files and directories
post_replay
