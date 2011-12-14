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
#include <replayer.h>
#include <loader.h>
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

	struct replay_command* command;
	struct dispatchable_command* next;
};

void alloc_fd_array (int* pid_entry) {
	pid_entry = (int*) malloc (PID_MAX * sizeof(int));
	memset (pid_entry, -1, PID_MAX * sizeof(int));
}

typedef struct _sbuffs_t {

	unsigned int produced_count;

	unsigned int produced_queue[BUFF_SIZE];
	unsigned int produced_empty;
	unsigned int produced_full;

	struct replay_command* consumed_queue[BUFF_SIZE];
	unsigned int consumed_empty;
	unsigned int consumed_full;

	unsigned int produced_count;
	const unsigned int total_commands;

	struct dispatchable_command* frontier;

	sem_t sem_produced_full;
	sem_t sem_produced_empty;

	sem_t sem_consumed_full;
	sem_t sem_consumed_empty;

	sem_t mutex;

} sbuffs_t;

int has_commands_to_produce (sbuffs_t* shared) {
	return shared->total_commands - shared->produced_count;
}

struct dispatchable_command*
_del (struct dispatchable_command* current, struct replay_command* to_remove) {

	if (current == NULL) {
		return NULL;
	}

	if (current->command->id == to_remove->id) {
		struct dispatchable_command *next = current->next;
		//free(currP);
		return next;
	}

	current->next = _del(current->next, to_remove);
	return current;
}

void _add (struct replay_command* collection, struct replay_command* element) { }

int _contains (struct replay_command* collection, struct replay_command* element) {
	return 0;
}

/**
 * It checks if all replay_command from commands array were produced
 */
int produced (struct replay_command* commands, int n_commands) {

	int i;
	int dispatched;

	for (i = 0; i < n_commands; i++) {
		struct replay_command* cmd = commands[ i * sizeof (struct replay_command)];
		dispatched += cmd->consumed;
	}

	return dispatched;
}

/**
 * It checks if all replay_command from commands array were dispatched
 */
int consumed (struct replay_command* commands, int n_commands) {

	int i;
	int dispatched;

	for (i = 0; i < n_commands; i++) {
		struct replay_command* cmd = commands[ i * sizeof (struct replay_command)];
		dispatched += cmd->consumed;
	}

	return dispatched;
}

/**
 * Produce commands to be dispatched. Dispatching evolves according to a
 * dispatch frontier. Commands enter the frontier after they have
 * been consumed (dispatched) and they left the frontier when all of their children
 * come to frontier. A fake command acts as workflow's root to boostrap the frontier.
 */
void produce () {

	unsigned int i;

	struct dispatchable_command current_d_cmd;
	struct replay_command* current_r_cmd;

	sbuffs_t* shared = (sbuffs_t*) malloc( sizeof(sbuffs_t));

	while (has_commands_to_produce (shared)) {

		//FIXME: acquire lock

		while (current_d_cmd != NULL) {
			/* dispatch children that was not dispatched yet*/
			current_r_cmd = current_d_cmd->command;
			struct replay_command* children = current_r_cmd->children;
			while (children != NULL) {
				if (! produced (children, current_r_cmd->n_children)) {
					//1. produce
					//2. mark
					//3. increment count
					children = children->children;
				}
			}
			current_d_cmd = current_d_cmd->next;
		}

		//FIXME release lock
		//FIXME sleep ?? is it a good idea
		//FIXME acquire locks

		struct replay_command* consumed;
		struct replay_command* parent;

		/* new items come to the frontier after they have been consumed (dispatched)  */
		for (i = 0; i < shared->consumed_empty; i++)
			consumed = shared->consumed_queue[i];
			/* items left the frontier if its children were consumed (dispatched) */
			parent = consumed->parents;
			while (parent != NULL) {
				if ( consumed (parent->children, parent->n_children)) {
					_del(shared->frontier, parent);
				}
			}
			if (! _contains (frontier, consumed)) {
				_add (frontier, consumed);
			}
	}
}

int replay (Replay_workload* rep_workload) {
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
		cmd = cmd->next;
	}
	return -1;
}

int main (int argc, const char* argv[]) {
	FILE* fp = fopen(argv[1], "r");
	Replay_workload* rep_wld = (Replay_workload*) malloc(
			sizeof(Replay_workload));

	int ret = load(rep_wld, fp);
	if (ret < 0) {
		perror("Error loading trace\n");
	}
	replay(rep_wld);
	return 0;
}
