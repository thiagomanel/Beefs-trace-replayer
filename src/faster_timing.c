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
#include "faster_timing.h"
#include <assert.h>
#include <stdlib.h>
#include <sys/time.h>

static double faster_delay (struct replay* rep, Workflow_element* to_replay);

const struct timing_policy faster_policy_ops = {
    faster_delay,
};

double faster_delay (struct replay* rep, Workflow_element* to_replay)
{

    assert (rep != NULL);
    assert (to_replay != NULL);

    command_replay_result* cmd_result = RESULT (rep, to_replay->id);
    assert (cmd_result != NULL);
    gettimeofday (cmd_result->schedule_stamp, NULL);
    return 0.0;
}
