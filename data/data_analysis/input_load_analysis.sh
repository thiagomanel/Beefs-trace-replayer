#!/bin/bash

file=$1
#e.g /local/tracer/processed/abelhinha/20111014/2011_10_14-abelhinha.clean

base=`basename $file`
year=`echo ${base:0:4}`
month=`echo ${base:5:2}`
day=`echo ${base:8:2}`
epoch=`date -d "$year-$month-$day 00:00:00" +%s`
machine=`echo $base | cut -d"-" -f2 | cut -d"." -f1`
python input_load_analysis.py 600000000 $file > $file.ops
