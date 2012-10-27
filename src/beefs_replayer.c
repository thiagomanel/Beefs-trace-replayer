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
#include <sys/time.h>

int main (int argc, const char* argv[]) {

	int i;
	command_replay_result *results, *tmp;

	FILE* fp = fopen (argv[1], "r");
	Replay_workload* rep_wld = (Replay_workload*) malloc (
			sizeof (Replay_workload));

	int ret = load (rep_wld, fp);
	if (ret < 0) {
		perror("Error loading trace\n");
	}

	Replay_result *result = replay (rep_wld);
	results = result->cmds_replay_result;
        
	for (i = 0; i < result->replayed_commands; i++) {
		tmp = &(results[i]);
		printf ("%ld %ld %ld %ld %f %d %d\n",
				tmp->dispatch_begin->tv_sec,
				tmp->dispatch_begin->tv_usec,
				tmp->dispatch_end->tv_sec,
				tmp->dispatch_end->tv_usec,
				tmp->delay,
				tmp->expected_rvalue,
				tmp->actual_rvalue);
	}
}
