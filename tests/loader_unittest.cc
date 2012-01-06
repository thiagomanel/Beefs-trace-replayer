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
//#include "../src/loader.h"
#include "loader.h"
#include "replayer.h"
#include "gtest/gtest.h"
#include <stdlib.h>

TEST(LoaderTest, EmptyInputFile) {
    Replay_workload rep_wld;
    FILE * input_f = fopen("tests/input_data/empty_input", "r");
    int ret = load(&rep_wld, input_f);
    EXPECT_EQ(0, ret);
    EXPECT_EQ(0, rep_wld.num_cmds);
    EXPECT_EQ(0, rep_wld.current_cmd);
    fclose(input_f);
}

TEST(LoaderTest, NonexistentInputFile) {
    Replay_workload rep_wld;
    FILE * input_f = fopen("tests/input_data/nonexistent_input", "r");
    int ret = load(&rep_wld, input_f);
    EXPECT_EQ(-3, ret);
    EXPECT_EQ(0, rep_wld.num_cmds);
    EXPECT_EQ(0, rep_wld.current_cmd);
}

//FIXME test args for the loaded syscalls
//FIXME test timestamp for the loaded syscalls.
//test for a misformatted op

TEST(LoaderTest, LoadCloseCall) {
//0 2097 2097 (udisks-daemon) close 1318539063006403-37 7 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/close_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(CLOSE_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(2097, caller_id->pid);
    EXPECT_EQ(2097, caller_id->tid);
//args
    EXPECT_EQ(7, loaded_cmd->params[0].arg.i_val);
    fclose(input_f);
}

TEST(LoaderTest, LoadFstatCall) {
	//syscall.fstat
	//uid pid tid exec_name fstat begin-elapsed fd return
	//1159 2076 2194 (gnome-do) fstat 1318539073583678-143 23 0
	//FIXME What if in other arch the calls name is not fstat64 ?
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/fstat_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(FSTAT_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2076, caller_id->pid);
    EXPECT_EQ(2194, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadRmdirCall) {
    //uid pid tid exec_name rmdir begin-elapsed fullpath return
    //1159 2364 32311 (eclipse) rmdir 1318539134542480-46 /home/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images -1

    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/rmdir_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(RMDIR_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadLstatCall) {
//uid pid tid exec_name lstat begin-elapsed cwd filename return
//1159 2076 2194 (gnome-do) lstat 1318539555812393-87 /usr/share/applications/gnome-sudoku.desktop 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/lstat_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(LSTAT_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2076, caller_id->pid);
    EXPECT_EQ(2194, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadStatCall) {
    //syscall.stat
    //uid pid tid exec_name stat begin-elapsed fullpath return
    //0 1163 1163 (cron) stat 1317750601526436-18178 /var/spool/cron/crontabs 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/stat_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(STAT_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(1163, caller_id->pid);
    EXPECT_EQ(1163, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadStatfsCall) {
    //syscall.statfs
    //uid pid tid exec_name statfs begin-elapsed cwd pathname return
    //1159 2053 2053 (gnome-settings-) statfs 1318540136505344-287 /local/tracer/logs_nfs 0

    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/statfs_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(STATFS_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2053, caller_id->pid);
    EXPECT_EQ(2053, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadDupCall) {
    //syscall.dup
    //uid pid tid exec_name dup begin-elapsed fd return
    //0 32544 32544 (sshd) dup 1318539601707575-31 4 5
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/dup_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(DUP_OP, loaded_cmd->command);
    EXPECT_EQ(5, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(32544, caller_id->pid);
    EXPECT_EQ(32544, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadFstatfsCall) {
    //syscall.fstatfs
    //uid pid tid exec_name fstatfs begin-elapsed fd return
    //0 32544 32544 (sshd) fstatfs 1318539601707575-31 4 -1
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/fstatfs_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(FSTATFS_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(32544, caller_id->pid);
    EXPECT_EQ(32544, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadReaddirCall) {
    //uid pid tid exec_name readdir begin-elapsed fullpath return
    //1159 2076 2194 (gnome-do) readdir 1318539555798359-27 /usr/share/applications/ 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/readdir_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(READDIR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2076, caller_id->pid);
    EXPECT_EQ(2194, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadUnlinkCall) {
    //syscall.unlink
    //uid pid tid exec_name unlink begin-elapsed fullpath return
    //1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images/1.png 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/unlink_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(UNLINK_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadGetattrCall) {
    //getattr
    //uid pid tid exec_name getattr begin-elapsed fullpath return
    //0 1547 1547 (puppet) getattr 1318539062631232-30 /etc/puppet/puppet.conf 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/getattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(GETATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(1547, caller_id->pid);
    EXPECT_EQ(1547, caller_id->tid);
    fclose(input_f);
}

//FIXME test problems when reading file input
TEST(LoaderTest, LoadOpenCall) {
	//TODO: args
    //syscall.open
    //uid pid tid exec_name open begin-elapsed fullpath flags mode return
    //0 2097 2097 (udisks-daemon) open 1318539063003892-2505 /dev/sdb 34816 0 7
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/open_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(OPEN_OP, loaded_cmd->command);
    EXPECT_EQ(7, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(2097, caller_id->pid);
    EXPECT_EQ(2097, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadDup2Call) {
	//syscall.dup2
	//uid pid tid exec_name dup2 begin-elapsed oldfd newfd return
	//0 32544 32544 (sshd) dup2 1318539601707761-41 4 0 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/dup2_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(DUP2_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(32544, caller_id->pid);
    EXPECT_EQ(32544, caller_id->tid);
    fclose(input_f);
}
TEST(LoaderTest, LoadDup3Call) {
	//syscall.dup3
	//uid pid tid exec_name dup3 begin-elapsed oldfd newfd return
	//0 32544 32544 (sshd) dup3 1318539601707761-41 4 0 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/dup3_input", "r");
    int ret = load(rep_wld, input_f);
        
    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(DUP3_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(32544, caller_id->pid);
    EXPECT_EQ(32544, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadWriteCall) {
	//syscall.write
	//uid pid tid exec_name write begin-elapsed root pwd fullpath fd count return
	//0 6194 6194 (xprintidle) write 1318539063058255-131 /local/userActivityTracker/logs/tracker.log 1 17 17
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/write_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(WRITE_OP, loaded_cmd->command);
    EXPECT_EQ(17, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(6194, caller_id->pid);
    EXPECT_EQ(6194, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadReadCall) {
	//syscall.read
	//uid pid tid exec_name read begin-elapsed fullpath fd count return
	//114 1562 1562 (snmpd) read 1318539063447564-329 /proc/stat 8 3072 2971
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/read_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(READ_OP, loaded_cmd->command);
    EXPECT_EQ(2971, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(114, caller_id->uid);
    EXPECT_EQ(1562, caller_id->pid);
    EXPECT_EQ(1562, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadLLseekCall) {
//syscall.llseek
//uid pid tid exec_name llseek begin-elapsed fullpath fd offset_high offset_low whence_str $result
//1159 2364 2364 (eclipse) llseek 1318539072857083-113 /local/thiagoepdc/eclipse/configuration/org.eclipse.core.runtime/.mainData.4 30 0 931001 SEEK_SET 931001
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/llseek_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(LLSEEK_OP, loaded_cmd->command);
    EXPECT_EQ(931001, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(2364, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadMkdirCall) {
//syscall.mkdir
//uid pid tid exec_name mkdir begin-elapsed fulpath mode return
//1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /local/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images 511 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/mkdir_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(MKDIR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadMknodCall) {
//mknod
//uid pid tid exec_name mknod begin-elapsed fullpath mode dev return
//1159 11407 11407 (gconftool-2) mknod 1319207649254700-14 /home/thiagoepdc/orbit-thiagoepdc/linc-2c8f-0-69f0eff3e2d5 S_IFSOCK|S_IXOTH|S_IROTH|S_IXGRP|S_IRGRP|S_IRWXU 0 0
//TODO: we need to convert mode from string to a number type
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/mknod_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(MKNOD_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(11407, caller_id->pid);
    EXPECT_EQ(11407, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadSymlink) {
//syscall.symlink
//uid pid tid exec_name symlink begin-elapsed  oldname newname return
//0 603 603 (update-rc.d) symlink 1318540206298997-36 /etc/rcS.d/../init.d/puppet /etc/rc0.d/K20puppet 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/symlink_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(SYMLINK_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(603, caller_id->pid);
    EXPECT_EQ(603, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadReadlink) {
//syscall.readlink
//uid pid tid exec_name readlink begin-elapsed fullpath return
//1159 2092 2092 (gvfs-gdu-volume) readlink 1318539355485686-40 /dev/scd0 3
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/readlink_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(READLINK_OP, loaded_cmd->command);
    EXPECT_EQ(3, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2092, caller_id->pid);
    EXPECT_EQ(2092, caller_id->tid);
    fclose(input_f);
}

//Note xattr calls will be called as fake
TEST(LoaderTest, LoadGetxattr) {
//getxattr
//uid pid tid exec_name getxattr begin-elapsed fullpath return
//1159 32362 32362 (ls) getxattr 1318539209608557-21 /tmp/0014b4e97285d -95
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/getxattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(GETXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-95, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadRemovexattr) {
//syscall.removexattr
//uid pid tid exec_name removexattr begin-elapsed fullpath return
//1159 32362 32362 (ls) removexattr 1318539209608557-21 /tmp/0014b4e97285d 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/removexattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(REMOVEXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadSetxattr) {
//syscall.setxattr
//uid pid tid exec_name setxattr begin-elapsed fullpath return
//1159 32362 32362 (ls) setxattr 1318539209608557-21 /tmp/0014b4e97285d -3
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/setxattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(SETXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-3, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadListxattr) {
//syscall.listxattr
//uid pid tid exec_name listxattr begin-elapsed fullpath return
//1159 32362 32362 (ls) listxattr 1318539209608557-21 /tmp/0014b4e97285d 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/listxattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(LISTXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadLremovexattr) {
//syscall.lremovexattr
//uid pid tid exec_name lremovexattr begin-elapsed fulpath return
//1159 32362 32362 (ls) lremovexattr 1318539209608557-21 /tmp/0014b4e97285d -1

    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/lremovexattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(LREMOVEXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadLlistxattr) {
//syscall.llistxattr
//uid pid tid exec_name llistxattr begin-elapsed fullpath list return
//1159 32362 32362 (ls) llistxattr 1318539209608557-21 /tmp/0014b4e97285d -1
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/llistxattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(LLISTXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadFgetxattr) {
//syscall.fgetxattr
//uid pid tid exec_name fgetxattr begin-elapsed fd return
//1159 32362 32362 (ls) fgetxattr 1318539209608557-21 /tmp/0014b4e97285d -1
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/fgetxattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(FGETXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadFremovexattr) {
//syscall.fremovexattr
//uid pid tid exec_name fremovexattr begin-elapsed fd return
//1159 32362 32362 (ls) fremovexattr 1318539209608557-21 /tmp/0014b4e97285d 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/fremovexattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(FREMOVEXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadFsetxattr) {
//syscall.fsetxattr
//uid pid tid exec_name fsetxattr begin-elapsed fd return
//1159 32362 32362 (ls) fsetxattr 1318539209608557-21 /tmp/0014b4e97285d -2
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/fsetxattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(FSETXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-2, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadFlistxattr) {
//syscall.flistxattr
//uid pid tid exec_name flistxattr begin-elapsed fd return
//1159 32362 32362 (ls) flistxattr 1318539209608557-21 /tmp/0014b4e97285d 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/flistxattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(FLISTXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
    fclose(input_f);
}

TEST(LoaderTest, LoadLsetxattr) {
//syscall.lsetxattr
//uid pid tid exec_name lsetxattr begin-elapsed cwd pathname name value flags return
//1159 32362 32362 (chmod) lsetxattr 1318539209608557-21 /tmp/0014b4e97285d 34 33 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/lsetxattr_input", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(1, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;

    EXPECT_EQ(LSETXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);

    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
    fclose(input_f);
}


TEST(LoaderTest, LoadMany) {
//syscall.mkdir
//uid pid tid exec_name mkdir begin-elapsed fulpath mode return
//1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /local/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images 511 0
//1159 2364 32311 (eclipse) mkdir 1318539134552649-480 /local/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images2 511 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/input_2_calls", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(2, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(MKDIR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);

    loaded_cmd = loaded_cmd->next;
    EXPECT_EQ(MKDIR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);
//FIXME: ARGS
    fclose(input_f);
}

/** 
* we faced a bug when replaying a stat followed by two open, open file names
* repeat stat parameters
*/

TEST(LoaderTest, LoadStatAndOpens) {
    //syscall.stat
//0 1163 1163 (cron) stat 1317750601526436-18178 /var/spool/cron/crontabs 0
//0 2097 2097 (udisks-daemon) open 1318539063003892-2505 /tmp/foo 34816 0 7
//0 2097 2097 (udisks-daemon) open 1318539063003892-2505 /tmp/foo2 34816 0 7
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/input_data/statAndOpens_input", "r");
    int ret = load(rep_wld, input_f);
    EXPECT_EQ(3, rep_wld->num_cmds);
    EXPECT_EQ(0, ret);
    EXPECT_EQ(0, rep_wld->current_cmd);

    struct replay_command* loaded_cmd = rep_wld->cmd;
    EXPECT_EQ(STAT_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(1163, caller_id->pid);
    EXPECT_EQ(1163, caller_id->tid);

    loaded_cmd = loaded_cmd->next;	
    EXPECT_EQ(OPEN_OP, loaded_cmd->command);
    EXPECT_EQ(7, loaded_cmd->expected_retval);
    caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(2097, caller_id->pid);
    EXPECT_EQ(2097, caller_id->tid);
    EXPECT_TRUE(strcmp("/tmp/foo", loaded_cmd->params[0].arg.cprt_val) == 0);

    loaded_cmd = loaded_cmd->next;	
    EXPECT_EQ(OPEN_OP, loaded_cmd->command);
    EXPECT_EQ(7, loaded_cmd->expected_retval);
    caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(2097, caller_id->pid);
    EXPECT_EQ(2097, caller_id->tid);
    EXPECT_TRUE(strcmp("/tmp/foo2", loaded_cmd->params[0].arg.cprt_val) == 0);
    fclose(input_f);
}

TEST(ReplayTest, SingleOperationReplay) {

	Replay_workload* rep_wld
		= (Replay_workload*) malloc (sizeof (Replay_workload));
	
	//filling workload_element (TODO: it may be moved from this test to code)
	rep_wld->element = (Workflow_element*) malloc (sizeof (Workflow_element));
	rep_wld->element->n_children = 0;
	rep_wld->element->children = NULL;

	rep_wld->element->n_parents = 0;
	rep_wld->element->parents = NULL;

	rep_wld->element->produced = 0;
	rep_wld->element->consumed = 0;
	

	rep_wld->element->command
		= (struct replay_command*) malloc( sizeof (struct replay_command));

	fill_replay_command (rep_wld->element->command);
	//end workload_element filling

	rep_wld->element->command->params = (Parms*) malloc (3 * sizeof (Parms));

	Parms* parm;
	parm = rep_wld->element->command->params;
	parm[0].arg.cprt_val = (char*) malloc (MAX_FILE_NAME * sizeof (char));
	strcpy (parm[0].arg.cprt_val, "fileToOpen");
	parm[1].arg.i_val = 34816;//flag
	parm[2].arg.i_val = 0; //mode

	rep_wld->num_cmds = 1;

	Replay_result* actual_result = (Replay_result*) malloc (sizeof (Replay_result));
	actual_result->replayed_commands = 0;
	actual_result->produced_commands = 0;

	replay (rep_wld, actual_result);

	EXPECT_EQ (1, actual_result->replayed_commands);
	EXPECT_EQ (1, actual_result->produced_commands);
}

TEST(LoaderTest, ParseWorkflowElement) {
			//uid pid tid exec_name mkdir begin-elapsed fulpath mode return
//1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0

	char line[] = "1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0";
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	parse_element (element, line);

    EXPECT_EQ(1, element->id);

    EXPECT_EQ(0, element->n_children);

    EXPECT_EQ(1, element->n_parents);
    int child_id = element->parents_ids[element->n_parents - 1];
    EXPECT_EQ(2, child_id);

    EXPECT_EQ(0, element->consumed);
    EXPECT_EQ(0, element->produced);

    struct replay_command* loaded_cmd = element->command;

    EXPECT_EQ(MKDIR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;

    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);

	Parms* parm = element->command->params;
	EXPECT_TRUE(strcmp("/tmp/jdt-images-1", parm[0].arg.cprt_val) == 0);
	EXPECT_EQ(511, parm[1].arg.i_val);

//2 1 1 1 3 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-2 511 0
}

TEST(LoaderTest, LoadWorkflow) {
			//uid pid tid exec_name mkdir begin-elapsed fulpath mode return
//1 1 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0
//2 1 1 1 3 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-2 511 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/replay_input/workflow_samples/workflow_2_sequencial_command_mkdir", "r");
    int ret = load2(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(2, rep_wld->num_cmds);
    EXPECT_EQ(0, rep_wld->current_cmd);

    /**
    struct replay_command* command;
    int n_children;
    int children_id[];//we are going to hash w_elements
    int n_parents;
    int parents_id[];//we are going to hash w_elements
   	int produced;
   	int consumed;
   	int id;

    Workflow_element* w_element = rep_wld->element;
    struct replay_command* loaded_cmd = w_element->command;

    EXPECT_EQ(MKDIR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);*/
    fclose(input_f);
}

