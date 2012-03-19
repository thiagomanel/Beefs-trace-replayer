#!/bin/bash
#It generates workflow files for all cleaned files in dir data_dir

if [ $# -ne 1 ]
then
    echo "Usage: " $0 " data_dir"
    exit 1
fi

data_dir=$1
for file in `find $data_dir -name "*.cut" -type f`
do
    python ../trace2workflow.py < $file > $file.pidfid_order
done 
