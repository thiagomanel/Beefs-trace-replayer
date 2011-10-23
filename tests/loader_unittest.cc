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
//0 2097 2097 (udisks-daemon) close 1318539063006403-37 7 0
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
	//uid pid tid exec_name fstat begin-elapsed fd return
	//1159 2076 2194 (gnome-do) fstat 1318539073583678-143 23 0
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

TEST(LoaderTest, LoadLstatCall) {
//uid pid tid exec_name lstat begin-elapsed cwd filename return
//1159 2076 2194 (gnome-do) lstat 1318539555812393-87 /usr/share/applications/gnome-sudoku.desktop 0
    struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
    FILE * input_f = fopen("tests/lstat_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(LSTAT_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2076, caller_id->pid);
    EXPECT_EQ(2194, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadStatCall) {
    //syscall.stat
    //uid pid tid exec_name stat begin-elapsed fullpath return
    //0 1163 1163 (cron) stat 1317750601526436-18178 /var/spool/cron/crontabs 0
    struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
    FILE * input_f = fopen("tests/stat_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(STAT_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(1163, caller_id->pid);
    EXPECT_EQ(1163, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadStatfsCall) {
    //syscall.statfs
    //uid pid tid exec_name statfs begin-elapsed cwd pathname return
    //1159 2053 2053 (gnome-settings-) statfs 1318540136505344-287 /local/tracer/logs_nfs 0

    struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
    FILE * input_f = fopen("tests/statfs_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(STATFS_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2053, caller_id->pid);
    EXPECT_EQ(2053, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadDupCall) {
    //syscall.dup
    //uid pid tid exec_name dup begin-elapsed fd return
    //0 32544 32544 (sshd) dup 1318539601707575-31 4 5
    struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
    FILE * input_f = fopen("tests/dup_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(DUP_OP, loaded_cmd->command);
    EXPECT_EQ(5, loaded_cmd->expected_retval);
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(32544, caller_id->pid);
    EXPECT_EQ(32544, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadFstatfsCall) {
    //syscall.fstatfs
    //uid pid tid exec_name fstatfs begin-elapsed fd return
    //0 32544 32544 (sshd) fstatfs 1318539601707575-31 4 -1
    struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
    FILE * input_f = fopen("tests/fstatfs_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(FSTATFS_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(32544, caller_id->pid);
    EXPECT_EQ(32544, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadReaddirCall) {
    //uid pid tid exec_name readdir begin-elapsed fullpath return
    //1159 2076 2194 (gnome-do) readdir 1318539555798359-27 /usr/share/applications/ 0
    struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
    FILE * input_f = fopen("tests/readdir_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(READDIR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2076, caller_id->pid);
    EXPECT_EQ(2194, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadUnlinkCall) {
    //syscall.unlink
    //uid pid tid exec_name sys_unlink begin-elapsed fullpath return
    //1159 2364 32311 (eclipse) sys_unlink 1318539134533662-8118 /home/thiagoepdc/ /local/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images/1.png 0
    struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
    FILE * input_f = fopen("tests/unlink_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(UNLINK_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);
    fclose(input_f);
}
