#!/bin/bash

input_dir="../tests/input_data/nfs/workflow_sort/"
policy=$1

#conservative
if [ "$policy" = "conservative" ]
then
    echo "testing conservative policy with a serial workflow"
    actual_serial="/tmp/actual.conservative.serial.workflow"
    python ./nfs_trace_policies.py "c" < $input_dir/serial.workflow > $actual_serial
    diff $input_dir/expected.conservative.serial.workflow $actual_serial

    echo "testing conservative policy with an interleaved workflow"
    actual_interleaved="/tmp/actual.conservative.interleaved.workflow"
    python ./nfs_trace_policies.py "c" < $input_dir/interleaved.workflow > $actual_interleaved
    diff $input_dir/expected.conservative.interleaved.workflow $actual_interleaved
elif [ "$policy" = "fs" ]
then
    #FS
    echo "testing FS policy with a serial workflow"
    actual_fs_serial="/tmp/actual.fs.serial.workflow"
    python ./nfs_trace_policies.py "fs" < $input_dir/serial.workflow > $actual_fs_serial
    diff $input_dir/expected.fs.serial.workflow $actual_fs_serial
fi
