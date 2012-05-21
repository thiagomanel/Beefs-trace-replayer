from bfs import *
from fs_objects import *
from workflow import *
from clean_trace import *
import os, errno
import sys

def build_namespace(replay_dir, workflow_lines):#FIXME TEST-IT
    """
       it builds filesystem namespace, directories and files. Files are created empty.
       it returns a 2-tuple of list ([created_dirs], [created_files]) ordered as they
       were created
    """
    def is_dir(to_create):
        return fs_type(to_create) is "d"

    def fs_object(to_create):
        return to_create[0]

    def fs_type(to_create):
        return to_create[1]

    _fs_tree = fs_tree(workflow_lines)
    created_dirs = set()#we want to list them
    created_files = set()

    for (parent, children) in _fs_tree.iteritems():
        _parent_path = replay_dir + fs_object(parent)
        if is_dir(parent) and not os.path.exists(_parent_path):
            created_dirs.add(_parent_path)
        for child in children:
            if is_dir(child):
                if not os.path.exists(_parent_path):
                    created_dirs.add(_parent_path)
                child_path = replay_dir + fs_object(child)
                created_dirs.add(child_path)
            else:
                filepath = replay_dir + fs_object(child)
                if not os.path.exists(_parent_path):
                    parents = dirs(parent_path(filepath))
                    for parent in parents:
                        if not os.path.exists(_parent_path):
                            created_dirs.add(_parent_path)
                if not os.path.exists(filepath):
                    created_files.add(filepath)

    return (created_dirs, created_files)

if __name__ == "__main__":

    """
        It find the namespace to be created, it means file and directories
        that are used in workflow data but are not present in replay_dir_path. It outputs file or
        directories names and its type, "f" or "d", separated by \t

        replay_dir is a path to mount point where remote file system was mounted.
        For example a remote directory, e.g /local/nfs_to_export is exported in
        the server machine and mounted at client side at /tmp/home, so replay_dir
        is /tmp. A directory within the exported directory, e.g 
        /local/nfs_to_export/thiagoepdc, will be seen as /tmp/home/manel
    """
    #FIXME use opt
    usage_msg = "Usage: python pre_replay.py replay_dir workflow_path\n"

    if not len(sys.argv) == 3:
        sys.stderr.write(usage_msg)
        sys.exit(1)

    replay_dir = sys.argv[1]
    with open(sys.argv[2], 'r') as workflow_file:
        workflow_json = json.load(workflow_file)
        w_lines = [WorkflowLine.from_json(wline_json) 
                      for wline_json in workflow_json]

        created_dirs, created_files = build_namespace(replay_dir, w_lines)
        for _dir in created_dirs:
            sys.stdout.write("\t".join([_dir, "d", "\n"]))
        for _file in created_files:
            sys.stdout.write("\t".join([_file, "f", "\n"]))
