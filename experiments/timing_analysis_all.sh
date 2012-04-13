#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 machines_file results_dir"
    exit 1
fi

machines_file=$1
results_dir=$2

if [ ! -f $machines_file ]
then 
    echo "File $machines_file does not exist"
    exit 1
fi

if [ ! -d $results_dir ]
then 
    echo "Directory $results_dir does not exist"
    exit 1
fi

while read line
do
    #machines_file follows this format
    #150.165.85.117 /root/nfs_lsd/thiagoepdc/experiments/nfs/2011_10_21-cherne.clean.cut.pidfid_order
    worker_node_id=`echo $line | cut -d" " -f1`
    input_file=`echo $line | cut -d" " -f2`
    #e.g output file naming format 150.165.85.23.0.5195761.replay.out
    # worker_node_id.random.replay.out
    
    #analyse all data from this machine
    for file in `ls -t $results_dir/$worker_node_id*replay.out`
    do
        base=`basename $file`
        python ../data/data_analysis/timing_analysis.py $input_file $file > $base.timing 2> $base.timing.err
    done

done < $machines_file
