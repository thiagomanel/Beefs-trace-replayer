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
#define CLOSE_OP        (NONE + 1)
#define MUNMAP_OP       (CLOSE_OP + 1)
#define FSTAT_OP	(MUNMAP_OP + 1)
#define RMDIR_OP	(FSTAT_OP + 1)
#define LSTAT_OP	(RMDIR_OP + 1)
#define STAT_OP		(LSTAT_OP + 1)
#define STATFS_OP	(STAT_OP + 1)
#define DUP_OP		(STATFS_OP + 1)
#define FSTATFS_OP	(DUP_OP + 1)
#define READDIR_OP	(FSTATFS_OP + 1)
#define UNLINK_OP	(READDIR_OP + 1)
#define GETATTR_OP	(UNLINK_OP + 1)
#define OPEN_OP		(GETATTR_OP + 1)
#define DUP2_OP		(OPEN_OP + 1)
#define DUP3_OP		(DUP2_OP + 1)
#define WRITE_OP	(DUP3_OP + 1)
#define READ_OP		(WRITE_OP + 1)
#define LLSEEK_OP	(READ_OP + 1)
#define MKDIR_OP	(LLSEEK_OP + 1)
#define MKNOD_OP	(MKDIR_OP + 1)
#define SYMLINK_OP	(MKNOD_OP + 1)
#define READLINK_OP	(SYMLINK_OP + 1)
#define GETXATTR_OP	(READLINK_OP + 1)
#define REMOVEXATTR_OP	(GETXATTR_OP + 1)
#define SETXATTR_OP	(REMOVEXATTR_OP + 1)
#define LISTXATTR_OP	(SETXATTR_OP + 1)
#define LREMOVEXATTR_OP	(LISTXATTR_OP + 1)
#define LLISTXATTR_OP	(LREMOVEXATTR_OP + 1)
#define FGETXATTR_OP	(LLISTXATTR_OP + 1)
#define FREMOVEXATTR_OP (FGETXATTR_OP + 1)
#define FSETXATTR_OP (FREMOVEXATTR_OP + 1)
#define FLISTXATTR_OP (FSETXATTR_OP + 1)
#define LSETXATTR_OP (FLISTXATTR_OP + 1)
#define PREAD_OP (LSETXATTR_OP + 1)
#define PWRITE_OP (PREAD_OP + 1)

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

    pthread_cond_t condition;
    pthread_mutex_t mutex;

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
void control_replay (struct replay* rpl, int additional_delay_usec);

#define IS_CONSUMED(element) ((element)->consumed)
#define IS_PRODUCED(element) ((element)->produced)

//a boxing function to get the replay result from a given element_id
#define RESULT(_replay, el_id) &(_replay->result->cmds_replay_result[el_id])

#endif /* _REPLAYER_H */
