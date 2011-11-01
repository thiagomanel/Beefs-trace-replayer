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

int
replay (replay_workload* rep_workload)
{
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
	  case OPEN_OP:
	    printf("open %s\n", args[0].arg.cprt_val);
	    open (args[0].arg.cprt_val, args[1].arg.i_val, args[2].arg.i_val);
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
