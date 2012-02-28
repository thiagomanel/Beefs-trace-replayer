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
#include <assert.h>

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

#define UNKNOW_OP_ERROR -2

void fill_replay_command (struct replay_command* cmd) {

	cmd->caller = NULL;
	cmd->command = NONE;
	cmd->expected_retval = -666; //:O
	cmd->params = NULL;
}

void parse_caller (Caller* caller, char* token) {

	token = strtok(NULL, " ");
	caller->uid = atoi(token);
	token = strtok(NULL, " ");
	caller->pid = atoi(token);
	token = strtok(NULL, " ");
	caller->tid = atoi(token);
}

Parms* alloc_and_parse_parms (op_t cmd_type,  char* token) {

	Parms* parm = NULL;

	switch (cmd_type) {
	case OPEN_OP:
		parm = (Parms*) malloc(3 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		parm[0].argm = (arg*) malloc (sizeof (arg));
		parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].argm->cprt_val, token);
		token = strtok(NULL, " "); //flag
		parm[1].argm = (arg*) malloc (sizeof (arg));
		parm[1].argm->i_val = atoi(token);
		token = strtok(NULL, " "); //mode
		parm[2].argm = (arg*) malloc (sizeof (arg));
		parm[2].argm->i_val = atoi(token);
		break;
	case DUP2_OP:
	case DUP3_OP:
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //oldfd
		token = strtok(NULL, " "); //new_fd
		break;
	case WRITE_OP:
	case READ_OP: //TODO: write and read have the same token sequence than open
		parm = (Parms*) malloc(3 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		parm[0].argm = (arg*) malloc (sizeof (arg));
		parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].argm->cprt_val, token);
		token = strtok(NULL, " "); //fd
		parm[1].argm = (arg*) malloc (sizeof (arg));
		parm[1].argm->i_val = atoi(token);
		token = strtok(NULL, " "); //count
		parm[2].argm = (arg*) malloc (sizeof (arg));
		parm[2].argm->i_val = atoi(token);
		break;
	case LLSEEK_OP: //TODO: write and read have the same token sequence than open
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		token = strtok(NULL, " "); //fd
		token = strtok(NULL, " "); //offset_high
		token = strtok(NULL, " "); //offset_low
		token = strtok(NULL, " "); //whence_str
		break;
	case MKDIR_OP:
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		parm[0].argm = (arg*) malloc (sizeof (arg));
		parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].argm->cprt_val, token);
		token = strtok(NULL, " "); //mode
		parm[1].argm = (arg*) malloc (sizeof (arg));
		parm[1].argm->i_val = atoi(token);
		break;
	case MKNOD_OP:
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		token = strtok(NULL, " "); //mode
		token = strtok(NULL, " "); //dev
		break;
	case SYMLINK_OP:
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath_old_name
		token = strtok(NULL, " "); //fullpath_new_name
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
		break;
	case LSETXATTR_OP:
		parm = (Parms*) malloc(2 * sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		token = strtok(NULL, " "); //name
		token = strtok(NULL, " "); //value
		token = strtok(NULL, " "); //flag
		break;
	case CLOSE_OP:
		parm = (Parms*) malloc(sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " ");
		parm[0].argm = (arg*) malloc (sizeof (arg));
		parm[0].argm->i_val = atoi(token); //fd
		break;
	case FSTAT_OP:
		parm = (Parms*) malloc(3 * sizeof(Parms));
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //fullpath
		parm[0].argm = (arg*) malloc (sizeof (arg));
		parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].argm->cprt_val, token);
		token = strtok(NULL, " "); //fd
		parm[1].argm = (arg*) malloc (sizeof (arg));
		parm[1].argm->i_val = atoi(token);
		break;
	default: //FIXME we need a case to NONE_OP, test it
		parm = (Parms*) malloc(sizeof(Parms)); //it should be done at each switch case
		token = strtok(NULL, " "); //timestamp
		token = strtok(NULL, " "); //arg
		parm[0].argm = (arg*) malloc (sizeof (arg));
		parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
		strcpy(parm[0].argm->cprt_val, token);
		break;
	}

	return parm;
}

int parse_element (Workflow_element* element, char* line) {
//1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0
	//ugly, eh !
	char* token = strtok (line, " ");
	element->id = atoi (token);

	token = strtok (NULL, " ");
	element->n_parents = atoi (token);

	if (element->n_parents < 1) {
		//consume special token "-". ugly. it seems better to have a double empty char
		token = strtok (NULL, " ");
	} else {
		element->parents_ids = (int*) malloc (element->n_parents * sizeof (int));
		int i;
		for (i = 0; i < element->n_parents ; i++) {
			token = strtok (NULL, " ");
			element->parents_ids[i] = atoi(token);
		}
	}

	token = strtok (NULL, " ");
	element->n_children = atoi (token);

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

	struct replay_command*
		current_command = (struct replay_command*)
			malloc (sizeof (struct replay_command));
	fill_replay_command (current_command);

	current_command->caller = (Caller*) malloc(sizeof(Caller));
	parse_caller (current_command->caller, token);

	token = strtok (NULL, " "); //exec_name

	token = strtok (NULL, " ");
	op_t loaded_cmd = marker2operation (token);
	current_command->command = loaded_cmd;

	current_command->params = alloc_and_parse_parms (loaded_cmd, token);

	token = strtok (NULL, " ");
	current_command->expected_retval = atoi (token);

	element->command = current_command;

	return (loaded_cmd == NONE) ? UNKNOW_OP_ERROR : 0;
//free something ?
}

/**
 * Increase array size by one element and add value_to_append to last position
 */
void append(int* array, int array_size, int value_to_append) {
	realloc (array, array_size + 1);
	array[array_size] = value_to_append;
}

//this function is used once, so I would not like to have it in header. I also
//think resizing arrays smells bad, it necessary to insert the bootstrap element.
void add_child (Replay_workload* workload, Workflow_element* parent,
		Workflow_element* child) {

	//assuming that is A is child of B, B is parent of A. So, everybody should
	//modify child/parent arrays using the available functions, never directly
	if (! is_child (parent, child)) {
		printf("really adding child\n");

		append (parent->children_ids, parent->n_children, child->id);
		parent->n_children++;

		append (child->parents_ids, child->n_parents, parent->id);
		child->n_parents++;
	}
}

/**
 * Collect who are the orphans
 *
 * @param int *orphans_ids_result - An malloc'ed array to store the orphans' ids.
 * 	It is ok to assume that we have enough space in this array.
 * @param Replay_workload* repl_wld - A pointer to the Replay_workload we are
 *	collecting the orphans
 *
 * @return the number of collected orphans
 */
int orphans (int *orphans_ids_result, Replay_workload* repl_wld)  {

	int i;
	int orphans_i = 0;
	for (i = 1; i < repl_wld->num_cmds; i++) {
		if ( element(repl_wld, i)->n_parents == 0 ) {
			orphans_ids_result[orphans_i++] = i;
		}
	}

	return orphans_i;
}

int load (Replay_workload* replay_wld, FILE* input_file) {

	size_t read_bytes = 0;
	size_t line_len = 0;
	char* line = NULL;
	int loaded_commands = 0;

	fill_replay_workload (replay_wld);

	if (input_file == NULL) {
		replay_wld->current_cmd = 0;
		replay_wld->num_cmds = 0;
		return NULL_FILE_OP_ERROR;
	}

	while ( (read_bytes = getline (&line, &line_len, input_file)) != -1 ) {

		if (replay_wld->element_list == NULL){//first line is the number of commands

			int num_commands_to_load = atoi (line);
			replay_wld->element_list
					= (Workflow_element*) malloc ((num_commands_to_load + 1)
													* sizeof (Workflow_element));

			//A fake element is the workflow root
			struct replay_command* root_cmd
				= (struct replay_command*) malloc( sizeof (struct replay_command));
			fill_replay_command(root_cmd);
			root_cmd->command = NONE;

			//fake element is also element_list's head
			Workflow_element* root_element = element(replay_wld, 0);
			fill_workflow_element(root_element);
			root_element->command = root_cmd;
			root_element->id = ROOT_ID;
			root_element->produced = 1;
			root_element->consumed = 1;

			++loaded_commands;

		} else {
			if (read_bytes >= 0) {

				Workflow_element* tmp_element
					= (replay_wld->element_list + loaded_commands);
				fill_workflow_element (tmp_element);
				parse_element (tmp_element, line);

				++loaded_commands;
			}
		}
	}

	replay_wld->current_cmd = 0;
	replay_wld->num_cmds = loaded_commands;

	if (loaded_commands > 1) {//ok, there is something to replay

		//child that has no parents should become child of fake element
		Workflow_element* root_element = element(replay_wld, 0);

		//we are wasting a lot of memory, but is make thinks easy
		int *orphans_ids = (int*) malloc (sizeof (int) * replay_wld->num_cmds);
		root_element->n_children = orphans (orphans_ids, replay_wld);

		assert (root_element->children_ids == NULL);
		root_element->children_ids =
				(int*) malloc (sizeof (int) * root_element->n_children);

		int i;
		for (i = 0; i < root_element->n_children ; i++) {
			//proud papa gets a new baby
			root_element->children_ids[i] = orphans_ids[i];

			//poor orphan baby gets a new papa
			Workflow_element *child = element (replay_wld,
												root_element->children_ids[i]);

			assert (! is_parent (root_element, child));
			assert (child->n_parents == 0);
			assert (child->parents_ids == NULL);

			child->parents_ids = (int*) malloc (sizeof(int));
			child->parents_ids[child->n_parents] = root_element->id;
			child->n_parents++;
		}

		free (orphans_ids);
	}

	free (line);

	return 0;
}
