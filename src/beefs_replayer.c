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
#include "conservative_timing.h"
#include "faster_timing.h"
#include "loader.h"
#include <stdlib.h>
#include <stdio.h>
#include <sys/time.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

int main (int argc, const char* argv[]) {

	int i;
	pid_t main_tid = syscall(SYS_gettid);
	command_replay_result *results, *tmp;
	char const *faster_police = "faster";
	char const *conservative_police = "conservative";

	if (argc < 3 || argc > 4) {
		perror("Wrong args. Usage: beefs_replayer $replay_input $timing_police [debug] \n");
		exit(1);
	}

	Replay_workload* workload = (Replay_workload*) malloc (sizeof (Replay_workload));
	workload->num_cmds = 0;
	workload->current_cmd = 0;
	workload->element_list = NULL;

	FILE* fp = fopen (argv[1], "r");
	int ret = load (workload, fp);
	if (ret < 0) {
		perror("Error loading trace\n");
		exit(1);
	}

	struct replay* repl = create_replay (workload);

	if (strcmp(argv[2], faster_police) == 0) {
		repl->timing_ops = faster_police_ops;
	} else if (strcmp(argv[2], conservative_police) == 0) {
		repl->timing_ops = conservative_police_ops;
	} else {
		perror("Error on timing police allowed: [faster, conservative])\n");
		exit(1);
	}

	fprintf (stderr, "main_tid=%d\n", main_tid);
	replay (repl);

	Replay_result *result = repl->result;
	results = result->cmds_replay_result;

	if (argc == 4) {
		if (strncmp (argv[3], "debug", 5) == 0) {
			for (i = 0; i < result->replayed_commands; i++) {
				tmp = &(results[i]);
				printf ("%ld %ld %ld %ld %f %d %d %d\n",
						tmp->dispatch_begin->tv_sec,
						tmp->dispatch_begin->tv_usec,
						tmp->dispatch_end->tv_sec,
						tmp->dispatch_end->tv_usec,
						tmp->delay,
						tmp->expected_rvalue,
						tmp->actual_rvalue,
						tmp->worker_id);
			}
		}
	}
}
