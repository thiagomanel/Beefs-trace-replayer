from bfs import *
from fs_objects import *
from workflow2graph import *
from workflow_objects import *
from clean_trace import *
import os, errno

def build_fs_tree(replay_dir, workflow_lines):

    def is_dir(_type):
        return _type is "d"

    def fs_object(to_create):
        return to_create[0]

    def fs_type(to_create):
        return to_create[1]

    def mkdir_p(path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST:
                pass
            else: raise

    def create_file(path):
        open(path, 'w').close()
     
    if os.path.exists(replay_dir):
        raise Exception("replay_dir should be created by replay_code")
    os.mkdir(replay_dir)

    _fs_tree = fs_tree(workflow_lines)
    for (parent, children) in _fs_tree.iteritems():
        if is_dir(parent):
            mkdir_p(replay_dir + fs_object(parent))
        for child in children:
            if is_dir(child):
                mkdir_p(replay_dir + fs_object(parent))
            else:
                if not os.path.exists(replay_dir + fs_object(parent)):
                    parents = dirs(parent_path(replay_dir + fs_object(child)))
                    for parent in parents:
                        mkdir_p(parent)
                    create_file(replay_dir + fs_object(child))

