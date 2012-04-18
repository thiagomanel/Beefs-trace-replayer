from bfs import *
from fs_objects import *
from workflow2graph import *
from workflow_objects import *
from clean_trace import *
import os, errno
import sys

def find_timestamps(replay_dir, created_files, workflow_lines):
    """
       find the timestamps of the first write, read or llseek
       calls to created_files list. Paths on created_files are different
       than those from workflow_lines, they have replay_dir as root
    """
    calls_with_size = ["write", "read", "llseek"]

    to_find = list(created_files)
    result = dict((_file, None) for _file in created_files)
    for line in workflow_lines:
        if not to_find:#we found everything
            break
        traced_line_tokens = WorkflowLine(line.split()).syscall.split()
        syscall = call(traced_line_tokens)
        if syscall in calls_with_size:
            to_replay_fullpath = replay_dir + syscall_fullpath(traced_line_tokens)
            if (to_replay_fullpath) in to_find:
                result[to_replay_fullpath] = syscall_timestamp(traced_line_tokens)
                to_find.remove(to_replay_fullpath)

    return result

def find_file_size(join_data_file, path_and_timestamps):
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
        file_info_tokens = line.split("(/")[1].split(" ")
        file_size = file_info_tokens[3]
        try:
            return long(file_size)
        except ValueError:
            return None

    join_calls_with_size = ["sys_read", "sys_write", "sys_llseek"]
    timestamp_to_find = [timestamp(stamp_str)
				 for stamp_str in path_and_timestamps.values()
                                  if stamp_str]#excluding stamps equals to None

    result = {}
    if timestamp_to_find:
        first_stamp = min(timestamp_to_find)
        #last_stamp = max(timestamp_to_find)

        to_find = {}
        #invert dict
        for path, stamp_str in path_and_timestamps.iteritems():
            if stamp_str:
                stamp = timestamp(stamp_str)
                if not stamp in to_find:
                    to_find[stamp] = set()
                to_find[stamp].add((path, stamp))

        for line in join_data_file:
            line_timestamp = join_line_timestamp(line)
            if first_stamp <= line_timestamp:
                if line_timestamp in to_find:
                    _syscall = join_line_syscall(line)
                    if _syscall in join_calls_with_size:
                        for path, stamp in to_find[line_timestamp]:
                            #we can have multiple lines in in the same timestamp
                            if basename(path) in line:
                                file_size = join_line_file_size(line)
                                result[path] = file_size
            #if line_timestamp > last_stamp:
             #   break

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
        We operate in one of two modes: "f" or "s"

        If -f options was given, it find the namespace to be created, it means file and directories
        that are used in workflow data but are not present in replay_dir_path. It outputs file or
        directories names and its type, "f" or "d", separated by \t

        If -s option was given it tries to find the file size of files found by the this module using
        -f option. It outpus file name, type and file size separated by \t. If it was not possible to
        find the size for a given file, it assumes -1 to mark this lack of information
    """
    #FIXME use opt

    usage_msg = "Usage: python pre_replay.py replay_dir [-f] [-s to_create_namespace_file_path join_file_path] replay_input_path\n"

    if (len(sys.argv) < 3):
        sys.stderr.write(usage_msg)
        sys.exit(1)

    replay_dir = sys.argv[1]
    mode = sys.argv[2]

    if mode == "-f":
        if not len(sys.argv) == 4:
            sys.stderr.write(usage_msg)
            sys.exit(1)

        with open(sys.argv[3], 'r') as workflow_file:
            workflow_file.readline()#excluding header
            created_dirs, created_files = build_namespace(replay_dir, workflow_file.readlines())
            for _dir in created_dirs:
                sys.stdout.write("\t".join([_dir, "d", "\n"]))
            for _file in created_files:
                sys.stdout.write("\t".join([_file, "f", "\n"]))
    elif mode == "-s":
        if not len(sys.argv) == 6:
            sys.stderr.write(usage_msg)
            sys.exit(1)

        with open(sys.argv[3]) as namespace_to_create:
            created_dirs, created_files = set(), set()
            for fs_obj in namespace_to_create:
                tokens = fs_obj.split()
                ftype = tokens[-1]
                if ftype == "d":
                    created_dirs.add(tokens[0])
                elif ftype == "f":
                    created_files.add(tokens[0])

        with open(sys.argv[5], 'r') as workflow_file:
            workflow_file.readline()#excluding header
            workflow_lines = workflow_file.readlines()

        path_to_timestamp = find_timestamps(replay_dir, created_files, workflow_lines)
        #FIXME it's possible to get None timestamps here
        files_sizes = {}
        with open(sys.argv[4], 'r') as join_data_file:
            files_sizes = find_file_size(join_data_file, path_to_timestamp)

        for _dir in created_dirs:
            sys.stdout.write("\t".join([_dir, "d", "\n"]))
        for _file in created_files:
            if _file in files_sizes:
                sys.stdout.write("\t".join([_file, "f", str(files_sizes[_file]),
                                            str(path_to_timestamp[_file]), "\n"]))
            else:
                sys.stdout.write("\t".join([_file, "f", "-1",
                                            str(path_to_timestamp[_file]), "\n"]))
    else:
        sys.stderr.write("We need a mode: -f or -s\n")
        sys.exit(-1)
