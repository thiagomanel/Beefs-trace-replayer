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
#include <replayer.h>
#include <loader.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <hashtbl.h>

#define PID_MAX 32768
static int[PID_MAX][PID_MAX] pids;

fill_pids(int* pid_line)
  {
    for (int i = 0; i <= PID_MAX
  }

int
replay (replay_workload* rep_workload)
{
  for (int = 0 ; i <= PID_MAX ; i++)
    {
	pids[0] = NULL;
    }

  replay_command* cmd = rep_workload->cmd;
  while (cmd != NULL)
    {
      parms* args = cmd->params;
      switch(cmd->command)
        {
          case MKDIR_OP:
	    mkdir (args[0].arg.cprt_val, args[1].arg.i_val);
          break;
          case STAT_OP:
	    struct stat sb;
	    stat (args[0].arg.cprt_val, &sb);
	    break;
	  case OPEN_OP:
	    {
	      int op_fd = open (args[0].arg.cprt_val, args[1].arg.i_val, args[2].arg.i_val);
 	      int pid_from_trace = cmd->caller->pid;
	      for 
              pids[pid_from_trace] = 
              hashtbl_insert (hashtbl, args[0].arg.cprt_val, (void*) &op_fd);//It should removed at close FIXME:
	    }
	    break;
	  case READ_OP:
	    {
              char* buf = (char*) malloc (sizeof (char) *args[2].arg.i_val);
              int* fd = (int*) hashtbl_get (hashtbl, args[0].arg.cprt_val);
	      read(*fd, buf, args[2].arg.i_val);
	    }
          case WRITE_OP:
	    {
              char* buf = (char*) malloc (sizeof (char) *args[2].arg.i_val);
              int* fd = (int*) hashtbl_get (hashtbl, args[0].arg.cprt_val);
	      write(*fd, buf, args[2].arg.i_val);
	    }
	    break;
	  case CLOSE_OP:
	    {
              int* fd = (int*) hashtbl_get (hashtbl, args[0].arg.cprt_val);
	      close();
	    }
          default:
	    return -1;  	
	}
        cmd = cmd->next;
    } 
  return -1;
}

int
main (int argc, const char* argv[])
{
  FILE* fp = fopen(argv[1], "r");
  struct replay_workload* rep_wld = (replay_workload*) malloc (sizeof (replay_workload));
  int ret = load (rep_wld, fp);

  replay (rep_wld);
  if (ret < 0)
    {
	perror("Error loading trace\n");
    }
  return 0;
}
