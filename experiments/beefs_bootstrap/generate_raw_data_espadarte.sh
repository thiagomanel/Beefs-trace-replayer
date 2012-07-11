#!/bin/bash

# it the beefs backup data. It is used to build OSDs raw data.
# we augment it with the hidden files (using pre_replay data)

# this script is supposed to run in espadarte using sudo

nfs_backup_data="/local/nfs_manel"
beefs_backup_data="/local/beefs_backup"

users="igorvcs armstrongmsg patrickjem nathaniel jeymissonebeo manoelfmn thiagoepdc heitor"

if [ $# -ne 1 ]
then
    echo "Usage:" $0 "pre_replay_file"
    exit 1
fi

pre_replay_data=$1
if [ ! -f $pre_replay_data ]
then
    echo "File:" $pre_replay_data "does not exist"
    exit 1
fi

for user in $users
do
     rsync -progtl --delete $nfs_backup_data/$user $beefs_backup_data/
done

python pre_replay_beefs_backup.py $nfs_backup_data $beefs_backup_data $pre_replay_data
