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

/*
 * beefs_replayer.c
 *
 *  Created on: Dec 22, 2011
 *  Author: Thiago Emmanuel Pereira, thiago.manel@gmail.com
 */
#include "replayer.h"
#include "loader.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include </usr/include/semaphore.h>

int main (int argc, const char* argv[]) {
	/**
	FILE* fp = fopen (argv[1], "r");
	Replay_workload* rep_wld = (Replay_workload*) malloc (
			sizeof (Replay_workload));

	int ret = load (rep_wld, fp);
	if (ret < 0) {
		perror("Error loading trace\n");
	}
	Replay_result* actual_result = (Replay_result*) malloc( sizeof (Replay_result));
	replay (rep_wld, actual_result);
	return 0;*/

	Replay_workload* rep_wld
			= (Replay_workload*) malloc (sizeof (Replay_workload));

	//filling workload_element (TODO: it may be moved from this test to code)
	rep_wld->element = (Workflow_element*) malloc (sizeof (Workflow_element));
	rep_wld->element->n_children = 0;
	rep_wld->element->children = NULL;

	rep_wld->element->n_parents = 0;
	rep_wld->element->parents = NULL;

	rep_wld->element->produced = 0;
	rep_wld->element->consumed = 0;

	rep_wld->element->command
		= (struct replay_command*) malloc( sizeof (struct replay_command));

	fill_replay_command (rep_wld->element->command);
	//end workload_element filling

	rep_wld->element->command->params = (Parms*) malloc (3 * sizeof (Parms));

	Parms* parm;
	parm = rep_wld->element->command->params;
	parm[0].arg.cprt_val = (char*) malloc (MAX_FILE_NAME * sizeof (char));
	strcpy (parm[0].arg.cprt_val, "fileToOpen");
	parm[1].arg.i_val = 34816;//flag
	parm[2].arg.i_val = 0; //mode

	Replay_result* actual_result = (Replay_result*) malloc (sizeof (Replay_result));
	actual_result->replayed_commands = 0;
	actual_result->produced_commands = 0;

	replay (rep_wld, actual_result);
}
