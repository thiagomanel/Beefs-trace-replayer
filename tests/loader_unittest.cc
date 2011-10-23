/**
 * Copyright (C) 2009 Universidade Federal de Campina Grande
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include "../src/loader.h"
#include "gtest/gtest.h"
#include <stdlib.h>


TEST(LoaderTest, EmptyInputFile) {
    struct replay_workload rep_wld;
    FILE * input_f = fopen("tests/empty_input", "r");
    int ret = load(&rep_wld, input_f);
    EXPECT_EQ(0, ret);
    EXPECT_EQ(0, rep_wld.num_cmds);
    EXPECT_EQ(0, rep_wld.current_cmd);
    fclose(input_f);
}

//FIXME test args for the loaded syscalls
//FIXME test timestamp for the loaded syscalls.

TEST(LoaderTest, LoadCloseCall) {
//0 2097 2097 (udisks-daemon) sys_close 1318539063006403-37 7 0
    struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
    FILE * input_f = fopen("tests/close_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(CLOSE_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(2097, caller_id->pid);
    EXPECT_EQ(2097, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadFstatCall) {
	//syscall.fstat
	//uid pid tid exec_name sys_fstat begin-elapsed fd return
	//1159 2076 2194 (gnome-do) sys_fstat64 1318539073583678-143 23 0
	//FIXME What if in other arch the calls name is not fstat64 ?
    struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
    FILE * input_f = fopen("tests/fstat_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(FSTAT_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2076, caller_id->pid);
    EXPECT_EQ(2194, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadRmdirCall) {
    //uid pid tid exec_name rmdir begin-elapsed fullpath return
    //1159 2364 32311 (eclipse) rmdir 1318539134542480-46 /home/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images -1

    struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
    FILE * input_f = fopen("tests/rmdir_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(RMDIR_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);
    fclose(input_f);
}
