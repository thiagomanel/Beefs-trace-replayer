/**
 * Copyright (C) 2008 Universidade Federal de Campina Grande
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
#ifndef _REPLAYER_H
#define _REPLAYER_H

#include "list.h"
#include <sys/types.h>

#define MAX_ARGS 5
#define PROC_NAME_LEN 256 //FIXME TOO BIG. search for exec name in task structs
#define MAX_FILE_NAME 256 //FIXME TOO BIG.

typedef unsigned short op_t;

#define NONE		0
#define CLOSE_OP        1
#define MUNMAP_OP       2
#define FSTAT_OP	3
#define RMDIR_OP	4
#define LSTAT_OP	5
#define STAT_OP		6
#define STATFS_OP	7
#define DUP_OP		8
#define FSTATFS_OP	9
#define READDIR_OP	10
#define UNLINK_OP	11
#define GETATTR_OP	12
#define OPEN_OP		13
#define DUP2_OP		14
#define DUP3_OP		15
#define WRITE_OP	16
#define READ_OP		17
#define LLSEEK_OP	18
#define MKDIR_OP	19
#define MKNOD_OP	20
#define SYMLINK_OP	21
#define READLINK_OP	22
#define GETXATTR_OP	23
#define REMOVEXATTR_OP	24
#define SETXATTR_OP	25
#define LISTXATTR_OP	26
#define LREMOVEXATTR_OP	27
#define LLISTXATTR_OP	28
#define FGETXATTR_OP	29
#define FREMOVEXATTR_OP 30
#define FSETXATTR_OP 	31
#define FLISTXATTR_OP 	32
#define LSETXATTR_OP 	33

#define NFSD_PROC_FSSTAT_OP	34
#define NFSD_PROC_SETATTR_OP	35
#define NFSD_PROC_GETATTR_OP	36
#define NFSD_PROC_LOOKUP_OP	37
#define NFSD_PROC_WRITE_OP	38
#define NFSD_PROC_READ_OP	39
#define NFSD_PROC_RENAME_OP	40
#define NFSD_PROC_REMOVE_OP	41
#define NFSD_PROC_RMDIR_OP	42
#define NFSD_PROC_LINK_OP	43
#define NFSD_PROC_SYMLINK_OP	44
#define NFSD_PROC_READLINK_OP	45
#define NFSD_PROC_READDIR_OP	46
#define NFSD_PROC_READDIRPLUS_OP	47
#define NFSD_PROC_ACCESS_OP	48
#define NFSD_PROC_MKNOD_OP	49
#define NFSD_PROC_MKDIR_OP	50
#define NFSD_PROC_CREAT_OP	51
#define NFSD_PROC_COMMIT_OP	52
#define NFSD_PROC_MKNOD_OP	53

//FIXME: it's ugly, it'd be better to have each replayer mode, syscall or nfsd,
//sṕecifying their own flags. Also, not there is no need to #define them.
//Anyway, I'll wait a refactor

#define ROOT_ID 0

#define PID_MAX 32768

//FIXME: FD_MAX is a way to high. I doubt trace has a single pid so high
//maybe pre-process trace to uncover the biggest possible value ?
#define FD_MAX 32768

//FIXME: find a value to this
#define SESSION_ID_MAX 32768

typedef struct _caller {
	int uid;
	int pid;
	int tid;
} Caller;

typedef union args {
    int i_val;
    long l_val;
    char* cprt_val;
} arg;

typedef struct _parms {
	arg* argm;
} Parms;

struct replay_command {

	op_t command;
	Caller* caller;
	Parms* params;

	double traced_begin;
	long traced_elapsed_time;

	int session_id;
	int expected_retval;
};

typedef struct workflow_element {

	struct replay_command* command;

	int n_children;
	int* children_ids;

	int n_parents;
	int* parents_ids;

	int produced;
	int consumed;
	int id;

	struct list_head frontier;
} Workflow_element;

typedef struct _command_replay_result {
	struct timeval *schedule_stamp;//when we scheduled the command
	struct timeval *dispatch_begin;
	struct timeval *dispatch_end;
	double delay;

	//These analysis is specially important for read/write to check
	//acessed number of bytes and for check returned errors codes.
	int expected_rvalue;
	int actual_rvalue;
	pid_t worker_id;
} command_replay_result ;

typedef struct replay_workload {
	Workflow_element* element_list;
	int num_cmds;
	int current_cmd;
} Replay_workload;

typedef struct replay_result {
	int replayed_commands;
	int produced_commands;
	command_replay_result* cmds_replay_result;
} Replay_result;

struct timing_policy {
	double (*delay) (struct replay*, Workflow_element*);
};

struct replay {

	/**
	 *  As we are a single process replayer, we need some magic to handle a
	 *  trace with multiple process. To make it clear, note that our trace
	 *  may have concurrent processes manipulating file descriptors of the
	 *  same value, since fd is a per-process variable.
	 *
	 *  We use two methods to manage file descriptors:
	 *
	 *  session_id - session_id in a unique number assigned to trace
	 *  	operations related to the same open-to-close sequence.
	 *  	*session_id_to_fd array is a {session_id:replayed_fd} mapping
	 *
	 * pids_to_fid - In replay time, we map and lookup pid to traced and
	 * 	replayed file descriptor tuples. Maps are made by open syscalls
	 * 	and remove by close syscalls.
	 *
	 * FIXME: convert conservative traces to use session_id too.
	 **/
	int session_enabled;
	int *session_id_to_fd;
	int **pids_to_fd_pairs;

	Replay_workload* workload;
	Replay_result* result;

	struct timing_policy timing_ops;
};

void workflow_element_init (Workflow_element* element);

Workflow_element* element (Replay_workload* workload, int element_id);
Workflow_element* parent (Replay_workload* workload, Workflow_element* child,
				int parent_index);

struct replay_command* replay_command_create (Caller* caller, op_t command, Parms* params,
			                       double traced_begin, long traced_elapsed_time,
                       				int expected_retval);

struct replay* create_replay (Replay_workload* workload);

#define REPLAY_SUCCESS 0

/**
* Execute syscall specified on replay_command pointed by cmd. If syscall executes
* properly, it returns REPLAY_SUCCESS or -1 otherwise. Executed syscall's
* returned value is copied to call_rvalue in case of REPLAY_SUCCESS.
*/
int exec (struct replay_command* to_exec, int *exec_rvalue, struct replay* rep);

void replay (struct replay* rpl);

//it seems a bit less ugly to pass this control parameters via a metadata struct
//instead of having two replay functions
void control_replay (struct replay* rpl, int num_workers, int additional_delay_usec);

#define IS_CONSUMED(element) ((element)->consumed)
#define IS_PRODUCED(element) ((element)->produced)

//a boxing function to get the replay result from a given element_id
#define RESULT(_replay, el_id) &(_replay->result->cmds_replay_result[el_id])

#endif /* _REPLAYER_H */

