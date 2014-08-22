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
#include "list.h"
#include <pthread.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <sys/time.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#define PID_MAX 32768

#define BUFF_SIZE   50000
#define DEBUG 1

static pthread_cond_t cmds_were_produced_cond = PTHREAD_COND_INITIALIZER;
static pthread_cond_t cmds_were_consumed_cond = PTHREAD_COND_INITIALIZER;

static pthread_mutex_t lock;
static struct replay* __replay;
static int add_delay_usec = 0;

void workflow_element_init (Workflow_element* element) {

	element->n_children = 0;
	element->children_ids = NULL;

	element->n_parents = 0;
	element->parents_ids = NULL;

	element->produced = 0;
	element->consumed = 0;

	element->id = -1;
	element->command = NULL;
}

//FIXME: these 2 methods below share a lot
static Workflow_element* get_child (Workflow_element* parent, int child_index) {
	int child_id = parent->children_ids[child_index];
    return element(__replay->workload, child_id);
}

struct frontier {//we can use a generic list instead of this struct
	struct workflow_element* w_element;
	struct frontier* next;
};

typedef struct _sbuffs_t {

	Workflow_element* produced_queue[BUFF_SIZE];
	int last_produced;

	Workflow_element* consumed_queue[BUFF_SIZE];
	int last_consumed;

	int produced_count;
	int consumed_count;

	int total_commands;

	struct frontier* frontier;
} sbuffs_t;

static sbuffs_t* shared_buff;

static int all_produced (sbuffs_t* shared) {
	return (shared->produced_count >= shared->total_commands);
}

static int all_consumed (sbuffs_t* shared) {
	return (shared->consumed_count >= shared->total_commands);
}

static int has_commands_to_consume (sbuffs_t* shared) {
	return shared->last_produced >= 0;
}

static int commands_were_consumed (sbuffs_t* shared) {
	return shared->last_consumed >= 0;
}

//FIXME we can move this list method do an util list code outside replayer
//FIXME this code can set the frontier to null, do we want this (because of this,
//i had to modify _add method to malloc frontier when it is null
static struct frontier* _del (struct frontier* current, Workflow_element* to_remove) {

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

static struct frontier* frontier_create() {
	struct frontier* newf = NULL;
        newf = (struct frontier*) malloc (sizeof (struct frontier));
	newf->next = NULL;
	newf->w_element = NULL;
	return newf;
}

//We can think these add and remove to be specific to the frontier
//or add one more indirection level and pass a frontier**
static void frontier_append (Workflow_element* to_add) {

	if (shared_buff->frontier == NULL) {
		shared_buff->frontier = frontier_create();
		shared_buff->frontier->w_element = to_add;
	} else {
		struct frontier* tmp = shared_buff->frontier;
		while (tmp->next != NULL) {
			tmp = tmp->next;
		}

		tmp->next = frontier_create();
		tmp->next->w_element = to_add;
	}
}

static int _contains (struct frontier* current, Workflow_element* tocheck) {

	struct frontier* tmp = current;

	while (tmp != NULL) {
		if (tmp->w_element->id == tocheck->id) {
			return 1;
		}
		tmp = tmp->next;
	}
	return 0;
}

/**
 * Returns non-zero if all Workflow_element identified by the ids stored in
 * *element_ids were consumed (dispatched) or n_elements is zero
 */
static int _consumed (int* elements_ids, int n_elements) {

	int i;
	int total_consumed = 0;

	for (i = 0; i < n_elements; i++) {
		Workflow_element* el = element(__replay->workload, elements_ids[i]);
		total_consumed += el->consumed;
	}

	return total_consumed == n_elements;
}

static void mark_produced (Workflow_element* element) {
	element->produced = 1;
}

static void mark_consumed (Workflow_element* element) {
	element->consumed = 1;
}

static void do_produce(Workflow_element* el_to_produce) {
	//1. produce
	shared_buff->produced_queue[++shared_buff->last_produced] = el_to_produce;
	//2. mark
	mark_produced (el_to_produce);
	//3. increment count
	++shared_buff->produced_count;
}

static void fill_command_replay_result (command_replay_result *result) {
	result->dispatch_begin = (struct timeval*) malloc (sizeof (struct timeval));
	result->dispatch_end = (struct timeval*) malloc (sizeof (struct timeval));
	result->schedule_stamp = (struct timeval*) malloc (sizeof (struct timeval));
}

static int produce_buffer_full() {
	return (shared_buff->last_produced + 1) >= BUFF_SIZE;
}

/**
 * Produce commands to be dispatched. Dispatching evolves according to a dispatch
 * frontier. Commands enter the frontier after they have been consumed (dispatched)
 * and they left the frontier when all of their children come to frontier. A fake
 * command acts as workflow's root to bootstrap the frontier.
 */
void *produce (void *arg) {
	//FIXME: maybe produce should not be a pthread stuff
	//FIXME: what if produce does not wait ?

	int i;

	struct frontier* frontier;
	Workflow_element* w_element;

	//It seems the second part of this algorithm cannot be nested in this while
	//it is allowed to run even when all commands were produced
	while ( ! all_produced (shared_buff)) {

		pthread_mutex_lock (&lock);

			frontier = shared_buff->frontier;
			while (frontier != NULL) {
		        //dispatch children that was not dispatched yet
				w_element = frontier->w_element;
				int chl_index;
				for (chl_index = 0;
					chl_index < w_element->n_children;
					chl_index++) {

					Workflow_element* child =
						get_child (w_element, chl_index);

					if (! IS_PRODUCED (child) &&
						_consumed (child->parents_ids,
								child->n_parents)) {

						if ( ! produce_buffer_full ()) {
							do_produce (child);
						}
					}
				}
				frontier = frontier->next;
			}

			if (has_commands_to_consume (shared_buff)) {
				pthread_cond_broadcast (&cmds_were_produced_cond);
			}

			if (commands_were_consumed(shared_buff)) {
				//items come to the frontier after
				//they have been consumed (dispatched)
				Workflow_element* consumed;
				for (i = 0; i <= shared_buff->last_consumed; i++) {

					consumed = shared_buff->consumed_queue[i];
					int parent_i;
					for (parent_i = 0;
						parent_i < consumed->n_parents;
						parent_i++) {

						Workflow_element* _parent =
							parent (__replay->workload,
								 consumed, parent_i);

						//items left the frontier if its children
						//were consumed (dispatched)
						int all_children_consumed =
							_consumed (_parent->children_ids,
									 _parent->n_children);
						if ( all_children_consumed ) {
							shared_buff->frontier =
								_del (shared_buff->frontier,
									 _parent);
						}
					}

					//FIXME I think items do not leave the frontier
					if (! _contains (shared_buff->frontier, consumed)) {
						frontier_append (consumed);
					}
				}
				//cleaning consumed_queue
				shared_buff->last_consumed = -1;
			} else {
				while ( ! commands_were_consumed(shared_buff)) {
					//SPURIOUS IF, docs says to use a while
					pthread_cond_wait (&cmds_were_consumed_cond,
								 &lock);
				}
			}

		pthread_mutex_unlock (&lock);
	}

	while ( ! all_consumed (shared_buff)) {
		//last chance to wake consumers up, how ugly it can be ?
		pthread_cond_broadcast (&cmds_were_produced_cond);
	}
	pthread_exit(NULL);
}

/**
 * Take a command from produced buffer
 */
static Workflow_element* take () {
	Workflow_element* cmd = shared_buff->produced_queue[shared_buff->last_produced];
	--shared_buff->last_produced;
	return cmd;
}

/**
 * 1.take a command C from produced queue
 * 2.dispatch C
 * 3.add C to consumed queue
 */
void *consume (void *arg) {

	int actual_rvalue = 0;
	struct timespec sleep_t;

	while (1) {

		pthread_mutex_lock (&lock);

		while (! has_commands_to_consume (shared_buff) &&
			! all_consumed (shared_buff)) {
			//if we use "if" we can get spurious behaviour
			pthread_cond_wait (&cmds_were_produced_cond, &lock);
		}

		if ( has_commands_to_consume (shared_buff)) {

			Workflow_element* element = take ();
			pthread_mutex_unlock (&lock);

			command_replay_result *cmd_result = RESULT (__replay, element->id);
			fill_command_replay_result (cmd_result);
			double dlay = __replay->timing_ops.delay (__replay, element);
			if (dlay > 0) {
				if (dlay > 1000) {
					usleep (dlay + add_delay_usec);
				} else {
					sleep_t.tv_sec = 0;
					sleep_t.tv_nsec = (dlay * 1000) +
							(add_delay_usec * 1000);
					//one more hack it to sleep (dlay - sleep_delay)
					//FIXME: pass the rem field if case of receiving a interrupt
					nanosleep (&sleep_t, NULL);
				}
			}

			gettimeofday (cmd_result->dispatch_begin, NULL);
			int result = exec (element->command, &actual_rvalue, __replay);

			//assigning actual syscall returning value. We do not check
			//REPLAY_SUCCESS because it will lead to program termination if it
			//does not succeded properly anyway

			//FIXME: We need to set expected rvalue
			cmd_result->actual_rvalue = actual_rvalue;
			gettimeofday (cmd_result->dispatch_end, NULL);

			//FIXME: debugging purposes, remove soon to avoid the
			//syscall overhead (or add a debug switch)
			cmd_result->worker_id = syscall(SYS_gettid);

			pthread_mutex_lock (&lock);

			if (result == REPLAY_SUCCESS) {
				shared_buff->consumed_queue[++shared_buff->last_consumed] = element;
				mark_consumed (element);
				++shared_buff->consumed_count;
			} else {
				fprintf (stderr,
					"Err replaying command workflow_id=%d type=%d\n",
					element->id, element->command->command);
				pthread_mutex_unlock (&lock);
				exit (1);
			}

			cmd_result->delay = dlay;

			pthread_cond_broadcast (&cmds_were_consumed_cond);
			pthread_mutex_unlock (&lock);

		} else if (all_consumed (shared_buff)) {
			pthread_mutex_unlock (&lock);
			pthread_exit(NULL);
		}
	}
}

static void fill_shared_buffer (Replay_workload* workload, sbuffs_t* shared) {

	//bootstrap element is consumed and produced
	shared->produced_count = 1;
	shared->consumed_count = 1;

	shared->last_consumed = -1;
	shared->last_produced = -1;

	shared->total_commands = workload->num_cmds;

	shared->frontier = (struct frontier*) malloc (sizeof (struct frontier));

	//FIXME: cannot call add ?
	shared->frontier->w_element = element(workload, ROOT_ID);
	shared->frontier->next = NULL;

	//stamping root
	command_replay_result *root_result = RESULT (__replay, ROOT_ID);

	root_result->actual_rvalue = -666;
	root_result->delay = 0;

	fill_command_replay_result (root_result);
	gettimeofday (root_result->dispatch_begin, NULL);
	gettimeofday (root_result->dispatch_end, NULL);
	gettimeofday (root_result->schedule_stamp, NULL);
}

static void assign_expected_rvalue (command_replay_result *results, Replay_workload *wld) {

	int i;
	for (i = 0; i < wld->num_cmds ; i++) {
		results[i].expected_rvalue
			= wld->element_list[i].command->expected_retval;
	}
}

struct replay* create_replay (Replay_workload* workload) {

	struct replay* repl = (struct replay*) malloc (sizeof (struct replay));
	repl->workload = workload;

	if (repl->workload->num_cmds > 0) {
		assert (repl->workload->element_list != NULL);
	}

	//it'd be a way simpler if we had a header line on trace input with
	//this kind of meta-information
	int sample_session_id = element (repl->workload, 1)->command->session_id;
	if (sample_session_id == -1) {
		repl->session_enabled = 0;
	} else {
		repl->session_enabled = 1;
	}

	//FIXME: I'll keep both, pids_to_fd and session_id, allocations. The plan
	//is to have just session_id in the future. Check replayer.h annotations
	repl->pids_to_fd_pairs = (int**) malloc (PID_MAX * sizeof (int*));
	memset (repl->pids_to_fd_pairs, 0, PID_MAX * sizeof (int*));

	repl->session_id_to_fd = (int*) malloc (SESSION_ID_MAX * sizeof (int));
	memset (repl->session_id_to_fd, -1, SESSION_ID_MAX * sizeof (int));

	repl->result = (Replay_result*) malloc (sizeof(Replay_result));
	repl->result->produced_commands = 0;
	repl->result->replayed_commands = 0;
	repl->result->cmds_replay_result = (command_replay_result*) malloc (
			sizeof (command_replay_result) * workload->num_cmds);
	assign_expected_rvalue (repl->result->cmds_replay_result, workload);

	return repl;
}

void replay (struct replay* rpl) {
	control_replay (rpl, 10, 0);
}

void control_replay (struct replay* rpl, int num_workers, int additional_delay_usec) {

	int i;
	assert (rpl != NULL);
	assert (rpl->workload != NULL);
	assert (rpl->result != NULL);

	__replay = rpl;
	add_delay_usec = additional_delay_usec;

        shared_buff = (sbuffs_t*) malloc( sizeof(sbuffs_t));
	fill_shared_buffer (__replay->workload, shared_buff);

	pthread_mutex_init (&lock, NULL);

	pthread_t producer;
	pthread_create (&producer, NULL, produce, 0);

	int max_consumers = num_workers;
	int num_consumers = (__replay->workload->num_cmds >= max_consumers)
				? max_consumers : __replay->workload->num_cmds;

	pthread_t *consumers = (pthread_t*) malloc (sizeof (pthread_t) * num_consumers);
	for (i = 0; i < num_consumers ; i++) {
		pthread_create (&consumers[i], NULL, consume, 0);
	}

	pthread_join(producer, NULL);

	__replay->result->produced_commands = shared_buff->produced_count;
	__replay->result->replayed_commands = shared_buff->consumed_count;
}
