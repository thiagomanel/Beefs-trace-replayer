#!/bin/bash
#It concats .sort files within $data_dir directory. It sorts this concatened file

if [ $# -ne 2 ]
then
    echo "Usage: " $0 " data_dir output_name"
    exit 1
fi

data_dir=$1
output_name=$2

cat $data_dir/*.sort | sort -T /tmp -n -k 6,6.17 > $output_name.join
