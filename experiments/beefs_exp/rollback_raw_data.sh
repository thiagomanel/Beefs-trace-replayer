#!/bin/bash

# It rsyncs local raw data with a backup dir
# First rsync will take a lot, don't worry


if [ $# -ne 2 ]
then
	echo "Usage:" $0 "backup_dir local_raw_dir"
	exit 1
fi

#backup path is usually a remote dir as such hostname:/path
BACKUP_PATH=$1
DST_PATH=$2

if [ ! -d $DST_PATH ]
then
    echo "local_raw_dir" $DST_PATH "does not exist"
fi

rsync -progtl --delete $BACKUP_PATH/* $DST_PATH/
