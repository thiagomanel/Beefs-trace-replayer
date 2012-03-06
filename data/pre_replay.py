from bfs import *
from fs_objects import *
from workflow2graph import *
from workflow_objects import *
from clean_trace import *
import os, errno

def find_file_size(join_data_lines, path_and_timestamps):
    """ 
        join_data_lines is the input data to clean_trace.py
        path_and_timestamps is a list of tuple as
        [(path1, timestamp2) ... (pathn, timestampn)] where timestamp
        comes from the first occurrence of a llseek, write or read operation
        over the filepath to find. This list is timestamp ordered
    """
    def timestamp(path_and_timestamp):
        return path_and_timestamp[1]

    def join_line_timestamp(line):
        pass

    first_stamp = timestamp(path_and_timestamps[0])
    last_stamp = timestamp(path_and_timestamps[0])
    to_find = {}
    for path_and_stamp in path_and_timestamps:
        stamp = timestamp(path_and_stamp)
        if not stamp in to_find:
            to_find[stamp] = set()
        to_find[stamp].add(path_and_stamp)

    for line in join_data_lines:
        line_timestamp = join_line_timestamp(line)
        if first_stamp <= line_timestamp <= last_stamp:
            if 

def build_namespace(replay_dir, workflow_lines):#FIXME TEST-IT
    """
       it builds filesystem namespace, directories and files. Files are created empty.
       it returns a 2-tuple of list ([created_dirs], [created_files]) ordered as they
       were created
    """

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

    created_dirs = []
    created_files = []

    for (parent, children) in _fs_tree.iteritems():
        parent_path = replay_dir + fs_object(parent)
        if is_dir(parent):
            mkdir_p(parent_path)
            created_dirs.append(parent_path)
        for child in children:
            if is_dir(child):
                mkdir_p(parent_path)#FIXME is this correct ?
                created_dirs.append(parent_path)
            else:
                if not os.path.exists(parent_path):
                    filepath = replay_dir + fs_object(child)
                    parents = dirs(parent_path(filepath))
                    for parent in parents:
                        mkdir_p(parent)#FIXME we do not need this if we use mkdir_p
                        created_dirs.append(parent_path)
                    create_file(filepath)
                    files_to_write.append(filepath)

    return (created_dirs, created_files)
