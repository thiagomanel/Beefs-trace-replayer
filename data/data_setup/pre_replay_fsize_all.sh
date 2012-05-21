#!/bin/bash

if [ $# -ne 2 ]
then 
    echo "Usage:" $0 "workflow_data_dir" "cated_pre_replay_file"
    exit 1
fi

workflow_data_dir=$1
#all pre_replay files cat'ed in a single file
cated_pre_replay_file=$2

if [ ! -d $workflow_data_dir ]
then
    echo $workflow_data_dir "does not exist"
    exit 1
fi

if [ ! -f $cated_pre_replay_file ]
then
    echo $cated_pre_replay_file "does not exist"
    exit 1
fi

> solve_size.out
for file in `ls $workflow_data_dir/*.order`
do
    python ../pre_replay_fsize.py $cated_pre_replay_file $file >> solve_size.out
done

python merge_solve_size_lines.py solve_size.out $cated_pre_replay_file > $cated_pre_replay_file.size
