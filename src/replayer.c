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

static struct replay* __replay;
static int add_delay_usec = 0;

//FIXME to init
typedef struct thread_info {
    int trace_pid;
    int trace_tid;
} thread_info;

void workflow_element_init (Workflow_element* element)
{

    element->n_children = 0;
    element->children_ids = NULL;

    element->n_parents = 0;
    element->parents_ids = NULL;

    element->id = -1;
    element->command = NULL;
}

static Workflow_element* get_child (Workflow_element* parent, int child_index)
{
    int child_id = parent->children_ids[child_index];
    return element(__replay->workload, child_id);
}

/**
 * Returns non-zero if all Workflow_element identified by the ids stored in
 * *element_ids were consumed (dispatched) or n_elements is zero
 */
static int _consumed (int* elements_ids, int n_elements)
{

    int i;
    int total_consumed = 0;

    for (i = 0; i < n_elements; i++) {
        Workflow_element* el = element(__replay->workload, elements_ids[i]);
        total_consumed += el->consumed;
    }

    return total_consumed == n_elements;
}

static void mark_consumed (Workflow_element* element)
{
    element->consumed = 1;
}

static void fill_command_replay_result (command_replay_result *result)
{
    result->dispatch_begin = (struct timeval*) malloc (sizeof (struct timeval));
    result->dispatch_end = (struct timeval*) malloc (sizeof (struct timeval));
    result->schedule_stamp = (struct timeval*) malloc (sizeof (struct timeval));
}

static int belongs (Workflow_element* element, thread_info* t_info)
{
    return ( (t_info->trace_pid == element->command->caller->pid) &&
             (t_info->trace_tid == element->command->caller->tid));
}

static int do_consume (Workflow_element* element)
{

    int result;
    int actual_rvalue = 0;
    struct timespec sleep_t;

    command_replay_result *cmd_result = RESULT (__replay, element->id);
    fill_command_replay_result (cmd_result);
    double dlay = __replay->timing_ops.delay (__replay, element);
    if (dlay > 0) {
        if (dlay > 1000) {
            usleep (dlay + add_delay_usec);
        } else {
            sleep_t.tv_sec = 0;
            sleep_t.tv_nsec = (dlay * 1000) + (add_delay_usec * 1000);
            //one more hack it to sleep (dlay - sleep_delay)
            //FIXME: pass the rem field if case of receiving a interrupt
            nanosleep (&sleep_t, NULL);
        }
    }

    gettimeofday (cmd_result->dispatch_begin, NULL);
    result = exec (element->command, &actual_rvalue, __replay);

    //assigning actual syscall returning value. We do not check
    //REPLAY_SUCCESS because it will lead to program termination if it
    //does not succeded properly anyway

    //FIXME: We need to set expected rvalue
    cmd_result->actual_rvalue = actual_rvalue;
    gettimeofday (cmd_result->dispatch_end, NULL);

    //FIXME: debugging purposes, remove soon to avoid the
    //syscall overhead (or add a debug switch)
    cmd_result->worker_id = syscall(SYS_gettid);
    cmd_result->delay = dlay;

    return result;
}

void *consume (void *arg)
{

    int i, j, child_id;
    int result = -1;
    int total_cmds = __replay->workload->num_cmds;
    Workflow_element * child;

    thread_info* t_info = (thread_info*) arg;

    for (i = 1; i < total_cmds; i++) {

        Workflow_element* el = element (__replay->workload, i);

        if (belongs(el, t_info)) {
	    pthread_mutex_lock (&el->mutex);
	    while (! _consumed (el->parents_ids, el->n_parents)) {
		pthread_cond_wait (&el->condition, &el->mutex);
	    }

	    pthread_mutex_unlock (&el->mutex);
            result = do_consume(el);

            if (result == REPLAY_SUCCESS) {
                mark_consumed (el);
		for (j = 0; j < el->n_children; j++) {
		   child_id = el->children_ids[j];
		   child = element (__replay->workload, child_id);
		   //TODO: do we need to lock unlock the child mutex?
		   pthread_cond_signal (&child->condition);
		}
            } else {
                fprintf (stderr,
                         "Err replaying command workflow_id=%d type=%d\n",
                         el->id, el->command->command);
                exit (1);
            }
        }
    }
    return NULL;
}

static void fill_root ()
{

    //bootstrap element is consumed and produced
    //stamping root
    command_replay_result *root_result = RESULT (__replay, ROOT_ID);

    root_result->actual_rvalue = -666;
    root_result->delay = 0;

    fill_command_replay_result (root_result);
    gettimeofday (root_result->dispatch_begin, NULL);
    gettimeofday (root_result->dispatch_end, NULL);
    gettimeofday (root_result->schedule_stamp, NULL);
}

static void assign_expected_rvalue (command_replay_result *results, Replay_workload *wld)
{

    int i;
    for (i = 0; i < wld->num_cmds ; i++) {
        results[i].expected_rvalue
            = wld->element_list[i].command->expected_retval;
    }
}

struct replay* create_replay (Replay_workload* workload)
{

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
    repl->result->replayed_commands = 0;
    repl->result->cmds_replay_result = (command_replay_result*) malloc (
                                           sizeof (command_replay_result) * workload->num_cmds);
    assign_expected_rvalue (repl->result->cmds_replay_result, workload);

    return repl;
}

void replay (struct replay* rpl)
{
    control_replay (rpl, 0);
}

void control_replay (struct replay* rpl, int additional_delay_usec)
{

    int i,j,k;
    int pid;
    int tid;
    int num_workers;
    int** pids_map;

    assert (rpl != NULL);
    assert (rpl->workload != NULL);
    assert (rpl->result != NULL);

    __replay = rpl;
    add_delay_usec = additional_delay_usec;

    fill_root ();

    //a matrix with the pid-tid mapping
    num_workers = 0;
    pids_map = (int**) malloc (PID_MAX * sizeof (int*));
    memset (pids_map, 0, PID_MAX * sizeof (int*));

    Replay_workload* wld = __replay->workload;
    for (i = 1; i < wld->num_cmds; i++) {
        Workflow_element* el = element(__replay->workload, i);
        pid = el->command->caller->pid;
        tid = el->command->caller->tid;

        if (!pids_map[pid]) {
            pids_map[pid] = (int*) malloc (PID_MAX * sizeof (int));
            memset (pids_map[pid], 0, FD_MAX * sizeof(int));
        }
        int* tids = pids_map[pid];
        if (!tids[tid]) {
            tids[tid] = 1;
            ++num_workers;
        }
    }

    pthread_t *consumers = (pthread_t*) malloc (sizeof (pthread_t) * num_workers);
    thread_info* info = (thread_info*) malloc (sizeof (thread_info) * num_workers);

    k = 0;
    for (i = 0; i < PID_MAX; i++) {
        if (pids_map[i]) {
            for (j = 0; j < PID_MAX; j++) {
                if (pids_map[i][j]) {
                    info[k].trace_pid = i;
                    info[k].trace_tid = j;
                    pthread_create (&consumers[k], NULL, consume, (void *) &info[k]);
                    ++k;
                }
            }
        }
    }

    for (i = 0; i < num_workers; i++) {
        pthread_join(consumers[i], NULL);
    }

    __replay->result->produced_commands = __replay->workload->num_cmds;
    __replay->result->replayed_commands =__replay->workload->num_cmds;
}
