from bfs import *
from workflow2graph import *
from workflow_objects import objects

def fs_objects_to_create(workflow_lines):

    def trace_walk(workflow_lines, timestamp):

        def syscall_timestamp(syscall):
            # it should be moved to an util module (testing tool has something related to it) FIXME
            """ ex. 0 916 916 (rm) rmdir 1319227056527181-26 /ok_rmdir/lib/gp_hash_table_map_ 0 """
            timestamp_tokens = syscall.split()[5].split("-")
            return (int(timestamp_tokens[0]), int(timestamp_tokens[1]))

        def created_before(timestamp, workflow_line):
            (_id, n_parents, parents, n_children, children, syscall) = objects(workflow_line)
            return syscall_timestamp(syscall)[0] < timestamp[0]

        w_tree = graph(workflow_lines)
        for node, children in bfs(w_tree, 1):
            if created_before(timestamp, node):
                old_children = [child for child in children 
                                if created_before(timestamp, child)]
                yield node, old_chilren#FIXME to add fd object type (f or d), do not know where

    return []
