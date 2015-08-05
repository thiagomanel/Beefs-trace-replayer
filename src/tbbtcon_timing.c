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
#include "tbbtcon_timing.h"
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <sys/time.h>

static double tbbtcon_delay (struct replay* rep, Workflow_element* to_replay);

const struct timing_policy tbbtcon_policy_ops = {
    tbbtcon_delay,
};

static double elapsed (struct timeval *later, struct timeval *earlier)
{
    assert (later != NULL);
    assert (earlier != NULL);

    double us_elapsed = (later->tv_sec - earlier->tv_sec) * 1000000
                        + (later->tv_usec - earlier->tv_usec);

    assert (us_elapsed >= 0);
    return us_elapsed;
}

static double delay_on_trace (struct replay_command* earlier, struct replay_command* later)
{
//FIXME: duplicated code
    double delay = (double) (later->traced_begin - earlier->traced_begin);
    if (delay < 0) {
        fprintf (stderr, "earlier->begin=%f later->begin=%f.\n",
                 earlier->traced_begin, later->traced_begin);
    }
    return delay;
}

/**
 * This function returns the number of microseconds a thread needs to wait before
 * dispatching a command. It should wait to preserve the relative timing to the
 * trace beggining (as defined in the trace)
 */
double tbbtcon_delay (struct replay* rep, Workflow_element* to_replay)
{
    assert (rep != NULL);
    assert (to_replay != NULL);

    Workflow_element* first = element (rep->workload, 1);
    assert (first != NULL);
    double dlay_trace = delay_on_trace (first->command, to_replay->command);
    if (dlay_trace < 0)  {
        fprintf (stderr, "negative dlay to_replay_id=%d first_id=%d\n",
                 to_replay->id, first->id);
        exit (1);
    }

    command_replay_result* cmd_result = RESULT (rep, to_replay->id);
    assert (cmd_result != NULL);
    gettimeofday (cmd_result->schedule_stamp, NULL);

    command_replay_result *root_result = RESULT (rep, ROOT_ID);
    assert (root_result != NULL);
    double elaps = elapsed (cmd_result->schedule_stamp,
                            root_result->schedule_stamp);
    return dlay_trace - elaps;
}
