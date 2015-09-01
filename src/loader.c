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
#include "loader.h"
#include "replayer.h"
#include "list.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <assert.h>
#include <jansson.h>
#include <unistd.h>

static struct lookuptab {
    const char *string;
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
    {"mkdir",	MKDIR_OP},
    {"mknod",	MKNOD_OP},
    {"symlink",	SYMLINK_OP},
    {"readlink",	READLINK_OP},
    {"getxattr",	GETXATTR_OP},
    {"removexattr",	REMOVEXATTR_OP},
    {"setxattr",	SETXATTR_OP},
    {"listxattr",	LISTXATTR_OP},
    {"lremovexattr",LREMOVEXATTR_OP},
    {"llistxattr",	LLISTXATTR_OP},
    {"fgetxattr",	FGETXATTR_OP},
    {"fremovexattr",	FREMOVEXATTR_OP},
    {"fsetxattr",	FSETXATTR_OP},
    {"flistxattr",	FLISTXATTR_OP},
    {"lsetxattr",	LSETXATTR_OP},
    {"pread",	PREAD_OP},
    {"pwrite",	PWRITE_OP},

};

static struct lookupwhence {
    const char *string;
    int whence;
} whence_tab[] = {
    {"SEEK_CUR",	SEEK_CUR},
    {"SEEK_END",	SEEK_END},
    {"SEEK_SET",	SEEK_SET},
};

static int str2whence(const char *string)
{
    unsigned int i;
    for (i = 0; i < sizeof(whence_tab) / sizeof(whence_tab[0]); i++)
        if (strcmp(whence_tab[i].string, string) == 0)
            return whence_tab[i].whence;
    return -1;
}

static int marker2operation(const char *string)
{
    unsigned int i;
    for (i = 0; i < sizeof(tab) / sizeof(tab[0]); i++)
        if (strcmp(tab[i].string, string) == 0)
            return tab[i].code;
    return NONE;
}

struct replay_command*
replay_command_create(Caller* caller, op_t command, Parms* params,
                      double traced_begin, long traced_elapsed_time,
                      int expected_retval)
{

    struct replay_command* _new = (struct replay_command*)
                                  malloc (sizeof (struct replay_command));

    _new->caller = caller;
    _new->command = command;//NONE
    _new->expected_retval = expected_retval;
    _new->params = params;
    _new->traced_begin = traced_begin;
    _new->traced_elapsed_time = traced_elapsed_time;
    return _new;
}

struct replay_command* __replay_command_create()
{
    return replay_command_create(NULL, NONE, NULL, -666, -666, -666);
}

static Parms* alloc_and_parse_parms (op_t cmd_type,  json_t *replay_object)
{

    Parms* parm = NULL;
    json_t 	*args = json_object_get (replay_object, "args");
    if (!json_is_array (args)) {
        fprintf (stderr, "error: args is not an array\n");
        return parm;
    }

    switch (cmd_type) {
    case OPEN_OP: {
        parm = (Parms*) malloc(3 * sizeof(Parms));
        const char *fullpath = json_string_value (json_array_get (args, 0));
        parm[0].argm = (arg*) malloc (sizeof (arg));
        parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
        strcpy(parm[0].argm->cprt_val, fullpath);

        const char *flag = json_string_value (json_array_get (args, 1));
        parm[1].argm = (arg*) malloc (sizeof (arg));
        parm[1].argm->i_val = atoi(flag);

        const char *mode = json_string_value (json_array_get (args, 2));
        parm[2].argm = (arg*) malloc (sizeof (arg));
        parm[2].argm->i_val = atoi(mode);
    }
    break;
    case DUP2_OP:
    case DUP3_OP: {
        parm = (Parms*) malloc(2 * sizeof(Parms));
        json_string_value (json_array_get (args, 0));//oldfd
        json_string_value (json_array_get (args, 1));//newfd
    }
    break;
    case WRITE_OP:
    case READ_OP: {//TODO: write and read have the same token sequence than open
        parm = (Parms*) malloc(3 * sizeof(Parms));
        const char *fullpath = json_string_value (json_array_get (args, 0));
        parm[0].argm = (arg*) malloc (sizeof (arg));
        parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
        strcpy(parm[0].argm->cprt_val, fullpath);

        const char *fd = json_string_value (json_array_get (args, 1));
        parm[1].argm = (arg*) malloc (sizeof (arg));
        parm[1].argm->i_val = atoi(fd);

        const char *count = json_string_value (json_array_get (args, 2));
        parm[2].argm = (arg*) malloc (sizeof (arg));
        parm[2].argm->i_val = atoi(count);
    }
    break;
    case PWRITE_OP:
    case PREAD_OP: {
        parm = (Parms*) malloc(4 * sizeof(Parms));
        const char *fullpath = json_string_value (json_array_get (args, 0));
        parm[0].argm = (arg*) malloc (sizeof (arg));
        parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
        strcpy(parm[0].argm->cprt_val, fullpath);

        const char *fd = json_string_value (json_array_get (args, 1));
        parm[1].argm = (arg*) malloc (sizeof (arg));
        parm[1].argm->i_val = atoi(fd);

        const char *count = json_string_value (json_array_get (args, 2));
        parm[2].argm = (arg*) malloc (sizeof (arg));
        parm[2].argm->i_val = atoi(count);

        const char *offset = json_string_value (json_array_get (args, 3));
        parm[3].argm = (arg*) malloc (sizeof (arg));
        parm[3].argm->i_val = atoi(offset);
    }
    break;
    case LLSEEK_OP: {//TODO: write and read have the same token sequence than open
        parm = (Parms*) malloc (5 * sizeof (Parms));
        const char *fullpath = json_string_value (json_array_get (args, 0));
        parm[0].argm = (arg*) malloc (sizeof (arg));
        parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
        strcpy(parm[0].argm->cprt_val, fullpath);

        const char *fd = json_string_value (json_array_get (args, 1));
        parm[1].argm = (arg*) malloc (sizeof (arg));
        parm[1].argm->i_val = atoi(fd);

        unsigned long long offset_high = atol (json_string_value
                                               (json_array_get (args, 2)));
        unsigned long long offset_low = atol (json_string_value
                                              (json_array_get (args, 3)));

        unsigned long long off = (offset_high << 32) | offset_low;

        parm[2].argm = (arg*) malloc (sizeof (arg));
        parm[2].argm->l_val = off;

        const char *whence_str = json_string_value (json_array_get (args, 4));
        parm[3].argm = (arg*) malloc (sizeof (arg));
        parm[3].argm->i_val = str2whence(whence_str);
    }
    break;
    case MKDIR_OP: {
        parm = (Parms*) malloc(2 * sizeof(Parms));
        const char *fullpath = json_string_value (json_array_get (args, 0));
        parm[0].argm = (arg*) malloc (sizeof (arg));
        parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
        strcpy(parm[0].argm->cprt_val, fullpath);

        const char *mode = json_string_value (json_array_get (args, 1));
        parm[1].argm = (arg*) malloc (sizeof (arg));
        parm[1].argm->i_val = atoi(mode);
    }
    break;
    case MKNOD_OP: {
        parm = (Parms*) malloc(2 * sizeof(Parms));
        json_string_value (json_array_get (args, 0));//fullpath
        json_string_value (json_array_get (args, 1));//mode
        json_string_value (json_array_get (args, 2));//dev
    }
    break;
    case SYMLINK_OP: {
        parm = (Parms*) malloc(2 * sizeof(Parms));
        json_string_value (json_array_get (args, 0));//fullpath_oldname
        json_string_value (json_array_get (args, 1));//fullpath_newname
    }
    break;
    case GETXATTR_OP:
    case REMOVEXATTR_OP:
    case SETXATTR_OP:
    case LISTXATTR_OP:
    case LREMOVEXATTR_OP:
    case LLISTXATTR_OP: {
        parm = (Parms*) malloc(2 * sizeof(Parms));
        json_string_value (json_array_get (args, 0));//fullpath
    }
    break;
    case LSETXATTR_OP: {
        parm = (Parms*) malloc(2 * sizeof(Parms));
        json_string_value (json_array_get (args, 0));//fullpath
        json_string_value (json_array_get (args, 1));//name
        json_string_value (json_array_get (args, 2));//value
        json_string_value (json_array_get (args, 3));//flag
    }
    break;
    case CLOSE_OP: {
        parm = (Parms*) malloc(sizeof(Parms));
        const char *fd = json_string_value (json_array_get (args, 0));
        parm[0].argm = (arg*) malloc (sizeof (arg));
        parm[0].argm->i_val = atoi(fd);
    }
    break;
    case FSTAT_OP: {
        parm = (Parms*) malloc(3 * sizeof(Parms));
        const char *fullpath = json_string_value (json_array_get (args, 0));
        parm[0].argm = (arg*) malloc (sizeof (arg));
        parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
        strcpy(parm[0].argm->cprt_val, fullpath);

        const char *fd = json_string_value (json_array_get (args, 1));
        parm[1].argm = (arg*) malloc (sizeof (arg));
        parm[1].argm->i_val = atoi(fd);
    }
    break;
    default: {//FIXME we need a case to NONE_OP, test it
        parm = (Parms*) malloc(sizeof(Parms));
        const char *_arg = json_string_value (json_array_get (args, 0));
        parm[0].argm = (arg*) malloc (sizeof (arg));
        parm[0].argm->cprt_val = (char*) malloc(MAX_FILE_NAME * sizeof(char));
        strcpy(parm[0].argm->cprt_val, _arg);
    }
    break;
    }
    return parm;
}

static int fill_parents (Workflow_element *element, json_t *replay_object)
{

    int i;
    json_t *parents = json_object_get (replay_object, "parents");

    if (!json_is_array (parents)) {
        fprintf (stderr, "error: parents is not an array\n");
        return PARSING_ERROR;
    }

    element->n_parents = (int) json_array_size (parents);
    element->parents_ids = (element->n_parents > 0) ?
                           (int*) malloc (element->n_parents * sizeof (int))
                           : NULL;

    for (i = 0; i < element->n_parents; i++) {
        element->parents_ids[i] =
            (int) json_integer_value (json_array_get (parents, i));
    }
    return 0;
}

static int fill_children (Workflow_element *element, json_t *replay_object)
{

    int i;
    json_t *children = json_object_get (replay_object, "children");

    if (!json_is_array (children)) {
        fprintf (stderr, "error: children is not an array\n");
        return PARSING_ERROR;
    }
    element->n_children = (int) json_array_size (children);
    element->children_ids = (element->n_children > 0) ?
                            (int*) malloc (element->n_children * sizeof (int))
                            : NULL;

    for (i = 0; i < element->n_children; i++) {
        element->children_ids[i] =
            (int) json_integer_value (json_array_get (children, i));
    }
    return 0;
}

static Caller* fill_caller (struct replay_command *command, json_t *replay_object)
{

    Caller* caller = NULL;
    json_t *json_caller = json_object_get (replay_object, "caller");

    if (!json_is_object (json_caller)) {
        fprintf (stderr, "error: caller is not an object\n");
    }

    caller = (Caller*) malloc (sizeof(Caller));
    const char *tid_s = json_string_value (json_object_get (json_caller, "tid"));
    const char *pid_s = json_string_value (json_object_get (json_caller, "pid"));
    const char *uid_s = json_string_value (json_object_get (json_caller, "uid"));
    const char *exec = json_string_value (json_object_get (json_caller, "exec"));

    int tid = atoi(tid_s);
    int pid = atoi(pid_s);
    int uid = atoi(uid_s);

    caller->tid = tid;
    caller->pid = pid;
    caller->uid = uid;

    return caller;
}

static int fill_syscall (struct replay_command *cmd, json_t *replay_object)
{

    json_t *syscall = json_object_get (replay_object, "call");

    if (!json_is_string (syscall)) {
        fprintf (stderr, "error: syscall is not a string\n");
        return PARSING_ERROR;
    }
    const char *syscall_name = json_string_value (syscall);
    cmd->command = marker2operation (syscall_name);
    return 0;
}

static int fill_stamp (struct replay_command *cmd, json_t *replay_object)
{
//FIXME It failed silent when there is no "elapsed field"
    json_t *stamp = json_object_get (replay_object, "stamp");

    if (!json_is_object (stamp)) {
        fprintf (stderr, "error: stamp is not an object\n");
        return PARSING_ERROR;
    }
    cmd->traced_begin =
        (double) json_real_value (json_object_get (stamp, "begin")),
        cmd->traced_elapsed_time =
            (long) json_integer_value (json_object_get (stamp, "elapsed"));
    return 0;
}

static int fill_rvalue (struct replay_command *cmd, json_t *replay_object)
{

    json_t *rvalue = json_object_get (replay_object, "rvalue");
    if (!json_is_number (rvalue)) {
        fprintf (stderr, "error: rvalue is not a number\n");
        return PARSING_ERROR;
    }
    cmd->expected_retval = (int) json_integer_value(rvalue);
    return 0;
}

static int fill_session_id (struct replay_command *cmd, json_t *replay_object)
{

    json_t *rvalue = json_object_get (replay_object, "session_id");
    if (!json_is_number (rvalue)) {
        fprintf (stderr, "error: rvalue is not a number\n");
        return PARSING_ERROR;
    }
    cmd->session_id = (int) json_integer_value(rvalue);
    return 0;
}

static int fill_id (Workflow_element *element, json_t *replay_object)
{

    json_t *id = json_object_get (replay_object, "id");
    if (!json_is_number (id)) {
        fprintf (stderr, "error: id is not a number\n");
        return PARSING_ERROR;
    }
    element->id = json_integer_value (id);
    return 0;
}

/**
 * It parses a json replay object into a Workflow_element. Return 0 in case
 * of sucess, non-zero otherwise.
 */
static int parse_element (Workflow_element *element, json_t* replay_object)
{

    if (!json_is_object (replay_object)) {
        fprintf (stderr, "error: replay_call is not an object\n");
        return PARSING_ERROR;
    }

    if (fill_id (element, replay_object) == PARSING_ERROR) {
        return PARSING_ERROR;
    }

    if (fill_parents (element, replay_object) == PARSING_ERROR) {
        return PARSING_ERROR;
    }

    if (fill_children (element, replay_object) == PARSING_ERROR) {
        return PARSING_ERROR;
    }

    element->command->caller = fill_caller (element->command, replay_object);

    if (fill_syscall (element->command, replay_object) == PARSING_ERROR) {
        return PARSING_ERROR;
    }

    if (fill_stamp (element->command, replay_object) == PARSING_ERROR) {
        return PARSING_ERROR;
    }

    if (fill_session_id (element->command, replay_object) == PARSING_ERROR) {
        return PARSING_ERROR;
    }

    if (fill_rvalue (element->command, replay_object) == PARSING_ERROR) {
        return PARSING_ERROR;
    }

    element->command->params
        = alloc_and_parse_parms(element->command->command, replay_object);

    return (element->command->command == NONE) ? UNKNOW_OP_ERROR : 0;
}

static int is_parent(Workflow_element* parent, Workflow_element* child)
{

    int i;
    for (i = 0; i < child->n_parents; i++) {
        if (child->parents_ids[i] == parent->id) {
            return 1;
        }
    }
    return 0;
}

/**
 * Collect who are the orphans
 *
 * @param int *orphans_ids_result - An malloc'ed array to store the orphans' ids.
 * 	It is ok to assume that we have enough space in this array.
 * @param Replay_workload* repl_wld - A pointer to the Replay_workload we are
 *	collecting the orphans
 *
 * @return the number of collected orphans
 */
static int orphans (int *orphans_ids_result, Replay_workload* repl_wld)
{

    int i;
    int orphans_i = 0;
    for (i = 1; i < repl_wld->num_cmds; i++) {
        if ( element(repl_wld, i)->n_parents == 0 ) {
            orphans_ids_result[orphans_i++] = i;
        }
    }

    return orphans_i;
}

static void assign_root_timestamp (Replay_workload* wld)
{

    Workflow_element* root = element (wld, 0);

    double first_stamp = -1;
    int chl_index;

    for (chl_index = 0; chl_index < root->n_children; chl_index++) {

        Workflow_element *child = element (wld, root->children_ids[chl_index]);
        double child_stamp = child->command->traced_begin;
        if (first_stamp == -1) {
            first_stamp = child_stamp;
        }

        first_stamp = (child_stamp < first_stamp) ? child_stamp : first_stamp;
    }

    assert (first_stamp >= 0);

    root->command->traced_begin = first_stamp;
    root->command->traced_elapsed_time = 0;
}

static void fill_root_element (Workflow_element *root)
{

    workflow_element_init(root);
    root->id = ROOT_ID;
    root->produced = 1;
    root->consumed = 1;

    root->command = __replay_command_create();
}

int load (Replay_workload* replay_wld, FILE* input_file)
{

    json_t *replay_call;
    json_error_t error;
    size_t max_line_len = 1000;

    int loaded_commands = 0;
    size_t num_cmds_on_file, i;
    ssize_t len;

    if (input_file == NULL) {
        replay_wld->current_cmd = 0;
        replay_wld->num_cmds = 0;
        return NULL_FILE_OP_ERROR;
    }

    char *line = (char*) malloc(max_line_len * sizeof(char));
    len = getline(&line, &max_line_len, input_file);
    if (len == -1) {
        fprintf (stderr, "error: Unable to load data header.\n");
        return PARSING_ERROR;
    }
    num_cmds_on_file = atoi(line);

    replay_wld->element_list =
        (Workflow_element*) malloc ((num_cmds_on_file + 1) * sizeof (Workflow_element));

    //fake element is also element_list's head
    Workflow_element* root_element = element(replay_wld, 0);
    fill_root_element (root_element);
    ++loaded_commands;

    for (i = 0; i < num_cmds_on_file; i++) {

        Workflow_element* tmp_element
            = (replay_wld->element_list + loaded_commands);

        workflow_element_init (tmp_element);
        tmp_element->command = __replay_command_create();

        len = getline(&line, &max_line_len, input_file);
        if (len == -1) {
            fprintf (stderr, "error: Unable to load data header.\n");
            return PARSING_ERROR;
        }

        replay_call = json_loads (line, 0, &error);
        if (parse_element (tmp_element, replay_call) == PARSING_ERROR) {
            return PARSING_ERROR;
        }
        json_decref (replay_call);
        ++loaded_commands;
    }

    replay_wld->current_cmd = 0;
    replay_wld->num_cmds = loaded_commands;

    if (loaded_commands > 1) {//ok, there is something to replay

        //child that has no parents should become child of fake element
        Workflow_element* root_element = element(replay_wld, 0);

        //we are wasting a lot of memory, but is make thinks easy
        int *orphans_ids = (int*) malloc (sizeof (int) * replay_wld->num_cmds);
        root_element->n_children = orphans (orphans_ids, replay_wld);

        assert (root_element->children_ids == NULL);
        root_element->children_ids =
            (int*) malloc (sizeof (int) * root_element->n_children);

        int i;
        for (i = 0; i < root_element->n_children ; i++) {
            //proud papa gets a new baby
            root_element->children_ids[i] = orphans_ids[i];

            //poor orphan baby gets a new papa
            Workflow_element *child
                = element (replay_wld, root_element->children_ids[i]);

            assert (! is_parent (root_element, child));
            assert (child->n_parents == 0);
            assert (child->parents_ids == NULL);

            child->parents_ids = (int*) malloc (sizeof(int));
            child->parents_ids[child->n_parents] = root_element->id;
            child->n_parents++;
        }

        free (orphans_ids);
        assign_root_timestamp (replay_wld);
    }
//FIXME: free json
//FIXME: In case on any parsing problems, we need a label to jump to
//	a default cleaning routine,
    return 0;
}
