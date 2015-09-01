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
#include "teka_timing.h"
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <sys/time.h>

static double teka_delay (struct replay* rep, Workflow_element* to_replay);

const struct timing_policy teka_policy_ops = {
    teka_delay,
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

static double delay_on_trace (struct replay_command* earlier,
                              struct replay_command* later)
{

    double earlier_end = earlier->traced_begin + earlier->traced_elapsed_time;
    double delay = (double) (later->traced_begin - earlier_end);
    if (delay < 0) {
        fprintf (stderr, "earlier->end=%f later->begin=%f.\n",
                 earlier_end, later->traced_begin);
    }
    return delay;
}

/**
 * This function returns the number of microseconds a thread needs to wait before
 * dispatching a command. It should wait to preserve the timing between itself
 * and its parents described on trace data.
 */
double teka_delay (struct replay* rep, Workflow_element* to_replay)
{
//FIXME what if I have two parents. I don't think it is possible in your data
//	but our workflow allows it
//FIXME what if I don't have a parent ?
    assert (rep != NULL);
    assert (to_replay != NULL);

    Workflow_element* _parent = parent (rep->workload, to_replay, 0);
    assert (IS_CONSUMED (_parent));

    double dlay_trace = delay_on_trace (_parent->command, to_replay->command);
    if (dlay_trace < 0)  {
        fprintf (stderr, "negative dlay to_replay_id=%d parent_id=%d\n",
                 to_replay->id, _parent->id);
        exit (1);
    }

    command_replay_result* cmd_result = RESULT (rep, to_replay->id);
    assert (cmd_result != NULL);
    command_replay_result* parent_result = RESULT (rep, _parent->id);
    assert (parent_result != NULL);

    //microseconds since the replay of parent
    gettimeofday (cmd_result->schedule_stamp, NULL);
    double elaps = elapsed (cmd_result->schedule_stamp,
                            parent_result->dispatch_end);
    //double elapsed = elapsed_since_replay (parent_cmd_result);
    return dlay_trace - elaps;
}
