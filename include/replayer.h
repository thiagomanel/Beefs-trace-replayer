/*
* Copyright (c) 2004-2007 Erez Zadok
* Copyright (c) 2004-2007 Stony Brook University
* Copyright (c) 2004-2007 The Research Foundation of State University of New York
* Copyright (c) 2004-2007 Nikolai Joukov
*
* For specific licensing information, see the COPYING file distributed with
* this package, or get one from ftp://ftp.filesystems.org/pub/fist/COPYING.
*
* This Copyright notice must be kept intact and distributed with all
* fistgen sources INCLUDING sources generated by fistgen.
*/
#ifndef _REPLAYER_H
#define _REPLAYER_H

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

#define ROOT_ID 0

//TODO: timestamps
//TODO: actual returned value
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
	int expected_retval;
};

typedef struct workflow_element {

	struct replay_command* command;

	int n_children;
	int* children_ids;//we are going to hash w_elements

	int n_parents;
	int* parents_ids;//we are going to hash w_elements

	int produced;
	int consumed;
	int id;

} Workflow_element;

typedef struct replay_workload {
	Workflow_element* element_list;
	int num_cmds;
	int current_cmd;
} Replay_workload;

Workflow_element* alloc_workflow_element ();

void fill_replay_workload (Replay_workload* replay_workload);

void fill_workflow_element (Workflow_element* element);

Workflow_element* element (Replay_workload* workload, int element_id);

int is_child (Workflow_element* parent, Workflow_element* child);

/**
 * Replay result.
 * TODO: begin and end of each replayed call
 * TODO: actual return value
 */
typedef struct replay_result {
	int replayed_commands;
	int produced_commands;
} Replay_result;

void fill_replay_command (struct replay_command* cmd);

int replay (Replay_workload* rep_workload, Replay_result* result);

#endif /* _REPLAYER_H */
