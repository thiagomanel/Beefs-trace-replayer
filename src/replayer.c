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

void alloc_fd_array (int* pid_entry) {
	pid_entry = (int*) malloc (PID_MAX * sizeof(int));
	memset (pid_entry, -1, PID_MAX * sizeof(int));
}

typedef struct _sbuffs_t {

	unsigned int produced_queue[BUFF_SIZE];
	unsigned int produced_empty;
	unsigned int produced_full;

	struct replay_command* consumed_queue[BUFF_SIZE];
	unsigned int consumed_empty;
	unsigned int consumed_full;

	unsigned int produced_count;
	const unsigned int total_commands;

	sem_t sem_produced_full;
	sem_t sem_produced_empty;

	sem_t sem_consumed_full;
	sem_t sem_consumed_empty;

	sem_t mutex;

} sbuffs_t;

typedef struct _producible_command {

	struct replay_command* command;
	unsigned int produced;
	unsigned int consumed;
} producible_command;

int has_commands_to_produce (int count, sbuffs_t* shared) {
	return shared->total_commands - count;
}

void _del (struct replay_command* collection, struct replay_command* element) { }

void _add (struct replay_command* collection, struct replay_command* element) { }

int _contains (struct replay_command* collection, struct replay_command* element) {
	return 0;
}

int command_was_produced (struct replay_command* command) {
	return 0;
}

int children_were_dispatched (struct replay_command* command) {
	return 0;
}

/**
 * Produce commands to be dispatched. Dispatching evolves according to a
 * dispatch frontier. Commands enter the frontier after they have
 * been consumed (dispatched) and they left the frontier when all of their children
 * come to frontier. A fake command acts as workflow's root to boostrap the frontier.
 */
void produce () {

	unsigned int i;
	int produce_count;

	struct replay_command* frontier;
	struct replay_command* current_frontier_cmd;
	sbuffs_t* shared = (sbuffs_t*) malloc( sizeof(sbuffs_t));

	while (has_commands_to_produce (produce_count, shared)) {

		//FIXME: acquire lock
		current_frontier_cmd = frontier;

		while (current_frontier_cmd != NULL) {

			/* dispatch children that was not dispatch yet*/
			struct replay_command* children = current_frontier_cmd->children;
			while (children != NULL) {
				if (! command_was_produced (children)) {

					//1. produce
					//2. mark
					//3. increment count

					children = children->children;
				}
			}
			current_frontier_cmd = current_frontier_cmd.next;
		}

		//FIXME release lock
		//FIXME sleep ?? is it a good idea
		//FIXME acquire locks

		struct replay_command* consumed;
		struct replay_command* parent;

		/* new items come to the frontier after they have been consumed (dispatched)  */
		for (i = 0; i < shared.consumed_empty; i++)
			consumed = shared.consumed_queue[i];
			parent = consumed->parents;
			/* items left the frontier if its children were consumed (dispatched) */
			while (parent != NULL) {
				if ( children_were_dispatched (parent)) {
					_del(frontier, parent);
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

			char* buf = (char*) malloc(sizeof(char) * read_count); //FIXME should be share a big bufer to avoid malloc_ing time wasting ?
			read(replayed_fd, buf, read_count);
		}
			break;
		case WRITE_OP: {
			int fd_from_trace = args[1].arg.i_val;
			int write_count = args[2].arg.i_val;

			int pid_from_trace = cmd->caller->pid;
			int* fds = pids[pid_from_trace];
			int replayed_fd = *(fds + fd_from_trace);

			char* buf = (char*) malloc(sizeof(char) * write_count); //FIXME should be share a big bufer to avoid malloc_ing time wasting ?
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
