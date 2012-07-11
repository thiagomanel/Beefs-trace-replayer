#!/bin/bash

# It stages-in all beefs raw data in a single local host. we want this to test
# replay locally, before go to remote cluster. We also may copy these staged
# directories to cluster nodes, instead of running stage_in.py on cluster nodes.
# Note the boot_data file should have fullpaths as seen on the remove server

if [ $# -ne 3 ]
then
	echo "Usage:" $0 "boot_data osd_map stagein_dst_dir"
	exit 1
fi

boot_data=$1
osd_map=$2
stagein_dir=$3

if [ ! -f $boot_data ]
then
    echo $boot_data "file not found"
    exit 1
fi

if [ ! -f $osd_map ]
then
    echo $osd_map "file not found"
    exit 1
fi

if [ ! -d $stagein_dir ]
then
    echo $stagein_dir "dir not found"
    exit 1
fi

for uuid in `cut -f2 $osd_map`
do 
    echo $uuid
    if [ ! -d $stagein_dir/$uuid ]
    then
        mkdir $stagein_dir/$uuid
    fi
    python stage_in.py $boot_data $uuid $stagein_dir/$uuid
done
