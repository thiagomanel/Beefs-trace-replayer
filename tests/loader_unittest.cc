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

#define MSG_ENTRY(M) { M, #M }
struct msg_desc_t {
        op_t msg_type;
        char *str_type;
};

TEST(LoaderTest, EmptyInputFile) {
    printf("%s\n", MSG_ENTRY(CLOSE_OP).str_type);

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
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(2097, caller_id->pid);
    EXPECT_EQ(2097, caller_id->tid);
    EXPECT_EQ(0, strcmp("udisks-daemon", caller_id->exec_name));
    fclose(input_f);
}

TEST(LoaderTest, LoadMunmapCall) {
//0 1102 32513 (automount) sys_munmap 1318539548518148-18 0xb76cb000 4096 0
    struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
    FILE * input_f = fopen("tests/munmap_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(MUNMAP_OP, loaded_cmd->command);
    struct caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(1102, caller_id->pid);
    EXPECT_EQ(32513, caller_id->tid);
    EXPECT_EQ(0, strcmp("automount", caller_id->exec_name));
    fclose(input_f);
}
