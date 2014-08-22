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

void set_session_fd (int session_id, int repl_fd, struct replay* rpl) {
	rpl->session_id_to_fd[session_id] = repl_fd;
}

int session_fd (int session_id, struct replay* rpl) {
	return rpl->session_id_to_fd[session_id];
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
	int current_session_id = to_exec->session_id;

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
			if (rpl->session_enabled) {
				set_session_fd (current_session_id, replayed_fd, rpl);
			} else {
				int traced_fd = to_exec->expected_retval;
				if (traced_fd > 0) {
					map_fd (to_exec->caller->pid, traced_fd, replayed_fd, rpl->pids_to_fd_pairs);
				}
			}
		}
		break;
		case READ_OP: {
			int traced_fd = args[1].argm->i_val;
			int repl_fd =  (rpl->session_enabled) ?
						session_fd (current_session_id, rpl) :
						replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);

			//FIXME should share a big bufer to avoid malloc'ing time wasting ?
			int read_count = args[2].argm->i_val;
			char* buf = (char*) malloc (sizeof (char) * read_count);
			*exec_rvalue = read (repl_fd, buf, read_count);
		}
		break;
		case PREAD_OP: {
			//args": ["/local2/bigdata.dat", "22857", "4096", "902141250"]
			//ssize_t pread(int fd, void *buf, size_t count, off_t offset);
			int traced_fd = args[1].argm->i_val;
			int repl_fd =  (rpl->session_enabled) ?
						session_fd (current_session_id, rpl) :
						replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);

			//FIXME should share a big bufer to avoid malloc'ing time wasting ?
			int read_count = args[2].argm->i_val;
			char* buf = (char*) malloc (sizeof (char) * read_count);
			int offset = args[3].argm->i_val;
			*exec_rvalue = pread (repl_fd, buf, read_count, offset);
		}
		break;
		case PWRITE_OP: {
			int traced_fd = args[1].argm->i_val;
			int repl_fd =  (rpl->session_enabled) ?
						session_fd (current_session_id, rpl) :
						replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);

			//FIXME should share a big bufer to avoid malloc'ing time wasting ?
			int write_count = args[2].argm->i_val;
			char* buf = (char*) malloc (sizeof (char) * write_count);
			int offset = args[3].argm->i_val;
			*exec_rvalue = pwrite (repl_fd, buf, write_count, offset);
		}
		break;
		case WRITE_OP: {
			int traced_fd = args[1].argm->i_val;
			int repl_fd =  (rpl->session_enabled) ?
						session_fd (current_session_id, rpl) :
						replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);

			//FIXME should share a big bufer to avoid malloc'ing time wasting ?
			int write_count = args[2].argm->i_val;
			char* buf = (char*) malloc (sizeof (char) * write_count);
			*exec_rvalue = write (repl_fd, buf, write_count);
		}
		break;
		case CLOSE_OP: {
			int traced_fd = args[0].argm->i_val;
			int repl_fd =  (rpl->session_enabled) ?
						session_fd (current_session_id, rpl) :
						replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);

			*exec_rvalue = close (repl_fd);
			//FIXME should we set the fd mapping to something impossible as -1
			//i think i this way we do not mask programming errors
		}
		break;
		case FSTAT_OP: {
			struct stat sb;
			int traced_fd = args[1].argm->i_val;
			int repl_fd =  (rpl->session_enabled) ?
						session_fd (current_session_id, rpl) :
						replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);

			*exec_rvalue = fstat(repl_fd, &sb);
		}
		break;
		case RMDIR_OP: {
			*exec_rvalue = unlink (args[0].argm->cprt_val);
		}
		break;
		case LLSEEK_OP: {
			int traced_fd = args[1].argm->i_val;
			int repl_fd =  (rpl->session_enabled) ?
						session_fd (current_session_id, rpl) :
						replayed_fd (to_exec->caller->pid, traced_fd, rpl->pids_to_fd_pairs);

			long high = (long) args[2].argm->l_val;
			long low = (long) args[3].argm->l_val;
			off_t offset = (off_t) (high << 32) | low;
			int whence = args[3].argm->i_val;
			*exec_rvalue = lseek (repl_fd, offset, whence);
		}
		break;
		default:
			return -1;
	}

	return REPLAY_SUCCESS;
}
