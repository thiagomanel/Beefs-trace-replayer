#!/bin/bash

# It cleans any processed data out withing a directory. Processed data
# follows this pattern:
# /mnt/backup_storage3/pepino/20111014/2011_10_14-pepino
# /mnt/backup_storage3/pepino/20111021/2011_10_21-pepino
# /mnt/backup_storage3/pepino/20111019/2011_10_19-pepino

if [ $# -ne 1 ]; then
    echo "Usage: $0 processed_dir_root"
    exit 1
fi

processed_dir_root=$1

if [ ! -d $processed_dir_root ]; then
    echo $processed_dir_root " does not exist. Usage: $0 processed_dir_root"
    exit 1
fi

for machine_dir in `ls -t $processed_dir_root`
do
    machine_name=`basename $machine_dir`
    processed_files=`find /mnt/backup_storage3/processed/ -type f -name "*$machine_name"`
    for file in $processed_files
    do
        python ../clean_trace.py < $file > $file.clean 2> $file.clean.err
    done
done
