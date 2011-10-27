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

int
replay (replay_workload* rep_workload)
{
  for (int i = 0; i < rep_workload->num_cmds; i++)
    {
      parms* args = rep_workload->cmd[i].params;
      switch(rep_workload->cmd[i].command)
        {
	  case MKNOD_OP:
            //#include <sys/types.h>#include <sys/stat.h>#include <fcntl.h>#include <unistd.h>
	    //int mknod(const char *pathname, mode_t mode, dev_t dev);  		
	    printf("mknod\n");
	    break;
          case MKDIR_OP:
	    //int mkdir(const char *pathname, mode_t mode);
	    printf("MKDIR\n");
	    mkdir(args[0].arg.cprt_val, args[1].arg.i_val);
            break;
          default:
	    return -1;  	
	}
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
