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

static struct lookuptab {
	char *string;
	int code;
} tab[] = {
	{"close",	CLOSE_OP},
	{"munmap",	MUNMAP_OP},
	{"fstat",	FSTAT_OP},
	{"rmdir",	RMDIR_OP},
	{"lstat",	LSTAT_OP},
	{"stat",	STAT_OP},
	{"statfs",	STATFS_OP},
	{"dup",		DUP_OP},
	{"fstatfs",	FSTATFS_OP},
	{"readdir",	READDIR_OP},
	{"unlink",	UNLINK_OP},
	{"getattr",	GETATTR_OP},
	{"open",	OPEN_OP},
	{"dup2",	DUP2_OP},
	{"dup3",	DUP3_OP},
	{"write",	WRITE_OP},
	{"read",	READ_OP},
	{"llseek",	LLSEEK_OP},
};

int marker2operation (char *string)
{
  int i;
  for(i = 0; i < sizeof(tab) / sizeof(tab[0]); i++)
    if(strcmp(tab[i].string, string) == 0)
      return tab[i].code;
  return NONE;
}

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
	  loaded_commands += 1;
	}
    }
  replay_wld->current_cmd = 0;
  replay_wld->num_cmds = loaded_commands;
  return 0;
}

#define UNKNOW_OP_ERROR -2

int
parse_line (replay_command* cmd, char* line)
{
  cmd->caller = (caller*) malloc (sizeof (caller));
//ugly, eh !
  char* token = strtok (line, " ");
  cmd->caller->uid = atoi (token);
  token = strtok (NULL, " ");
  cmd->caller->pid = atoi (token);
  token = strtok (NULL, " ");
  cmd->caller->tid = atoi (token);

  token = strtok (NULL, " ");//exec_name
  token = strtok (NULL, " ");
  op_t loaded_cmd = marker2operation (token);
  int exp_rvalue;
  switch (loaded_cmd)
    {
      case OPEN_OP:
        token = strtok (NULL, " ");//timestamp
        token = strtok (NULL, " ");//fullpath
        token = strtok (NULL, " ");//flag
        token = strtok (NULL, " ");//mode
        token = strtok (NULL, " ");
        exp_rvalue = atoi (token);
      break;
      case DUP2_OP:
      case DUP3_OP:
        token = strtok (NULL, " ");//timestamp
        token = strtok (NULL, " ");//oldfd
        token = strtok (NULL, " ");//new_fd
        token = strtok (NULL, " ");
        exp_rvalue = atoi (token);
        break;
      case WRITE_OP:
      case READ_OP://TODO: write and read have the same token sequence than open
        token = strtok (NULL, " ");//timestamp
        token = strtok (NULL, " ");//fullpath
        token = strtok (NULL, " ");//fd
        token = strtok (NULL, " ");//count
        token = strtok (NULL, " ");
        exp_rvalue = atoi (token);
      break;
      case LLSEEK_OP://TODO: write and read have the same token sequence than open
        token = strtok (NULL, " ");//timestamp
        token = strtok (NULL, " ");//fullpath
        token = strtok (NULL, " ");//fd
        token = strtok (NULL, " ");//offset_high
        token = strtok (NULL, " ");//offset_low
        token = strtok (NULL, " ");//whence_str
        token = strtok (NULL, " ");
        exp_rvalue = atoi (token);
      break;
      default:
        token = strtok (NULL, " ");//timestamp
        token = strtok (NULL, " ");//arg
        token = strtok (NULL, " ");
        exp_rvalue = atoi (token);
    }
  cmd->command = loaded_cmd;
  cmd->expected_retval = exp_rvalue;
  return (loaded_cmd == NONE) ? UNKNOW_OP_ERROR : 0;
//free something ?
}
