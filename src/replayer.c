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
#include "replayer.h"
#include "loader.h"
#include <stdlib.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include </usr/include/semaphore.h>

#define PID_MAX 32768
#define BUFF_SIZE   20

int N_ITEMS;

struct dispatchable_command {
	struct workflow_element* w_element;
	struct replay_command* command;
	struct dispatchable_command* next;
};

void alloc_fd_array (int* pid_entry) {
	pid_entry = (int*) malloc (PID_MAX * sizeof(int));
	memset (pid_entry, -1, PID_MAX * sizeof(int));
}

typedef struct _sbuffs_t {

	Workflow_element* produced_queue[BUFF_SIZE];
	unsigned int produced_full;

	Workflow_element* consumed_queue[BUFF_SIZE];
	unsigned int consumed_full;

	unsigned int produced_count;
	unsigned int consumed_count;

	const unsigned int total_commands;

	struct dispatchable_command* frontier;

	sem_t sem_produced_full;
	sem_t sem_produced_empty;

	sem_t sem_consumed_full;
	sem_t sem_consumed_empty;

	sem_t mutex;

} sbuffs_t;

sbuffs_t* shared_buff = (sbuffs_t*) malloc( sizeof(sbuffs_t));

int all_produced (sbuffs_t* shared) {
	return (shared->produced_count >= shared->total_commands);
}

int all_consumed (sbuffs_t* shared) {
	return (shared->consumed_count >= shared->total_commands);
}

int hasCommandAvailableToDispatch (sbuffs_t* shared) {
	return shared->consumed_full > 0;
}

struct dispatchable_command*
_del (struct dispatchable_command* current, Workflow_element* to_remove) {

	if (current == NULL) {
		return NULL;
	}

	if (current->w_element->command->id == to_remove->command->id) {
		struct dispatchable_command *next = current->next;
		//free(currP);
		return next;
	}

	current->next = _del(current->next, to_remove);
	return current;
}

void
_add (struct dispatchable_command* current, Workflow_element* to_add) {

	struct dispatchable_command* tmp = current;
	while (tmp->next != NULL) {
		tmp = tmp->next;
	}

	tmp->next =
			(struct dispatchable_command*) malloc (sizeof (struct dispatchable_command));
	tmp->next->w_element = to_add;
}

int _contains (struct dispatchable_command* current, Workflow_element* tocheck) {

	int contains = 0;
	struct dispatchable_command* tmp = current;

	while (tmp != NULL) {
		if (tmp->command->id == tocheck->command->id) {
			break;
		}
		tmp = tmp->next;
	}
	return contains;
}

/**
 * It checks if all replay_command from commands array were produced
 */
int produced (Workflow_element* elements, int n_commands) {

	int i;
	int produced;

	for (i = 0; i < n_commands; i++) {
		Workflow_element element = *(elements + (i * sizeof (Workflow_element)));
		produced += element.produced;
	}

	return produced;
}

/**
 * It checks if all replay_command from commands array were dispatched
 */
int _consumed (Workflow_element* elements, int n_commands) {

	int i;
	int consumed;

	for (i = 0; i < n_commands; i++) {
		Workflow_element element = *(elements + (i * sizeof (Workflow_element)));
		consumed += element.consumed;
	}

	return consumed;
}

/**
 * Produce commands to be dispatched. Dispatching evolves according to a
 * dispatch frontier. Commands enter the frontier after they have
 * been consumed (dispatched) and they left the frontier when all of their children
 * come to frontier. A fake command acts as workflow's root to boostrap the frontier.
 */
void produce () {

	unsigned int i;

	struct dispatchable_command* current_dispatch_cmd;
	struct replay_command* current_replay_cmd;

	while ( ! all_produced (shared_buff)) {
		//FIXME: acquire lock
		while (current_dispatch_cmd != NULL) {
			//dispatch children that was not dispatched yet
			current_replay_cmd = current_dispatch_cmd->w_element->command;
			Workflow_element* children = current_dispatch_cmd->w_element->children;
			while (children != NULL) {
				if (! produced (children, current_dispatch_cmd->w_element->n_children)) {
					//1. produce
					//2. mark
					//3. increment count
					children = children->children;
				}
			}
			current_dispatch_cmd = current_dispatch_cmd->next;
		}
		//FIXME release lock
		//FIXME sleep ?? is it a good idea
		//FIXME acquire locks
		Workflow_element* consumed;
		Workflow_element* parent;

		//new items come to the frontier after they have been consumed (dispatched)
		for (i = 0; i <= shared_buff->consumed_full; i++)
			consumed = shared_buff->consumed_queue[i];
			parent = consumed->parents;

			while (parent != NULL) {
				//items left the frontier if its children were consumed (dispatched)
				if ( _consumed (parent->children, parent->n_children)) {
					_del (shared_buff->frontier, parent);
				}
			}
			if (! _contains (shared_buff->frontier, consumed)) {
				_add (shared_buff->frontier, consumed);
			}
	}
}

void do_consume(Workflow_element* cmd) {

}

void consume () {

	unsigned int i;
	//FIXME I will add locks after code the algorithm (don't trust tips concerning locks below)
	while ( ! all_consumed (shared_buff)) {
		/*
		 * 1.take a command C from produced queue
		 * 2.dispatch C
		 * 3.add C to consumed queue
		*/
		//acquire lock to shared
			if ( hasCommandAvailableToDispatch (shared_buff)) {

				Workflow_element* cmd
					= shared_buff->produced_queue[shared_buff->produced_full];
				--shared_buff->produced_full;

				do_consume(cmd);

				//acquire lock to consumed queue (beware of this nested acquire)
					shared_buff->consumed_queue[++shared_buff->consumed_full] = cmd;
				//release lock to consumed queue

			}
		//release lock to shared
	}
}

int replay (Replay_workload* rep_workload, Replay_result* result) {
	/**
	 * pids[pid_from_trace] = fd_pairs[] = {fd_pair_0, fd_pair_1, ...,fd_pair_n}
	 * fd_pairs[fd_from_trace] = fd_from_replay
	 */
	int *pids[PID_MAX];
	memset(pids, 0, PID_MAX * sizeof(int*)); //size arg is correct ??

	struct replay_command* cmd = rep_workload->cmd;
	while (cmd != NULL) {
		Parms* args = cmd->params;
		switch (cmd->command) {
		case MKDIR_OP:
			mkdir(args[0].arg.cprt_val, args[1].arg.i_val);
			break;
		case STAT_OP: {
			struct stat sb;
			stat(args[0].arg.cprt_val, &sb);
		}
			break;
		case OPEN_OP: {
			int fd_from_replay = open(args[0].arg.cprt_val, args[1].arg.i_val,
					args[2].arg.i_val);
			int pid_from_trace = cmd->caller->pid;

			if (!pids[pid_from_trace]) {
				//FIXME it is a way too big. maybe pre-process trace to uncover the biggest possible value
				pids[pid_from_trace] = (int*) malloc(PID_MAX * sizeof(int));
				alloc_fd_array(pids[pid_from_trace]);
			}
			int fd_from_trace = cmd->expected_retval;
			int* fds = pids[pid_from_trace];
			*(fds + fd_from_trace) = fd_from_replay;
		}
			break;
		case READ_OP: {
			int fd_from_trace = args[1].arg.i_val;
			int read_count = args[2].arg.i_val;

			int pid_from_trace = cmd->caller->pid;
			int* fds = pids[pid_from_trace];
			int replayed_fd = *(fds + fd_from_trace);

			//FIXME should be share a big bufer to avoid malloc_ing time wasting ?
			char* buf = (char*) malloc(sizeof(char) * read_count);
			read(replayed_fd, buf, read_count);
		}
			break;
		case WRITE_OP: {
			int fd_from_trace = args[1].arg.i_val;
			int write_count = args[2].arg.i_val;

			int pid_from_trace = cmd->caller->pid;
			int* fds = pids[pid_from_trace];
			int replayed_fd = *(fds + fd_from_trace);

			//FIXME should be share a big bufer to avoid malloc_ing time wasting ?
			char* buf = (char*) malloc(sizeof(char) * write_count);
			write(replayed_fd, buf, write_count);
		}
			break;
		case CLOSE_OP: {
			int fd_from_trace = args[0].arg.i_val;

			int pid_from_trace = cmd->caller->pid;
			int* fds = pids[pid_from_trace];
			int replayed_fd = *(fds + fd_from_trace);
			close(replayed_fd);
		}
			break;
		default:
			return -1;
		}
//		cmd = cmd->next;
	}
	return -1;
}

