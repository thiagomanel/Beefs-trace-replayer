#!/bin/bash
#It sorts all .filtered files within $data_dir directory. It outputs sort data in stdout

if [ $# -ne 1 ]
then
    echo "Usage: " $0 " data_dir"
    exit 1
fi

data_dir=$1

#we sort each file because we might can concat any subset of them in the future
for file in `find $data_dir -name "*.filtered" -type f`
do
    cat $file | sort -T /tmp -n -k 6,6.17 > $file.sort
done
