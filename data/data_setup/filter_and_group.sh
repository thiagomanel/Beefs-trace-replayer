#!/bin/bash

raw_data_dir=$1
output_data_dir=$2

if [ ! -d "$raw_data_dir" ] ; then
    echo "raw_data_dir={" $raw_data_dir "} does not exist"
    exit 1
fi

if [ ! -d "$output_data_dir" ] ; then
    echo "output_data_dir={" $output_data_dir "} does not exist"
    exit 1
fi

for file in `ls -tr $raw_data_dir`
do
    _date=`echo ${file:0:8}`
    if [ ! -d "$output_data_dir/$_date" ]; then
        mkdir $output_data_dir/$_date
    fi

    cat $raw_data_dir/$file | python ../filter_trace.py > $output_data_dir/$_date/$file.filtered
done
