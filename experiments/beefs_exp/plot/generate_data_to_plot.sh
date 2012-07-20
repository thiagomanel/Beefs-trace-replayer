#!/bin/bash

# It generate date to plot for a collection of replayer output files

if [ $# -ne 4 ]
then
	echo "Usage:" $0 "output_dir traces_file machines_file system"
	exit 1
fi

outdir=$1
traces=$2
machines=$3
system=$4 #beefs or nfs

# traces stores replay input path, each line one input
# machines stores replay client machines names, each line one machine
# first machine used the first trace input
# output files stored on outdir follow this naming format:
#     machine.seq_number.random_num.replay.out

if [ ! -d $outdir ]
then
	echo "directory" $outdir "not available"
	exit 1
fi

if [ ! $traces ]
then
	echo "file" $traces "not available"
	exit 1
fi

if [ ! $machines ]
then
	echo "file" $machines "not available"
	exit 1
fi

num_lines=`cat $traces | wc -l`
if [ "$system" == "beefs" ]
then 
    num_lines=`echo "${num_lines} - 1" | bc`
fi

for i in `seq $num_lines`
do
    machine=`sed -n ${i}p $machines`
    trace=`sed -n ${i}p $traces`
    for file in `find ${outdir} -name "${machine}*.replay.out"`
    do
        plot_data=$file.`basename $trace`.plot.data
        python transform_output.py $trace.expected $file > $plot_data.tmp
        awk -v d="$system" '{ printf("%s\t%s\t%s\t%s\t\n", $1, $2, $3, d); }' $plot_data.tmp > $plot_data
        rm $plot_data.tmp
    done
done
