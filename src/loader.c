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
#include "loader.h"
#include "replayer.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static struct lookuptab {
	char *string;
	int code;
} tab[] = {
	{"close",	CLOSE_OP},
	{"munmap",	MUNMAP_OP},
	{"fstat",	FSTAT_OP},
	{"rmdir",	RMDIR_OP},
	{"lstat",	LSTAT_OP},
	{"stat",	STAT_OP},
	{"statfs",	STATFS_OP},
	{"dup",		DUP_OP},
	{"fstatfs",	FSTATFS_OP},
	{"readdir",	READDIR_OP},
	{"unlink",	UNLINK_OP},
	{"getattr",	GETATTR_OP},
	{"open",	OPEN_OP},
	{"dup2",	DUP2_OP},
	{"dup3",	DUP3_OP},
	{"write",	WRITE_OP},
	{"read",	READ_OP},
	{"llseek",	LLSEEK_OP},
	{"mkdir",	MKDIR_OP},
	{"mknod",	MKNOD_OP},
	{"symlink",	SYMLINK_OP},
	{"readlink",	READLINK_OP},
	{"getxattr",	GETXATTR_OP},
	{"removexattr",	REMOVEXATTR_OP},
	{"setxattr",	SETXATTR_OP},
	{"listxattr",	LISTXATTR_OP},
	{"lremovexattr",LREMOVEXATTR_OP},
	{"llistxattr",	LLISTXATTR_OP},
	{"fgetxattr",	FGETXATTR_OP},
	{"fremovexattr",	FREMOVEXATTR_OP},
	{"fsetxattr",	FSETXATTR_OP},
	{"flistxattr",	FLISTXATTR_OP},
	{"lsetxattr",	LSETXATTR_OP},

};

int marker2operation(char *string) {
	int i;
	for (i = 0; i < sizeof(tab) / sizeof(tab[0]); i++)
		if (strcmp(tab[i].string, string) == 0)
			return tab[i].code;
	return NONE;
}

#define NULL_FILE_OP_ERROR -3

int load(Replay_workload* replay_wld, FILE* input_file) {
	unsigned int line_len;
	int tmp;
	char* line;
	int loaded_commands = 0;
	replay_wld->cmd = NULL;

	if (input_file == NULL) {
		replay_wld->current_cmd = 0;
		replay_wld->num_cmds = 0;
		return NULL_FILE_OP_ERROR;
	}

	while (!feof(input_file)) {
		line = NULL;
		line_len = 0;
		tmp = getline(&line, &line_len, input_file);
		if (tmp >= 0) {
			tmp = parse_line(&(replay_wld->cmd), line);
			loaded_commands += 1;
		}
	}
	replay_wld->current_cmd = 0;
	replay_wld->num_cmds = loaded_commands;
	return 0;
}

#define UNKNOW_OP_ERROR -2
void fill_replay_command (struct replay_command* cmd) {

	srand ( time(NULL) );

	cmd->command = NULL;
	cmd->caller = NULL;
	cmd->params = NULL;
	cmd->expected_retval = -666; //:O
	cmd->next = NULL;
	cmd->id = rand();
}


int parse_workflow_element (Workflow_element* element, char* line) {

}

void parse_caller2 (Caller* caller, char* token) {

	token = strtok(NULL, " ");
	caller->uid = atoi(token);
	token = strtok(NULL, " ");
	caller->pid = atoi(token);
	token = strtok(NULL, " ");
	caller->tid = atoi(token);
}

void parse_caller (Caller* caller, char* token) {

	caller = (Caller*) malloc(sizeof(Caller));

	printf("parse_caller %s\n", token);
	caller->uid = atoi(token);
	token = strtok(NULL, " ");
	printf("parse_caller %s\n", token);
	caller->pid = atoi(token);
	token = strtok(NULL, " ");
	printf("parse_caller %s\n", token);
	caller->tid = atoi(token);
}

void parse_parms (Parms* parm, op_t cmd_type,  char* token) {

	switch (cmd_type) {
	case OPEN_OP:
		parm = (Parms*) malloc(3 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		parm[0].arg.cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].arg.cprt_val, token);
		token = strtok(NULL, " "); //flag
		parm[1].arg.i_val = atoi(token);
		token = strtok(NULL, " "); //mode
		parm[2].arg.i_val = atoi(token);
		break;
	case DUP2_OP:
	case DUP3_OP:
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //oldfd
		token = strtok(NULL, " "); //new_fd
		token = strtok(NULL, " ");
		break;
	case WRITE_OP:
	case READ_OP: //TODO: write and read have the same token sequence than open
		parm = (Parms*) malloc(3 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		parm[0].arg.cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].arg.cprt_val, token);
		token = strtok(NULL, " "); //fd
		parm[1].arg.i_val = atoi(token);
		token = strtok(NULL, " "); //count
		parm[2].arg.i_val = atoi(token);
		token = strtok(NULL, " ");
		break;
	case LLSEEK_OP: //TODO: write and read have the same token sequence than open
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		token = strtok(NULL, " "); //fd
		token = strtok(NULL, " "); //offset_high
		token = strtok(NULL, " "); //offset_low
		token = strtok(NULL, " "); //whence_str
		token = strtok(NULL, " ");
		break;
	case MKDIR_OP:
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		parm[0].arg.cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].arg.cprt_val, token);
		token = strtok(NULL, " "); //mode
		parm[1].arg.i_val = atoi(token);
		token = strtok(NULL, " ");
		break;
	case MKNOD_OP:
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		token = strtok(NULL, " "); //mode
		token = strtok(NULL, " "); //dev
		token = strtok(NULL, " "); //
		break;
	case SYMLINK_OP:
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath_old_name
		token = strtok(NULL, " "); //fullpath_new_name
		token = strtok(NULL, " "); //
		break;
	case GETXATTR_OP:
	case REMOVEXATTR_OP:
	case SETXATTR_OP:
	case LISTXATTR_OP:
	case LREMOVEXATTR_OP:
	case LLISTXATTR_OP:
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		token = strtok(NULL, " "); //
		break;
	case LSETXATTR_OP:
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		token = strtok(NULL, " "); //name
		token = strtok(NULL, " "); //value
		token = strtok(NULL, " "); //flag
		token = strtok(NULL, " "); //
		break;
	case CLOSE_OP:
		parm = (Parms*) malloc(sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " ");
		parm[0].arg.i_val = atoi(token); //fd
		token = strtok(NULL, " ");
		break;
	default: //FIXME we need a case to NONE_OP, test it
		parm = (Parms*) malloc(sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //arg
		parm[0].arg.cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].arg.cprt_val, token);
		token = strtok(NULL, " ");
		break;
	}
}

int parse_element (Workflow_element* element, char* line) {
//1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0

	//ugly, eh !
	char* token = strtok (line, " ");
	element->id = atoi (token);

	token = strtok (NULL, " ");
	element->n_children = atoi (token);

	//consume special token "-". ugly. it seems better to have a double empty char
	if (element->n_children < 1) {
		token = strtok (NULL, " ");
	} else {
		element->children_ids = (int*) malloc (element->n_children * sizeof (int));
		int i;
		for (i = 0; i < element->n_children ; i++) {
			token = strtok (NULL, " ");
			element->children_ids[i] = atoi(token);
		}
	}

	token = strtok (NULL, " ");
	element->n_parents = atoi (token);
	if (element->n_parents < 1) {
		token = strtok (NULL, " ");
	} else {
		element->parents_ids = (int*) malloc (element->n_parents * sizeof (int));
		int i;
		for (i = 0; i < element->n_parents ; i++) {
			token = strtok (NULL, " ");
			element->parents_ids[i] = atoi(token);
		}
	}

	struct replay_command*
		current_command = (struct replay_command*) malloc (sizeof (struct replay_command));
	fill_replay_command (current_command);

	current_command->caller = (Caller*) malloc(sizeof(Caller));
	parse_caller2 (current_command->caller, token);

	token = strtok (NULL, " "); //exec_name

	token = strtok (NULL, " ");
	op_t loaded_cmd = marker2operation (token);
	current_command->command = loaded_cmd;

//	parse_parms (current_command->params, loaded_cmd, token);

	token = strtok (NULL, " ");
	current_command->expected_retval = atoi (token);

	element->command = current_command;

	return (loaded_cmd == NONE) ? UNKNOW_OP_ERROR : 0;
//free something ?
}

int parse_line(struct replay_command** cmd, char* line) {

	struct replay_command* current_command;
	struct replay_command* new_command;

	if ((*cmd) == NULL) {
		(*cmd) = (struct replay_command*) malloc(sizeof(struct replay_command));
		fill_replay_command((*cmd));
		current_command = (*cmd);
	} else {
		current_command = (*cmd);
		while (current_command->next != NULL) {
			current_command = current_command->next;
		}
		new_command = (struct replay_command*) malloc(sizeof(struct replay_command));
		fill_replay_command(new_command);
		current_command->next = new_command;
		current_command = current_command->next;
	}

	current_command->caller = (Caller*) malloc(sizeof(Caller));
	//ugly, eh !
	char* token = strtok(line, " ");
	current_command->caller->uid = atoi(token);
	token = strtok(NULL, " ");
	current_command->caller->pid = atoi(token);
	token = strtok(NULL, " ");
	current_command->caller->tid = atoi(token);

	token = strtok(NULL, " "); //exec_name
	token = strtok(NULL, " ");
	op_t loaded_cmd = marker2operation(token);
	int exp_rvalue;

	Parms* parm;

	switch (loaded_cmd) {
	case OPEN_OP:
		current_command->params = (Parms*) malloc(3 * sizeof(Parms)); //it should be done at each switch case
		parm = current_command->params;
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		parm[0].arg.cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].arg.cprt_val, token);
		token = strtok(NULL, " "); //flag
		parm[1].arg.i_val = atoi(token);
		token = strtok(NULL, " "); //mode
		parm[2].arg.i_val = atoi(token);
		token = strtok(NULL, " ");
		exp_rvalue = atoi(token);
		break;
	case DUP2_OP:
	case DUP3_OP:
		current_command->params = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //oldfd
		token = strtok(NULL, " "); //new_fd
		token = strtok(NULL, " ");
		exp_rvalue = atoi(token);
		break;
	case WRITE_OP:
	case READ_OP: //TODO: write and read have the same token sequence than open
		current_command->params = (Parms*) malloc(3 * sizeof(Parms)); //it should be done at each switch case
		parm = current_command->params;
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		parm[0].arg.cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].arg.cprt_val, token);
		token = strtok(NULL, " "); //fd
		parm[1].arg.i_val = atoi(token);
		token = strtok(NULL, " "); //count
		parm[2].arg.i_val = atoi(token);
		token = strtok(NULL, " ");
		exp_rvalue = atoi(token);
		break;
	case LLSEEK_OP: //TODO: write and read have the same token sequence than open
		current_command->params = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		token = strtok(NULL, " "); //fd
		token = strtok(NULL, " "); //offset_high
		token = strtok(NULL, " "); //offset_low
		token = strtok(NULL, " "); //whence_str
		token = strtok(NULL, " ");
		exp_rvalue = atoi(token);
		break;
	case MKDIR_OP:
		current_command->params = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		parm = current_command->params;
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		parm[0].arg.cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].arg.cprt_val, token);
		token = strtok(NULL, " "); //mode
		parm[1].arg.i_val = atoi(token);
		token = strtok(NULL, " ");
		exp_rvalue = atoi(token);
		break;
	case MKNOD_OP:
		current_command->params = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		token = strtok(NULL, " "); //mode
		token = strtok(NULL, " "); //dev
		token = strtok(NULL, " "); //
		exp_rvalue = atoi(token);
		break;
	case SYMLINK_OP:
		current_command->params = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath_old_name
		token = strtok(NULL, " "); //fullpath_new_name
		token = strtok(NULL, " "); //
		exp_rvalue = atoi(token);
		break;
	case GETXATTR_OP:
	case REMOVEXATTR_OP:
	case SETXATTR_OP:
	case LISTXATTR_OP:
	case LREMOVEXATTR_OP:
	case LLISTXATTR_OP:
		current_command->params = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		token = strtok(NULL, " "); //
		exp_rvalue = atoi(token);
		break;
	case LSETXATTR_OP:
		current_command->params = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		token = strtok(NULL, " "); //name
		token = strtok(NULL, " "); //value
		token = strtok(NULL, " "); //flag
		token = strtok(NULL, " "); //
		exp_rvalue = atoi(token);
		break;
	case CLOSE_OP:
		current_command->params = (Parms*) malloc(sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " ");
		parm = current_command->params;
		parm[0].arg.i_val = atoi(token); //fd
		token = strtok(NULL, " ");
		exp_rvalue = atoi(token);
		break;
	default: //FIXME we need a case to NONE_OP, test it
		current_command->params = (Parms*) malloc(sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //arg
		parm = current_command->params;
		parm[0].arg.cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].arg.cprt_val, token);
		token = strtok(NULL, " ");
		exp_rvalue = atoi(token);
		break;
	}
	current_command->command = loaded_cmd;
	current_command->expected_retval = exp_rvalue;
	return (loaded_cmd == NONE) ? UNKNOW_OP_ERROR : 0;
//free something ?
}

int load2(Replay_workload* replay_wld, FILE* input_file) {

	printf("aha\n");

	unsigned int line_len = 0;
	int tmp;
	char* line = NULL;
	int loaded_commands = 0;
	replay_wld->cmd = NULL;

	if (input_file == NULL) {
		replay_wld->current_cmd = 0;
		replay_wld->num_cmds = 0;
		return NULL_FILE_OP_ERROR;
	}

	//at least, one line -- the number of commands
	tmp = getline (&line, &line_len, input_file);
	int num_commands_to_load = atoi (line);
	replay_wld->element
		= (Workflow_element*) malloc (num_commands_to_load * sizeof (Workflow_element));

	Workflow_element* element = replay_wld->element;

	while (! feof (input_file)) {
		line = NULL;
		line_len = 0;
		tmp = getline (&line, &line_len, input_file);
		printf("line %s\n", line);

		if (tmp >= 0) {
			Workflow_element* tmp_element
				= (replay_wld->element + (loaded_commands * sizeof (Workflow_element)));
			fill_workflow_element (tmp_element);
			tmp = parse_element (tmp_element, line);
			loaded_commands += 1;
		}
	}

	replay_wld->current_cmd = 0;
	replay_wld->num_cmds = loaded_commands;
	return 0;
}
