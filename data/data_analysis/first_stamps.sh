#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 processed_dir_root"
    exit 1
fi

processed_dir_root=$1

if [ ! -d $processed_dir_root ]; then
    echo $processed_dir_root " does not exist. Usage: $0 processed_dir_root"
    exit 1
fi

for file in `find $processed_dir_root -type f -name "*clean"`
do
    stamp=`head -n 1 $file | grep -v "<==" | cut -d' ' -f6`
    echo $file $stamp
    useconds=`echo $stamp | cut -d"-" -f 1`
    echo `date -d @${useconds:0:10}`
done
