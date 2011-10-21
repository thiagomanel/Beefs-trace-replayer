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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "loader.h"

int 
load (replay_workload* replay_wld, FILE* input_file)
{
  unsigned int line_len;
  int tmp;
  char* line;
  int loaded_commands = 0;
  replay_wld->cmd = (replay_command*) malloc (sizeof (replay_command));
  while (! feof (input_file))
    {
      line = NULL;
      line_len = 0; 		
      tmp = getline (&line, &line_len, input_file);
      if (tmp >= 0)
        {
	  tmp = parse_line (replay_wld->cmd, line);
	  if (tmp == 0)
            {
		loaded_commands += 1;
            }
	}
    }
  replay_wld->current_cmd = 0;
  replay_wld->num_cmds = loaded_commands;
  return 0;
}

int
parse_line (replay_command* cmd, char* line)
{
  cmd->command = CLOSE_OP;
  cmd->caller = (caller*) malloc (sizeof (caller));

  char* token = strtok (line, " ");
  cmd->caller->uid = atoi (token);
  token = strtok (NULL, " ");
  cmd->caller->pid = atoi (token);
  token = strtok (NULL, " ");
  cmd->caller->tid = atoi (token);

//  while (token != NULL)
  //  {
     // token = strtok (NULL, " ");
    //}
  cmd->caller->exec_name = "udisks-daemon";
  return 0;
}
