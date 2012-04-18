#!/bin/bash

# It generates files to be pre-replayed. To do so, it needs:
#	1. traces_input_dir - to know which files are acessed during the trace replay
#	2. replay_dir - to know if the files accessed during the trace replay do exist or not. Note it needs to be mounted in the machine this script run. It need also be in a consistent state (demands a rollback it was modified by a replay)
#	3. output_dir - to save results

if [ $# -ne 3 ]
then
	echo "Usage:" $0 "traces_input_dir replay_dir output_dir"
	exit 1
fi

replay_input_dir=$1
#moint point storing fs to replay
replay_dir=$2
output_dir=$3

machines="abelhinha  charroco  cherne  mulato  mussum  pepino  pitu  roncador  sargento  traira"

if [ ! -d $replay_input_dir ]
then
	echo "traces_input_dir" $replay_input_dir "does not exist"
	exit 1
fi

if [ ! -d $replay_dir ]
then
	echo "replay_dir" $replay_dir "does not exist"
	exit 1
fi

if [ ! -d $output_dir ]
then
	echo "outdir" $output_dir "does not exist"
	exit 1
fi

for machine in $machines
do
    filename="2011_10_21-${machine}"
    python pre_replay.py $replay_dir -f $replay_input_dir/$filename.clean.cut.pidfid_order > $output_dir/$filename.clean.cut.pidfid_order.to_create 2> $output_dir/$filename.clean.cut.pidfid_order.to_create.err
done
