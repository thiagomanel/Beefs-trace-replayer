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
#include <pthread.h>
#include </usr/include/semaphore.h>
#include <assert.h>

#define PID_MAX 32768
#define BUFF_SIZE   20
#define DEBUG 1

int N_ITEMS;

Replay_workload* workload;

//TODO: do we need both two methods below
Workflow_element* alloc_workflow_element () {
	Workflow_element* element = (Workflow_element*) malloc (sizeof (Workflow_element));
	fill_workflow_element (element);
	return element;
}

void fill_workflow_element (Workflow_element* element) {
	element->n_children = 0;
	element->children = NULL;
	element->children_ids = NULL;

	element->n_parents = 0;
	element->parents = NULL;
	element->parents_ids = NULL;

	element->produced = 0;
	element->consumed = 0;

	element->command = NULL;
}


Workflow_element* element (Replay_workload* workload, int element_id) {
	if (DEBUG) printf("element element_id=%d\n", element_id);
	return (workload->element_list + (element_id * sizeof (Workflow_element)));
}


Workflow_element* get_child (Replay_workload* workload, Workflow_element* parent,
		int child_index) {

	int child_id = *(parent->children_ids + (child_index * sizeof (int)));
	return element(workload, child_id);
}

int is_child (Workflow_element* parent, Workflow_element* child) {
	int i;
	for (i = 0; i < parent->n_children; i++) {
		if (parent->children_ids[i] == child->id) {
			return 1;
		}
	}
	return 0;
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
	printf("adding child\n");
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

struct frontier {//we can use a generic list instead of this struct
	struct workflow_element* w_element;
	struct frontier* next;
};

void alloc_fd_array (int* pid_entry) {
	pid_entry = (int*) malloc (PID_MAX * sizeof(int));
	memset (pid_entry, -1, PID_MAX * sizeof(int));
}

typedef struct _sbuffs_t {

	Workflow_element* produced_queue[BUFF_SIZE];
	int last_produced;

	Workflow_element* consumed_queue[BUFF_SIZE];
	int last_consumed;

	unsigned int produced_count;
	unsigned int consumed_count;

	unsigned int total_commands;//TODO: should include the fake command into the account ?

	struct frontier* frontier;

	sem_t sem_produced_full;
	sem_t sem_produced_empty;

	sem_t sem_consumed_full;
	sem_t sem_consumed_empty;

	sem_t* mutex;

} sbuffs_t;

sbuffs_t* shared_buff = (sbuffs_t*) malloc( sizeof(sbuffs_t));

int all_produced (sbuffs_t* shared) {
	return (shared->produced_count >= shared->total_commands);
}

int all_consumed (sbuffs_t* shared) {
	return (shared->consumed_count >= shared->total_commands);
}

int has_commands_to_consume (sbuffs_t* shared) {
	return shared->last_produced >= 0;
}

//FIXME we can move this list method do an util list code outside replayer
struct frontier* _del (struct frontier* current,
		Workflow_element* to_remove) {

	if (current == NULL) {
		return NULL;
	}

	if (current->w_element->command->id == to_remove->command->id) {
		struct frontier *next = current->next;
		//free(currP);TODO:
		return next;
	}

	current->next = _del(current->next, to_remove);
	return current;
}

void _add (struct frontier* current, Workflow_element* to_add) {

	struct frontier* tmp = current;
	while (tmp->next != NULL) {
		tmp = tmp->next;
	}

	tmp->next =
			(struct frontier*) malloc (sizeof (struct frontier));
	tmp->next->w_element = to_add;
}

int _contains (struct frontier* current, Workflow_element* tocheck) {

	int contains = 0;
	struct frontier* tmp = current;

	while (tmp != NULL) {
		if (tmp->w_element->command->id == tocheck->command->id) {
			break;
		}
		tmp = tmp->next;
	}
	return contains;
}

int produced (Workflow_element* element) {
	return element->produced;
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

void mark_produced (Workflow_element* element) {
	element->produced = 1;
}

void do_produce(Workflow_element* el_to_produce) {

	if (DEBUG) printf("do_produce element_id=%d\n", el_to_produce);

	//1. produce
	shared_buff->produced_queue[++shared_buff->last_produced] = el_to_produce;
	//2. mark
	mark_produced (el_to_produce);
	//3. increment count
	++shared_buff->produced_count;
}

/**
 * Produce commands to be dispatched. Dispatching evolves according to a
 * dispatch frontier. Commands enter the frontier after they have
 * been consumed (dispatched) and they left the frontier when all of their children
 * come to frontier. A fake command acts as workflow's root to bootstrap the frontier.
 */
void *produce (void *arg) {

	int i;

	struct frontier* frontier;
	Workflow_element* w_element;

	//It seems the second part of this algorithm cannot be nested in this while
	//it is allowed to run even when all commands were produced
	while ( ! all_produced (shared_buff)) {
		sem_wait(shared_buff->mutex);
			frontier = shared_buff->frontier;
			while (frontier != NULL) {
				//dispatch children that was not dispatched yet
				w_element = frontier->w_element;
				int chl_index;
				for (chl_index = 0; chl_index < w_element->n_children; chl_index++) {
					Workflow_element*
						child = get_child (workload, w_element, chl_index);
					if (! produced (child)) {
						do_produce (child);
					}
				}
				frontier = frontier->next;
			}

		sem_post(shared_buff->mutex);

		sleep(1);

		//FIXME sleep ?? is it a good idea ?
		/**
		sem_wait(shared_buff->mutex);
			Workflow_element* consumed;
			Workflow_element* parent;

			//new items come to the frontier after they have been consumed (dispatched)
			for (i = 0; i <= shared_buff->last_consumed; i++) {
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
		sem_post(shared_buff->mutex);*/
	}
}

int do_replay (struct replay_command* cmd) {

	assert (cmd != NULL);

	Parms* args = cmd->params;

	switch (cmd->command) {
		case MKDIR_OP: {
			mkdir(args[0].arg.cprt_val, args[1].arg.i_val);
		}
		break;
		default:
			return -1;
	}
	return 0;
}

void do_consume(Workflow_element* element) {
	do_replay(element->command);
	++shared_buff->consumed_count;
}

void *consume (void *arg) {

	//FIXME I will add locks after code the algorithm
	//(don't trust tips concerning locks below)
	while ( ! all_consumed (shared_buff)) {
		/*
		 * 1.take a command C from produced queue
		 * 2.dispatch C
		 * 3.add C to consumed queue
		*/
		sem_wait(shared_buff->mutex);
			if ( has_commands_to_consume (shared_buff)) {
				Workflow_element* cmd
					= shared_buff->produced_queue[shared_buff->last_produced];
				--shared_buff->last_produced;
				do_consume(cmd);
				//acquire lock to consumed queue (beware of this nested acquire)
					shared_buff->consumed_queue[++shared_buff->last_consumed] = cmd;
				//release lock to consumed queue
			}
		sem_post(shared_buff->mutex);
	}
}

void fill_shared_buffer (Replay_workload* workload, sbuffs_t* shared) {

	shared->mutex = (sem_t*) malloc (sizeof (sem_t));

	shared->produced_count = 0;
	shared->consumed_count = 0;

	shared->last_consumed = -1;
	shared->last_produced = -1;

	shared->total_commands = workload->num_cmds;

	shared->frontier = (struct frontier*) malloc (sizeof (struct frontier));

	//by construction, first element is the fake bootstrapper
	shared->frontier->w_element = element(workload, ROOT_ID);
	shared->frontier->next = NULL;
}

int replay (Replay_workload* rep_workload, Replay_result* result) {

	assert (rep_workload != NULL);
	assert (result != NULL);
	assert (rep_workload->num_cmds >= 0);

	if (rep_workload->num_cmds > 0) {
		assert (rep_workload->element_list != NULL);
	}

	workload = rep_workload;
	fill_shared_buffer (workload, shared_buff);

	sem_init(shared_buff->mutex, 0, 1);

	pthread_t consumer, producer;
	pthread_create (&producer, NULL, produce, 0);
	pthread_create (&consumer, NULL, consume, 0);

	pthread_join(consumer, NULL);
	pthread_join(producer, NULL);

	result->produced_commands = shared_buff->produced_count;
	result->replayed_commands = shared_buff->consumed_count;
	return -1;
}

int old_replay (Replay_workload* rep_workload, Replay_result* result) {
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
