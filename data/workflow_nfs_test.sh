#!/bin/bash

input_dir="../tests/input_data/nfs/workflow_sort/"

#conservative
echo "testing conservative policy with a serial workflow"
actual_serial="/tmp/actual.conservative.serial.workflow"
python ./nfs_trace_policies.py "c" < $input_dir/serial.workflow > $actual_serial
diff $input_dir/expected.conservative.serial.workflow $actual_serial

echo "testing conservative policy with an interleaved workflow"
actual_interleaved="/tmp/actual.conservative.interleaved.workflow"
python ./nfs_trace_policies.py "c" < $input_dir/interleaved.workflow > $actual_interleaved
diff $input_dir/expected.conservative.interleaved.workflow $actual_interleaved
