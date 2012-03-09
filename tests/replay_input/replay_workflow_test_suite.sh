#!/bin/bash

bash ./replay_workflow_test.sh ../../beefs_replayer workflow_samples/workflow_single_command_open
bash ./replay_workflow_test.sh ../../beefs_replayer workflow_samples/workflow_single_command_mkdir
bash ./replay_workflow_test.sh ../../beefs_replayer workflow_samples/workflow_single_command_stat
bash ./replay_workflow_test.sh ../../beefs_replayer workflow_samples/workflow_2_sequencial_command_mkdir
bash ./replay_workflow_test.sh ../../beefs_replayer workflow_samples/workflow_2_sequencial_command_mkdir_with_large_wait
bash ./replay_workflow_test.sh ../../beefs_replayer workflow_samples/workflow_48_sequencial_command_mkdir
bash ./replay_workflow_test.sh ../../beefs_replayer workflow_samples/workflow_sequencial_open_read_close_same_file
bash ./replay_workflow_test.sh ../../beefs_replayer workflow_samples/workflow_sequencial_open_write_close_same_file
bash ./replay_workflow_test.sh ../../beefs_replayer workflow_samples/workflow_9_seq__mkdir_and_an_independent
