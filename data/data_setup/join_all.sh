#!/bin/bash

# It join by date and sort it processed data out
# e.g processed date dirs
#    /local/tracer/processed/charroco/20111014/
#    /local/tracer/processed/charroco/20111021/
#    /local/tracer/processed/cherne/20111014
#
# Then, we have processed dir root /local/tracer/processed/
#
# The raw_dir_file follows this pattern
#   /local/trace/logs/charroco
# So we get the file name

if [ $# -ne 2 ]; then 
    echo "Usage: $0 raw_dir_file processed_dir_root"
    exit 1
fi 

raw_dir_file=$1
processed_dir_root=$2

if [ ! -d $processed_dir_root ]; then
    echo $processed_dir_root " does not exist. Usage: $0 raw_dir_file processed_dir_root"
    exit 1
fi

while read raw_dir
do
    machine_name=`basename $raw_dir`
    for day_dir in `ls -t $processed_dir_root/$machine_name/`
    do
        python join_by_date_and_sort.py $processed_dir_root/$machine_name/$day_dir
    done
done < $raw_dir_file
