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
    int ret = load (&rep_wld, input_f);
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
//1 0 - 1 2 0 2097 2097 (udisks-daemon) close 1318539063006403-37 7 0

	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 0 2097 2097 (udisks-daemon) close 1318539063006403-37 7 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

    struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(CLOSE_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);

    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(2097, caller_id->pid);
    EXPECT_EQ(2097, caller_id->tid);
//args
    EXPECT_EQ(7, loaded_cmd->params[0].argm->i_val);
}

TEST(LoaderTest, LoadFstatCall) {
	//syscall.fstat
	//uid pid tid exec_name fstat begin-elapsed fd return
	//1159 2076 2194 (gnome-do) fstat 1318539073583678-143 /home/thiagoepdc/.config/google-chrome/com.google.chrome.gUMVsk 23 0
	//FIXME What if in other arch the calls name is not fstat64 ?


	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 2076 2194 (gnome-do) fstat 1318539073583678-143 /home/thiagoepdc/.config/google-chrome/com.google.chrome.gUMVsk 23 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

    	struct replay_command* loaded_cmd = element->command;

	EXPECT_EQ(FSTAT_OP, loaded_cmd->command);
    	EXPECT_EQ(0, loaded_cmd->expected_retval);
    	Caller* caller_id = loaded_cmd->caller;
    	EXPECT_EQ(1159, caller_id->uid);
    	EXPECT_EQ(2076, caller_id->pid);
    	EXPECT_EQ(2194, caller_id->tid);
}

TEST(LoaderTest, LoadRmdirCall) {
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 2364 32311 (eclipse) rmdir 1318539134542480-46 /home/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images -1";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(RMDIR_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);
}

TEST(LoaderTest, LoadLstatCall) {
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 2076 2194 (gnome-do) lstat 1318539555812393-87 /usr/share/applications/gnome-sudoku.desktop 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(LSTAT_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2076, caller_id->pid);
    EXPECT_EQ(2194, caller_id->tid);
}

TEST(LoaderTest, LoadStatCall) {
    //syscall.stat
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 0 1163 1163 (cron) stat 1317750601526436-18178 /var/spool/cron/crontabs 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(STAT_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(1163, caller_id->pid);
    EXPECT_EQ(1163, caller_id->tid);
}

TEST(LoaderTest, LoadStatfsCall) {
    //syscall.statfs
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 2053 2053 (gnome-settings-) statfs 1318540136505344-287 /local/tracer/logs_nfs 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(STATFS_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2053, caller_id->pid);
    EXPECT_EQ(2053, caller_id->tid);
}

TEST(LoaderTest, LoadDupCall) {
    //syscall.dup
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 0 32544 32544 (sshd) dup 1318539601707575-31 4 5";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(DUP_OP, loaded_cmd->command);
    EXPECT_EQ(5, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(32544, caller_id->pid);
    EXPECT_EQ(32544, caller_id->tid);
}

TEST(LoaderTest, LoadFstatfsCall) {
    //syscall.fstatfs
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 0 32544 32544 (sshd) fstatfs 1318539601707575-31 4 -1";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(FSTATFS_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(32544, caller_id->pid);
    EXPECT_EQ(32544, caller_id->tid);
}

TEST(LoaderTest, LoadReaddirCall) {
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 2076 2194 (gnome-do) readdir 1318539555798359-27 /usr/share/applications/ 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(READDIR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2076, caller_id->pid);
    EXPECT_EQ(2194, caller_id->tid);
}

TEST(LoaderTest, LoadUnlinkCall) {
    //syscall.unlink
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images/1.png 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(UNLINK_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);
}

TEST(LoaderTest, LoadGetattrCall) {
    //getattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 0 1547 1547 (puppet) getattr 1318539062631232-30 /etc/puppet/puppet.conf 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(GETATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(1547, caller_id->pid);
    EXPECT_EQ(1547, caller_id->tid);
}

//FIXME test problems when reading file input
TEST(LoaderTest, LoadOpenCall) {
	//TODO: args
    //syscall.open
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 0 2097 2097 (udisks-daemon) open 1318539063003892-2505 /dev/sdb 34816 0 7";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(OPEN_OP, loaded_cmd->command);
    EXPECT_EQ(7, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(2097, caller_id->pid);
    EXPECT_EQ(2097, caller_id->tid);
}

TEST(LoaderTest, LoadDup2Call) {
	//syscall.dup2
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 0 32544 32544 (sshd) dup2 1318539601707761-41 4 0 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(DUP2_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(32544, caller_id->pid);
    EXPECT_EQ(32544, caller_id->tid);
}
TEST(LoaderTest, LoadDup3Call) {
	//syscall.dup3
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 0 32544 32544 (sshd) dup3 1318539601707761-41 4 0 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(DUP3_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(32544, caller_id->pid);
    EXPECT_EQ(32544, caller_id->tid);
}

TEST(LoaderTest, LoadWriteCall) {
	//syscall.write
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 0 6194 6194 (xprintidle) write 1318539063058255-131 /local/userActivityTracker/logs/tracker.log 1 17 17";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;

    EXPECT_EQ(WRITE_OP, loaded_cmd->command);
    EXPECT_EQ(17, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(6194, caller_id->pid);
    EXPECT_EQ(6194, caller_id->tid);
}

TEST(LoaderTest, LoadReadCall) {
	//syscall.read
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 114 1562 1562 (snmpd) read 1318539063447564-329 /proc/stat 8 3072 2971";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;

    EXPECT_EQ(READ_OP, loaded_cmd->command);
    EXPECT_EQ(2971, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(114, caller_id->uid);
    EXPECT_EQ(1562, caller_id->pid);
    EXPECT_EQ(1562, caller_id->tid);
}

TEST(LoaderTest, LoadLLseekCall) {
//syscall.llseek
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 2364 2364 (eclipse) llseek 1318539072857083-113 /local/thiagoepdc/eclipse/configuration/org.eclipse.core.runtime/.mainData.4 30 0 931001 SEEK_SET 931001";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(LLSEEK_OP, loaded_cmd->command);
    EXPECT_EQ(931001, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(2364, caller_id->tid);
}

TEST(LoaderTest, LoadMkdirCall) {
//syscall.mkdir
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /local/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images 511 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
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
}

TEST(LoaderTest, LoadMknodCall) {
//mknod
//TODO: we need to convert mode from string to a number type
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 11407 11407 (gconftool-2) mknod 1319207649254700-14 /home/thiagoepdc/orbit-thiagoepdc/linc-2c8f-0-69f0eff3e2d5 S_IFSOCK|S_IXOTH|S_IROTH|S_IXGRP|S_IRGRP|S_IRWXU 0 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(MKNOD_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(11407, caller_id->pid);
    EXPECT_EQ(11407, caller_id->tid);
}

TEST(LoaderTest, LoadSymlink) {
	//syscall.symlink
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 0 603 603 (update-rc.d) symlink 1318540206298997-36 /etc/rcS.d/../init.d/puppet /etc/rc0.d/K20puppet 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(SYMLINK_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(0, caller_id->uid);
    EXPECT_EQ(603, caller_id->pid);
    EXPECT_EQ(603, caller_id->tid);
}

TEST(LoaderTest, LoadReadlink) {
//syscall.readlink
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 2092 2092 (gvfs-gdu-volume) readlink 1318539355485686-40 /dev/scd0 3";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(READLINK_OP, loaded_cmd->command);
    EXPECT_EQ(3, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2092, caller_id->pid);
    EXPECT_EQ(2092, caller_id->tid);
}

//Note xattr calls will be called as fake
TEST(LoaderTest, LoadGetxattr) {
//getxattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 32362 32362 (ls) getxattr 1318539209608557-21 /tmp/0014b4e97285d -95";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(GETXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-95, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
}

TEST(LoaderTest, LoadRemovexattr) {
//syscall.removexattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 32362 32362 (ls) removexattr 1318539209608557-21 /tmp/0014b4e97285d 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(REMOVEXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
}

TEST(LoaderTest, LoadSetxattr) {
//syscall.setxattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 32362 32362 (ls) setxattr 1318539209608557-21 /tmp/0014b4e97285d -3";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(SETXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-3, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
}

TEST(LoaderTest, LoadListxattr) {
//syscall.listxattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 32362 32362 (ls) listxattr 1318539209608557-21 /tmp/0014b4e97285d 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(LISTXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
}

TEST(LoaderTest, LoadLremovexattr) {
//syscall.lremovexattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 32362 32362 (ls) lremovexattr 1318539209608557-21 /tmp/0014b4e97285d -1";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(LREMOVEXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
}

TEST(LoaderTest, LoadLlistxattr) {
//syscall.llistxattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 32362 32362 (ls) llistxattr 1318539209608557-21 /tmp/0014b4e97285d -1";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(LLISTXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
}

TEST(LoaderTest, LoadFgetxattr) {
//syscall.fgetxattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 32362 32362 (ls) fgetxattr 1318539209608557-21 /tmp/0014b4e97285d -1";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(FGETXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-1, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
}

TEST(LoaderTest, LoadFremovexattr) {
//syscall.fremovexattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 32362 32362 (ls) fremovexattr 1318539209608557-21 /tmp/0014b4e97285d 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(FREMOVEXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
}

TEST(LoaderTest, LoadFsetxattr) {
//syscall.fsetxattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 32362 32362 (ls) fsetxattr 1318539209608557-21 /tmp/0014b4e97285d -2";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(FSETXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(-2, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
}

TEST(LoaderTest, LoadFlistxattr) {
//syscall.flistxattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 32362 32362 (ls) flistxattr 1318539209608557-21 /tmp/0014b4e97285d 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;
    EXPECT_EQ(FLISTXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);
    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
}

TEST(LoaderTest, LoadLsetxattr) {
//syscall.lsetxattr
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);
	char line[] =
			"1 0 - 1 2 1159 32362 32362 (chmod) lsetxattr 1318539209608557-21 /tmp/0014b4e97285d teste 34 33 0";
	parse_element (element, line);

	EXPECT_EQ(1, element->id);
	EXPECT_EQ(0, element->n_parents);
	EXPECT_EQ(1, element->n_children);
	int child_id = element->children_ids[element->n_children - 1];
	EXPECT_EQ(2, child_id);
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	struct replay_command* loaded_cmd = element->command;

    EXPECT_EQ(LSETXATTR_OP, loaded_cmd->command);
    EXPECT_EQ(0, loaded_cmd->expected_retval);

    Caller* caller_id = loaded_cmd->caller;
    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(32362, caller_id->pid);
    EXPECT_EQ(32362, caller_id->tid);
}

TEST(ReplayTest, SingleOperationReplay) {

	//1 0 - 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images 511 0
	Replay_workload* rep_wld
		= (Replay_workload*) malloc (sizeof (Replay_workload));
	FILE * input_f = fopen("tests/replay_input/workflow_samples/workflow_single_command_mkdir", "r");
	load(rep_wld, input_f);

	Replay_result* actual_result = replay (rep_wld);

	EXPECT_EQ (2, actual_result->replayed_commands);//boostrap + 1
	EXPECT_EQ (2, actual_result->produced_commands);//boostrap + 1
	fclose(input_f);
}

//This method captures the bug of not replaying the
//tests/replay_input/workflow_samples/workflow_single_command_open (debug points
//out that its command type is NONE instead of OPEN
TEST(ReplayTest, SingleOpenOperationReplay) {

	Replay_workload* rep_wld
		= (Replay_workload*) malloc (sizeof (Replay_workload));

	FILE * input_f = fopen (
			"tests/replay_input/workflow_samples/workflow_single_command_open",
			"r");

	load (rep_wld, input_f);

	Replay_result* actual_result = replay (rep_wld);

	EXPECT_EQ (2, actual_result->replayed_commands);//boostrap + 1
	EXPECT_EQ (2, actual_result->produced_commands);//boostrap + 1
	fclose (input_f);
}

//This method try to capture the same bug report in the above method
TEST(LoaderTest, LoadWorkflowSingleOpenOperation) {
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen (
    		"tests/replay_input/workflow_samples/workflow_single_command_open",
    		"r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(2, rep_wld->num_cmds);//fake + 1
    EXPECT_EQ(0, rep_wld->current_cmd);

    //bootstraper
    Workflow_element* w_element = element(rep_wld, 0);
    EXPECT_EQ(0, w_element->id);
    EXPECT_EQ(1, w_element->n_children);
    EXPECT_EQ(0, w_element->n_parents);
    int child_id = w_element->children_ids[0];
    EXPECT_EQ(1, child_id);

    w_element = element(rep_wld, 1);
    EXPECT_EQ(1, w_element->id);
    EXPECT_EQ(0, w_element->n_children);
    EXPECT_EQ(1, w_element->n_parents);
    int parent_id = w_element->parents_ids[0];
    EXPECT_EQ(0, parent_id);

    struct replay_command* loaded_cmd = w_element->command;
	EXPECT_EQ(OPEN_OP, loaded_cmd->command);
    fclose(input_f);
}

//I have the felling that strtok is messing things up (in fact, doc said it
//does not work well with sub-routines). So, this test creates the same
//data structures loaded from workflow_2_sequencial_command_mkdir file
TEST(ReplayTest, 2_sequencial_command_mkdir_parsing_skipped) {

	//1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0
	//2 1 1 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-2 511 0
	Replay_workload* rep_wld
		= (Replay_workload*) malloc (sizeof (Replay_workload));

	fill_replay_workload (rep_wld);
	rep_wld->element_list
						= (Workflow_element*) malloc (3 * sizeof (Workflow_element));

	rep_wld->num_cmds = 3;

	//bootstrap
	struct replay_command* root_cmd
				= (struct replay_command*) malloc( sizeof (struct replay_command));
	fill_replay_command(root_cmd);
	root_cmd->command = NONE;

	Workflow_element* root_element = (rep_wld->element_list);
	fill_workflow_element(root_element);
	root_element->command = root_cmd;
	root_element->id = ROOT_ID;
	root_element->produced = 1;
	root_element->consumed = 1;

	root_element->n_children = 1;
	root_element->n_parents = 0;
	root_element->children_ids = (int*) malloc (sizeof (int));
	root_element->children_ids[0] = 1;

	//element 1
	Workflow_element* element_one = (rep_wld->element_list + 1);
	fill_workflow_element(element_one);

	struct replay_command* one_cmd
					= (struct replay_command*) malloc (sizeof (struct replay_command));
	fill_replay_command(one_cmd);
	one_cmd->command = MKDIR_OP;

	one_cmd->caller = (Caller*) malloc (sizeof (Caller));
	one_cmd->caller->uid = 1159;
	one_cmd->caller->pid = 2364;
	one_cmd->caller->tid = 32311;

	one_cmd->params = (Parms*) malloc (2 * sizeof (Parms));
	one_cmd->params[0].argm = NULL;
	one_cmd->params[0].argm = (arg*) malloc (sizeof (arg));
	one_cmd->params[0].argm->cprt_val = NULL;
	one_cmd->params[0].argm->cprt_val = (char*) malloc (MAX_FILE_NAME * sizeof (char));
	strcpy(one_cmd->params[0].argm->cprt_val, "/tmp/jdt-images-1");
	one_cmd->params[1].argm = NULL;
	one_cmd->params[1].argm = (arg*) malloc (sizeof (arg));
	one_cmd->params[1].argm->i_val = 511;

	one_cmd->expected_retval = 0;

	element_one->command = one_cmd;
	element_one->id = 1;
	element_one->produced = 0;
	element_one->consumed = 0;

	element_one->n_children = 1;
	element_one->n_parents = 1;
	element_one->children_ids = (int*) malloc (sizeof (int));
	element_one->children_ids[0] = 2;
	element_one->parents_ids = (int*) malloc (sizeof (int));
	element_one->parents_ids[0] = ROOT_ID;

	//element 1
	Workflow_element* element_two = (rep_wld->element_list + 2);
	fill_workflow_element(element_two);
	struct replay_command* cmd_two
					= (struct replay_command*) malloc( sizeof (struct replay_command));
	fill_replay_command(cmd_two);
	cmd_two->command = MKDIR_OP;

	cmd_two->caller = (Caller*) malloc(sizeof(Caller));
	cmd_two->caller->uid = 1159;
	cmd_two->caller->pid = 2364;
	cmd_two->caller->tid = 32311;

	cmd_two->params = (Parms*) malloc (2 * sizeof (Parms));
	cmd_two->params[0].argm = NULL;
	cmd_two->params[0].argm = (arg*) malloc (sizeof (arg));
	cmd_two->params[0].argm->cprt_val = NULL;
	cmd_two->params[0].argm->cprt_val = (char*) malloc (MAX_FILE_NAME * sizeof (char));
	strcpy(cmd_two->params[0].argm->cprt_val, "/tmp/jdt-images-2");
	cmd_two->params[1].argm = NULL;
	cmd_two->params[1].argm = (arg*) malloc (sizeof (arg));
	cmd_two->params[1].argm->i_val = 511;

	element_two->command = cmd_two;
	element_two->id = 2;
	element_two->produced = 0;
	element_two->consumed = 0;

	element_two->n_children = 0;
	element_two->n_parents = 1;
	element_two->parents_ids = (int*) malloc (sizeof (int));
	element_two->parents_ids[0] = 1;

	Replay_result* actual_result = replay (rep_wld);

	EXPECT_EQ (3, actual_result->replayed_commands);//boostrap + 2
	EXPECT_EQ (3, actual_result->produced_commands);//boostrap + 2
}

TEST(ReplayTest, 2_sequencial_command_mkdir) {

	//1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0
	//2 1 1 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-2 511 0
	Replay_workload* rep_wld
		= (Replay_workload*) malloc (sizeof (Replay_workload));
	FILE * input_f = fopen("tests/replay_input/workflow_samples/workflow_2_sequencial_command_mkdir", "r");
	load(rep_wld, input_f);

	Replay_result* actual_result = replay (rep_wld);

	EXPECT_EQ (3, actual_result->replayed_commands);//boostrap + 2
	EXPECT_EQ (3, actual_result->produced_commands);//boostrap + 2
	fclose(input_f);
}

//Wrote because our testing tool was saying that we are blocking on
//workflow_single_command_open
TEST(ReplayTest, sequencial_open_read_close_same_file) {

	//3
	//1 0 - 0 - 0 2097 2097 (udisks-daemon) open 1318539063003892-2505 workflow_samples/workflow_single_command_open 34816 0 7
	//2 1 3 1 1 0 2097 2097 (udisks-daemon) read 1318539063004000-329 workflow_samples/workflow_single_command_open 7 5 5
	//3 1 2 0 - 0 2097 2097 (udisks-daemon) close 1318539063006403-37 7 0
	Replay_workload* rep_wld
		= (Replay_workload*) malloc (sizeof (Replay_workload));
	FILE * input_f = fopen("tests/replay_input/workflow_samples/workflow_sequencial_open_read_close_same_file", "r");
	load(rep_wld, input_f);

	Replay_result* actual_result = replay (rep_wld);

	EXPECT_EQ (4, actual_result->replayed_commands);//boostrap + 3
	EXPECT_EQ (4, actual_result->produced_commands);//boostrap + 2
	fclose(input_f);
}

//Wrote because our testing tool was saying that we are blocking on
//workflow_9_seq__mkdir_and_an_independent
//This workflow pattern has two lines that have no parents (other than the fake
//boostrappper added after loading), probably we are not handling this two special
//lines correctly
TEST(ReplayTest, workflow_9_seq__mkdir_and_an_independent) {

/**
 *  10
	1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 0-0 /tmp/jdt-images-1 511 0
	2 1 1 1 3 1159 2364 32311 (eclipse) mkdir 1000000-0 /tmp/jdt-images-2 511 0
	3 1 2 1 4 1159 2364 32311 (eclipse) mkdir 1000000-0 /tmp/jdt-images-3 511 0
	4 1 3 1 5 1159 2364 32311 (eclipse) mkdir 1000000-0 /tmp/jdt-images-4 511 0
	5 0 - 0 - 1159 2364 32311 (eclipse) mkdir 1000000-0 /tmp/jdt-images-5 511 0
	6 1 5 1 7 1159 2364 32311 (eclipse) mkdir 1000000-0 /tmp/jdt-images-6 511 0
	7 1 6 1 8 1159 2364 32311 (eclipse) mkdir 1000000-0 /tmp/jdt-images-7 511 0
	8 1 7 1 9 1159 2364 32311 (eclipse) mkdir 1000000-0 /tmp/jdt-images-8 511 0
	9 1 8 1 10 1159 2364 32311 (eclipse) mkdir 1000000-0 /tmp/jdt-images-9 511 0
	10 1 9 1 11 1159 2364 32311 (eclipse) mkdir 1000000-0 /tmp/jdt-images-10 511
 */
	Replay_workload* rep_wld
		= (Replay_workload*) malloc (sizeof (Replay_workload));
	FILE * input_f = fopen("tests/replay_input/workflow_samples/workflow_9_seq__mkdir_and_an_independent", "r");
	load(rep_wld, input_f);

	Replay_result* actual_result = (Replay_result*) malloc (sizeof (Replay_result));
	actual_result->replayed_commands = 0;
	actual_result->produced_commands = 0;

	//Bootstrap children [1, 5]
	EXPECT_EQ(11, rep_wld->num_cmds);//boostrap + 1

	//bootstraper
	Workflow_element* w_element = element(rep_wld, 0);
	EXPECT_EQ(0, w_element->id);
	EXPECT_EQ(2, w_element->n_children);
	EXPECT_EQ(0, w_element->n_parents);
	int child_one = w_element->children_ids[0];
	EXPECT_EQ(1, child_one);
	int child_two = w_element->children_ids[1];
	EXPECT_EQ(5, child_two);

	fclose(input_f);
}

TEST(LoaderTest, ParseWorkflowElement) {
	//uid pid tid exec_name mkdir begin-elapsed fullpath mode return
	//1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0

	char line[] = "1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0";
	Workflow_element* element = alloc_workflow_element();
	EXPECT_EQ(0, element->consumed);
	EXPECT_EQ(0, element->produced);

	parse_element (element, line);
	//parse_element (element,
			//"1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0");

    EXPECT_EQ(1, element->id);

    EXPECT_EQ(0, element->n_parents);

    EXPECT_EQ(1, element->n_children);
    int child_id = element->children_ids[element->n_children - 1];
    EXPECT_EQ(2, child_id);

    EXPECT_EQ(0, element->consumed);
    EXPECT_EQ(0, element->produced);

    struct replay_command* loaded_cmd = element->command;

    EXPECT_EQ(MKDIR_OP, loaded_cmd->command);
    Caller* caller_id = loaded_cmd->caller;

    EXPECT_EQ(1159, caller_id->uid);
    EXPECT_EQ(2364, caller_id->pid);
    EXPECT_EQ(32311, caller_id->tid);

	Parms* parm = element->command->params;
	EXPECT_EQ(511, parm[1].argm->i_val);
	EXPECT_TRUE(strcmp("/tmp/jdt-images-1", parm[0].argm->cprt_val) == 0);

    EXPECT_EQ(0, loaded_cmd->expected_retval);
//2 1 1 1 3 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-2 511 0
}

TEST(LoaderTest, LoadWorkflow_2_sequencial_command_mkdir) {
			//uid pid tid exec_name mkdir begin-elapsed fulpath mode return
//1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0
//2 1 1 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-2 511 0
    Replay_workload* rep_wld = (Replay_workload*) malloc (sizeof (Replay_workload));
    FILE * input_f = fopen("tests/replay_input/workflow_samples/workflow_2_sequencial_command_mkdir", "r");
    int ret = load(rep_wld, input_f);

    EXPECT_EQ(0, ret);
    EXPECT_EQ(3, rep_wld->num_cmds);//fake + 2 commands
    EXPECT_EQ(0, rep_wld->current_cmd);

    //bootstraper
    Workflow_element* w_element = element(rep_wld, 0);
    EXPECT_EQ(0, w_element->id);
    EXPECT_EQ(1, w_element->n_children);
    EXPECT_EQ(0, w_element->n_parents);
    int child_id = w_element->children_ids[0];
    EXPECT_EQ(1, child_id);

    w_element = element(rep_wld, 1);
    EXPECT_EQ(1, w_element->id);
    EXPECT_EQ(1, w_element->n_children);
    EXPECT_EQ(1, w_element->n_parents);
    int parent_id = w_element->parents_ids[0];
    EXPECT_EQ(0, parent_id);
    child_id = w_element->children_ids[0];
    EXPECT_EQ(2, child_id);

    struct replay_command* loaded_cmd = w_element->command;

	EXPECT_EQ(MKDIR_OP, loaded_cmd->command);
	Caller* caller_id = loaded_cmd->caller;
	EXPECT_EQ(1159, caller_id->uid);
	EXPECT_EQ(2364, caller_id->pid);
	EXPECT_EQ(32311, caller_id->tid);
	Parms* parm = w_element->command->params;
	EXPECT_EQ(511, parm[1].argm->i_val);
	EXPECT_TRUE(strcmp("/tmp/jdt-images-1", parm[0].argm->cprt_val) == 0);
	EXPECT_EQ(0, loaded_cmd->expected_retval);
	EXPECT_EQ(MKDIR_OP, loaded_cmd->command);

    w_element = element(rep_wld, 2);
    EXPECT_EQ(2, w_element->id);
    EXPECT_EQ(0, w_element->n_children);
    EXPECT_EQ(1, w_element->n_parents);
    parent_id = w_element->parents_ids[0];
    EXPECT_EQ(1, parent_id);

    loaded_cmd = w_element->command;

	EXPECT_EQ(MKDIR_OP, loaded_cmd->command);
	caller_id = loaded_cmd->caller;
	EXPECT_EQ(1159, caller_id->uid);
	EXPECT_EQ(2364, caller_id->pid);
	EXPECT_EQ(32311, caller_id->tid);
	parm = w_element->command->params;
	EXPECT_EQ(511, parm[1].argm->i_val);
	EXPECT_TRUE(strcmp("/tmp/jdt-images-2", parm[0].argm->cprt_val) == 0);
	EXPECT_EQ(0, loaded_cmd->expected_retval);
	EXPECT_EQ(MKDIR_OP, loaded_cmd->command);

    fclose(input_f);
}
