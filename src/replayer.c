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
//FIXME: FD_MAX is a way to high. I doubt trace has a single pid so high.
//maybe pre-process trace to uncover the biggest possible value ?
#define FD_MAX 32768

#define BUFF_SIZE   20
#define DEBUG 1

#define REPLAY_SUCCESS 0

int N_ITEMS;

Replay_workload* workload;

/**
 * We cannot guarantee that a replayed call, e.g open, returns the same file
 * descriptor than when it was traced becaused the value of file descriptors
 * depends on operating system state.
 */
static int *pids_to_fd_pairs[PID_MAX];

void print_w_element (Workflow_element* element) {
	printf("w_element id=%d n_children=%d n_parent=%d produced=%d consumed=%d\n",
			element->id, element->n_children, element->n_parents, element->produced,
			element->consumed);
	int i;
	for (i = 0; i < element->n_children; i++) {
		printf ("child_i=%d id=%d\n", i, element->children_ids[i]);
	}

	for (i = 0; i < element->n_parents; i++) {
		printf ("parent_i=%d id=%d\n", i, element->parents_ids[i]);
	}
}

Workflow_element* alloc_workflow_element () {
	Workflow_element* element = (Workflow_element*) malloc (sizeof (Workflow_element));
	fill_workflow_element (element);
	return element;
}

void fill_workflow_element (Workflow_element* element) {

	element->n_children = 0;
	element->children_ids = NULL;

	element->n_parents = 0;
	element->parents_ids = NULL;

	element->produced = 0;
	element->consumed = 0;

	element->id = -1;
	element->command = NULL;
}

void fill_replay_workload (Replay_workload* r_workload) {

	//r_workload->cmd = NULL;
	r_workload->current_cmd = -1;
	r_workload->element_list = NULL;
	r_workload->num_cmds = 1;
}

Workflow_element* element (Replay_workload* workload, int element_id) {//FIXME: do we need this boxing method ?
	return &(workload->element_list[element_id]);
}

//FIXME: these 2 methods below share a lot
Workflow_element* get_child (Replay_workload* workload, Workflow_element* parent,
		int child_index) {

	int child_id = parent->children_ids[child_index];
    return element(workload, child_id);
}

Workflow_element* get_parent (Replay_workload* workload, Workflow_element* child,
		int parent_index) {

	int parent_id = child->parents_ids[parent_index];
	return element(workload, parent_id);
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

struct frontier {//we can use a generic list instead of this struct
	struct workflow_element* w_element;
	struct frontier* next;
};

void print_frontier (struct frontier* frontier) {

	printf("frontier_ptr=%p\n", frontier);
	if (frontier != NULL) {
		printf ("frontier->element=%p frontier->next=%p\n", frontier->w_element,
			frontier->next);
		print_w_element(frontier->w_element);
	}
}

typedef struct _sbuffs_t {

	Workflow_element* produced_queue[BUFF_SIZE];
	int last_produced;

	Workflow_element* consumed_queue[BUFF_SIZE];
	int last_consumed;

	int produced_count;
	int consumed_count;

	int total_commands;

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
//FIXME this code can set the frontier to null, do we want this (because of this,
//i had to modify _add method to malloc frontier when it is null
struct frontier* _del (struct frontier* current,
		Workflow_element* to_remove) {

	if (current == NULL) {
		return NULL;
	}

	if (current->w_element->id == to_remove->id) {
		struct frontier *next = current->next;
		//free(currP);TODO:
		return next;
	}

	current->next = _del(current->next, to_remove);
	return current;
}

void fill_frontier (struct frontier* new_frontier) {
	new_frontier->next = NULL;
	new_frontier->w_element = NULL;
}

//We can think these add and remove to be specific to the frontier
//or add one more indirection level and pass a frontier**
void frontier_append (Workflow_element* to_add) {

	if (shared_buff->frontier == NULL) {
		shared_buff->frontier
			= (struct frontier*) malloc (sizeof (struct frontier));
		fill_frontier (shared_buff->frontier);
		shared_buff->frontier->w_element = to_add;
	} else{
		struct frontier* tmp = shared_buff->frontier;
		while (tmp->next != NULL) {
			tmp = tmp->next;
		}

		tmp = (struct frontier*) malloc (sizeof (struct frontier));
		fill_frontier(tmp);
		tmp->w_element = to_add;
	}
}

int _contains (struct frontier* current, Workflow_element* tocheck) {

	struct frontier* tmp = current;

	while (tmp != NULL) {
		if (tmp->w_element->id == tocheck->id) {
			return 1;
		}
		tmp = tmp->next;
	}
	return 0;
}

int produced (Workflow_element* element) {//FIXME do we need this?
	return element->produced;
}

/**
 * Returns non-zero if all Workflow_element identified by the ids stored in
 * *element_ids were consumed (dispatched) or n_elements is zero
 */
int _consumed (int* elements_ids, int n_elements) {

	int i;
	int total_consumed = 0;

	for (i = 0; i < n_elements; i++) {
		Workflow_element* el = element(workload, elements_ids[i]);
		total_consumed += el->consumed;
	}

	return total_consumed == n_elements;
}

void mark_produced (Workflow_element* element) {
	element->produced = 1;
}

void mark_consumed (Workflow_element* element) {
	element->consumed = 1;
}

/**
 * Maps traced file descriptors to the real one returned during
 * replay for each pid registered in trace calls.
 */
int replayed_fd (int traced_pid, int traced_fd) {
	int* fds = pids_to_fd_pairs[traced_pid];
	return fds[traced_fd];
}

void map_fd (int traced_pid, int traced_fd, int replayed_fd) {

	if (!pids_to_fd_pairs[traced_pid]) {
		//TODO: create a fuction to allocate and memset this ?
		pids_to_fd_pairs[traced_pid] = (int*) malloc (FD_MAX * sizeof (int));
		memset (pids_to_fd_pairs[traced_pid], -1, FD_MAX * sizeof(int));
	}

	int* fd_pairs = pids_to_fd_pairs[traced_pid];
	fd_pairs[traced_fd] = replayed_fd;
}

int do_replay (struct replay_command* cmd) {

	assert (cmd != NULL);
	printf ("do_replay cmd_type=%d\n", cmd->command);
	Parms* args = cmd->params;

	switch (cmd->command) {
		case MKDIR_OP: {
			mkdir(args[0].argm->cprt_val, args[1].argm->i_val);
		}
		break;
		case STAT_OP: {
			struct stat sb;
			stat(args[0].argm->cprt_val, &sb);
		}
		break;
		case OPEN_OP: {
			int replayed_fd =
					open (args[0].argm->cprt_val, args[1].argm->i_val, args[2].argm->i_val);

			int traced_fd = cmd->expected_retval;
			map_fd (cmd->caller->pid, traced_fd, replayed_fd);
		}
		break;
		case READ_OP: {
			int traced_fd = args[1].argm->i_val;
			int repl_fd = replayed_fd (cmd->caller->pid, traced_fd);

			//FIXME should share a big bufer to avoid malloc'ing time wasting ?
			int read_count = args[2].argm->i_val;
			char* buf = (char*) malloc (sizeof (char) * read_count);
			read (repl_fd, buf, read_count);
		}
		break;
		case CLOSE_OP: {
			int traced_fd = args[0].argm->i_val;
			int repl_fd = replayed_fd (cmd->caller->pid, traced_fd);
			close (repl_fd);
			//FIXME should we set the fd mapping to something impossible as -1
			//i think i this way we do not mask programming errors
		}
		break;
		default:
			return -1;
	}

	return REPLAY_SUCCESS;
}

void do_produce(Workflow_element* el_to_produce) {

	//1. produce
	shared_buff->produced_queue[++shared_buff->last_produced] = el_to_produce;
	//2. mark
	mark_produced (el_to_produce);
	//3. increment count
	++shared_buff->produced_count;
}

void do_consume(Workflow_element* element) {

	if (do_replay (element->command) == REPLAY_SUCCESS) {
		shared_buff->consumed_queue[++shared_buff->last_consumed] = element;
		mark_consumed (element);
		++shared_buff->consumed_count;
	} else {
		fprintf (stderr, "Error on replaying command type=%d\n",
				element->command->command);
		exit (1);
	}
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

		sleep(1);//FIXME remove this later

		sem_wait(shared_buff->mutex);

			Workflow_element* consumed;

			//items come to the frontier after they have been consumed (dispatched)
			for (i = 0; i <= shared_buff->last_consumed; i++) {
				consumed = shared_buff->consumed_queue[i];
				int parent_i;
				for (parent_i = 0; parent_i < consumed->n_parents; parent_i++) {

					Workflow_element* parent
						= get_parent(workload, consumed, parent_i);

					//items left the frontier if its children were consumed (dispatched)
					int all_children_consumed =
							_consumed (parent->children_ids, parent->n_children);
					if ( all_children_consumed ) {
						shared_buff->frontier = _del (shared_buff->frontier, parent);
					}
				}

				if (! _contains (shared_buff->frontier, consumed)) {
					frontier_append (consumed);
				}
			}

			//cleaning consumed_queue
			shared_buff->last_consumed = -1;
		sem_post(shared_buff->mutex);
	}
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
					= shared_buff->produced_queue[shared_buff->last_produced];//take (i could move to a function)
				--shared_buff->last_produced;
				do_consume(cmd);
			}
		sem_post(shared_buff->mutex);

		sleep (1);
	}
}

void fill_shared_buffer (Replay_workload* workload, sbuffs_t* shared) {

	shared->mutex = (sem_t*) malloc (sizeof (sem_t));

	//bootstrap element is consumed and produced
	shared->produced_count = 1;
	shared->consumed_count = 1;

	shared->last_consumed = -1;
	shared->last_produced = -1;

	shared->total_commands = workload->num_cmds;

	shared->frontier = (struct frontier*) malloc (sizeof (struct frontier));

	//by construction, first element is the fake bootstrapper
	//FIXME: cannot call add ?
	shared->frontier->w_element = element(workload, ROOT_ID);
	shared->frontier->next = NULL;
}

int replay (Replay_workload* rep_workload, Replay_result* result) {

	assert (rep_workload != NULL);
	assert (result != NULL);
	assert (rep_workload->num_cmds >= 0);

	memset (pids_to_fd_pairs, 0, PID_MAX * sizeof (int*));

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
