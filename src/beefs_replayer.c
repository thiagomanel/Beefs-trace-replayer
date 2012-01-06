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

int main (int argc, const char* argv[]) {

	FILE* fp = fopen (argv[1], "r");
	Replay_workload* rep_wld = (Replay_workload*) malloc (
			sizeof (Replay_workload));

	int ret = load2 (rep_wld, fp);
	if (ret < 0) {
		perror("Error loading trace\n");
	}

	//loader.c is not using Workflow_elements yet, so we need to box them
	Replay_workload* boxed_rep_wld = (Replay_workload*) malloc (
				sizeof (Replay_workload));

	boxed_rep_wld->element = alloc_workflow_element();
	boxed_rep_wld->element->command = rep_wld->cmd;
	boxed_rep_wld->num_cmds = 1;

	Replay_result* actual_result = (Replay_result*) malloc (sizeof (Replay_result));
	actual_result->replayed_commands = 0;
	actual_result->produced_commands = 0;

	replay (boxed_rep_wld, actual_result);
}
