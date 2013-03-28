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
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>
#include <assert.h>
#include <fcntl.h>
#include <string.h>
#include <stdio.h>

/*
* Maps traced file descriptors to the real one returned during
* replay for each pid registered in trace calls.
*/
int replayed_fd (int traced_pid, int traced_fd, int *pids_to_fd_pairs[]) {
	int* fds = pids_to_fd_pairs[traced_pid];
	return fds[traced_fd];
}

void map_fd (int traced_pid, int traced_fd, int replayed_fd, int *pids_to_fd_pairs[]) {

	if (!pids_to_fd_pairs[traced_pid]) {
		//TODO: create a function to allocate and memset this ?
		 pids_to_fd_pairs[traced_pid] = (int*) malloc (FD_MAX * sizeof (int));
		 memset (pids_to_fd_pairs[traced_pid], -1, FD_MAX * sizeof(int));
	}

	int* fd_pairs = pids_to_fd_pairs[traced_pid];
	fd_pairs[traced_fd] = replayed_fd;
}

//int exec (struct replay_command* to_exec, int *exec_rvalue, int *pids_to_fd_pairs[]) {
int exec (struct replay_command* to_exec, int *exec_rvalue, struct replay* rpl) {

	assert (to_exec != NULL);
	Parms* args = to_exec->params;

	switch (to_exec->command) {
		case MKDIR_OP: {
			*exec_rvalue = mkdir (args[0].argm->cprt_val, args[1].argm->i_val);
		}
		break;
		case STAT_OP: {
			struct stat sb;
			*exec_rvalue = stat(args[0].argm->cprt_val, &sb);
		}
		break;
		case OPEN_OP: {
			int replayed_fd =
					open (args[0].argm->cprt_val, args[1].argm->i_val, args[2].argm->i_val);

			*exec_rvalue = replayed_fd;
			int traced_fd = to_exec->expected_retval;
			//fprintf (stderr, "open-replayed_fd=%d traced_fd=%d traced_pid=%d\n", replayed_fd, traced_fd, to_exec->caller->pid);
			if (traced_fd > 0) {
				map_fd (to_exec->caller->pid, traced_fd, replayed_fd, rpl->pids_to_fd_pairs);
			}
		}
		break;
		case READ_OP: {
			int traced_fd = args[1].argm->i_val;
			int repl_fd = replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);

			//FIXME should share a big bufer to avoid malloc'ing time wasting ?
			int read_count = args[2].argm->i_val;
			char* buf = (char*) malloc (sizeof (char) * read_count);
			*exec_rvalue = read (repl_fd, buf, read_count);
		}
		break;
		case WRITE_OP: {
			int traced_fd = args[1].argm->i_val;
			int repl_fd = replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);

			//FIXME should share a big bufer to avoid malloc'ing time wasting ?
			int write_count = args[2].argm->i_val;
			char* buf = (char*) malloc (sizeof (char) * write_count);
			*exec_rvalue = write (repl_fd, buf, write_count);
		}
		break;
		case CLOSE_OP: {
			int traced_fd = args[0].argm->i_val;
			int repl_fd = replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);
			*exec_rvalue = close (repl_fd);
			//fprintf (stderr, "close-replayed_fd=%d traced_fd=%d traced_pid=%d\n", repl_fd, traced_fd, to_exec->caller->pid);
			//FIXME should we set the fd mapping to something impossible as -1
			//i think i this way we do not mask programming errors
		}
		break;
		case FSTAT_OP: {
			struct stat sb;
			int traced_fd = args[1].argm->i_val;
			int repl_fd = replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);
			*exec_rvalue = fstat(repl_fd, &sb);
			//fprintf (stderr, "fstat-replayed_fd=%d traced_fd=%d traced_pid=%d\n", repl_fd, traced_fd, to_exec->caller->pid);
		}
		break;
		case RMDIR_OP: {
			*exec_rvalue = unlink (args[0].argm->cprt_val);
		}
		break;
		case LLSEEK_OP: {
			int traced_fd = args[1].argm->i_val;
			int repl_fd = replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);

			off_t offset = (off_t) args[2].argm->l_val;
			int whence = args[3].argm->i_val;
			*exec_rvalue = lseek (repl_fd, offset, whence);
			//fprintf (stderr, "llseek-replayed_fd=%d traced_fd=%d traced_pid=%d\n", repl_fd, traced_fd, to_exec->caller->pid);
		}
		break;
		default:
			return -1;
	}

	return REPLAY_SUCCESS;
}
