from bfs import *
from fs_objects import *
from workflow2graph import *
from workflow_objects import *
from clean_trace import *
import os, errno
import sys

def find_timestamps(created_files, workflow_lines):
     
    calls_with_size = ["write", "read", "llseek"]

    to_find = list(created_files)
    result = dict((_file, None) for _file in created_files)
    for line in workflow_lines:
        if not to_find:#we found everything
            break
        traced_line_tokens = WorkflowLine(line.split()).syscall.split()
        syscall = call(traced_line_tokens)
        if syscall in calls_with_size:
            _fullpath = syscall_fullpath(traced_line_tokens)
            if _fullpath in to_find:
                result[_fullpath] = syscall_timestamp(traced_line_tokens)
                to_find.remove(_fullpath)

    return result
            
def find_file_size(join_data_lines, path_and_timestamps):
    """ 
        join_data_lines is the input data to clean_trace.py
        path_and_timestamps is a list of tuple as
        [(path1, timestamp2) ... (pathn, timestampn)] where timestamp
        comes from the first occurrence of a llseek, write or read operation
        over the filepath to find. This list is timestamp ordered
    """
    def timestamp(stamp_str):#FIXME i bet this code is duplicated elsewhere
        return long(stamp_str.split("-")[0])

    def join_line_timestamp(line):
        """  e.g 1159 2064 2084 (pulseaudio) sys_write 1319203706332866-16 (/ / /[eventfd]/ 0  558) 19 8 8 """
        return timestamp(line.split()[5])

    def join_line_syscall(line):
        return line.split()[4]

    def join_line_file_size(line):
        """  e.g 1159 2064 2084 (pulseaudio) sys_write 1319203706332866-16 (/ / /[eventfd]/ 0  558) 19 8 8
             this format does not help much, we are going to:
             1. tokenize by "(/"
             2. take the second token
             3. tokenize by " "
             4. take the 3th token, If it's possible to transform to a number we use it
        """
        file_info_tokens = line.split("(\/")[1].split(" ")
        file_size = file_info_tokens[3]
        try:
            return long(file_size)
        except ValueError:
            return None

    join_calls_with_size = ["sys_read", "sys_write", "sys_llseek"]
    timestamp_to_find = [timestamp(stamp_str) 
				 for stamp_str in path_and_timestamps.values()]

    first_stamp = min(timestamp_to_find)
    last_stamp = max(timestamp_to_find)

    to_find = {}
    #invert dict
    for path, stamp in path_and_timestamps:
        stamp = timestamp(path_and_stamp)
        if not stamp in to_find:
            to_find[stamp] = set()
        to_find[stamp].add(path_and_stamp)

    result = {}

    for line in join_data_lines:
        line_timestamp = join_line_timestamp(line)
        if first_stamp <= line_timestamp:
            if line_timestamp in to_find:
                _syscall = join_line_syscall(line)
                if _syscall in join_calls_with_size:
                    for path, stamp in to_find[line_timestamp]:
                        if basename(path) in line:#we can have multiple lines in in the same timestamp
                            file_size = join_line_file_size(line)
                            if file_size:
                                result[path] = file_size
        if line_timestamp > last_stamp: break

    return result

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

    def mkdir_p(path):
        print "mkdir_p", path
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
        _parent_path = replay_dir + fs_object(parent)
        if is_dir(parent):
            mkdir_p(_parent_path)
            created_dirs.append(_parent_path)
        for child in children:
            if is_dir(child):
                mkdir_p(_parent_path)#FIXME is this correct ?
                created_dirs.append(_parent_path)
            else:
                filepath = replay_dir + fs_object(child)
                if not os.path.exists(_parent_path):
                    parents = dirs(parent_path(filepath))
                    for parent in parents:
                        mkdir_p(parent)#FIXME we do not need this if we use mkdir_p
                        created_dirs.append(parent_path)
                create_file(filepath)
                created_files.append(filepath)

    return (created_dirs, created_files)

def expand_file(filename, newsize):
    pass

if __name__ == "__main__":
    """Usage: python pre_replay.py replay_dir_path replay_input_path join_file_path"""

    replay_dir = sys.argv[1]
    with open(sys.argv[2], 'r') as workflow_file:
        workflow_lines = workflow_file.readlines()[1:]
        created_dirs, created_files = build_namespace(replay_dir, workflow_lines)

        for cd in created_dirs:
            print "cd", cd
        for cf in created_files:
            print "cf", cf

        workflow_file.seek(0)
        workflow_lines = workflow_file.readlines()[1:]

        path_to_timestamp = find_timestamps(created_files, workflow_lines)#FIXME it think we cannot iterate again over it
        with open(sys.argv[3], 'r') as join_data_file:
            for filepath, size in find_file_size(join_data_file.readlines(), path_to_timestamp):
                if size:
                    expand_file(filepath, size)
