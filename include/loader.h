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
#ifndef _LOADER_H
#define _LOADER_H

#include "replayer.h"
#include <stdio.h>

int
load (replay_workload* replay_wld, FILE* input_file);

int
parse_line (replay_command *cmd, char* line);

	 
#endif /* _LOADER_H */
