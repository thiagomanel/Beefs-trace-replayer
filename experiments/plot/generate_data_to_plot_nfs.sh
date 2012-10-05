#!/bin/bash

# It generates data to plot for a collection of replayer output files

if [ $# -ne 4 ]
then
	echo "Usage:" $0 "output_dir traces_file machines_file out_file"
	exit 1
fi

outdir=$1
# output files stored on outdir follow this naming format:
#     machine.seq_number.random_num.replay.out
traces=$2 #path to a text file, each line is a path to a replay input file
machines=$3 #path to a text file, each line is the address of a replay client machine
# Note that, Nth machine in machine file replayed the Nth replay input file in traces file

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

out_data=$4

if [ -f $out_data ]
then
    echo "File" $out_data "already exists"
    exit 1
fi

system="nfs"
stamp="None"

# output_dir/machine_ip.$sample.$random.replay.out
for i in `seq $num_lines`
do
    machine=`sed -n ${i}p $machines`
    trace=`sed -n ${i}p $traces`

    #trace is something likewise /local/thiagoepdc/input/2011_10_21-abelhinha.clean.cut.order
    #original client machine should be abelhinha
    original_client=`basename $trace | cut -d"-" -f2 | cut -d"." -f1`

    for file in `find ${outdir} -name "${machine}*.replay.out"`
    do
        #192.168.1.8.4.2676313.replay.out
        sample=`basename $file | cut -d"." -f5`
        plot_data=$file.`basename $trace`.plot.data
        #transformed output format -> operation_type	latency	expected_rvalue	actual_rvalue
        python transform_output.py $trace.expected $file > $plot_data.tmp

        #final format (sep by \t) -> operation_type latency expected_rvalue actual_rvalue system machine trace_input sample
        awk -v args="$system\t$machine\t$original_client\t$sample\t$stamp" '{ printf("%s\t%s\t%s\t%s\t%s\n", $1, $2, $3, $4, args); }' $plot_data.tmp >> $out_data
        rm $plot_data.tmp
    done
done
