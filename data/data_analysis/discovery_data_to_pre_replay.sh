#!/bin/bash

# This scripts reads a workflow file and finds the directories under the /home that we need
# to create during pre-replay
# machine to
#
# input file
#    mulato /home/igorvcs/
#    roncador /home/tiagohsl/
input_file=$1
dir=$2
home="home"

for file in `ls ${dir}/*pidfid_order`
do
    #2011_10_21-roncador.clean.cut.pidfid_order
    machine=`echo $file | cut -d"-" -f2 | cut -d"." -f 1`
    likely_dir=`grep $machine $input_file | cut -d" " -f2`
    non_likely_dirs=`grep $home $file | grep -v $likely_dir`
    echo $machine " has these unlikely dirs " $non_likely_dirs
done
