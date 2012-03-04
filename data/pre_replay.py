from bfs import *
from fs_objects import *
from workflow2graph import *
from workflow_objects import *

def fs_objects_to_create(workflow_lines):

    def trace_begin(workflow_lines):
        first_syscall = WorkflowLine(workflow_lines[0].split()).syscall
        return syscall_timestamp(first_syscall)

    def workflow_line_id(workflow_line_tokens):
        return WorkflowLine(workflow_line_tokens)._id

    def syscall_timestamp(syscall):
        # it should be moved to an util module (testing tool has something related to it) FIXME
        """ ex. 0 916 916 (rm) rmdir 1319227056527181-26 /ok_rmdir/lib/gp_hash_table_map_ 0 """
        timestamp_tokens = syscall.split()[5].split("-")
        return (int(timestamp_tokens[0]), int(timestamp_tokens[1]))

    def created_before(timestamp, syscall):
        return syscall_timestamp(syscall)[0] < timestamp[0]

    _trace_begin = trace_begin(workflow_lines)
    w_lines_by_id = dict([(workflow_line_id(w_line.split()),  w_line) 
                             for w_line in workflow_lines]
                        )
    to_create = []
    w_tree = graph(workflow_lines)
    for node_and_child in bfs(w_tree, 1):
        w_line = w_lines_by_id[node_and_child[1]]
        node_syscall = WorkflowLine(w_line.split()).syscall
        if created_before(_trace_begin, node_syscall):
            ac_dirs, ac_files, c_dirs, c_files = accessed_and_created(node_syscall.split())
            #to_create.append(dirssnode)#FIXME to add fd object type (f or d), do not know where
    return to_create

