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
    #e.g /local/tracer/processed/abelhinha/20111014/2011_10_14-abelhinha.clean
    base=`basename $file`
    year=`echo ${base:0:4}`
    month=`echo ${base:5:2}`
    day=`echo ${base:8:2}`
    epoch=`date -d "$year-$month-$day 00:00:00" +%s`
    machine=`echo $base | cut -d"-" -f2 | cut -d"." -f1`
    python input_load_analysis.py r ${epoch}000000 600000000 $file $machine > $file.ops
done
