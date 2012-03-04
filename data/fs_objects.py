from clean_trace import *
from fileutil import *
from workflow2graph import *
from workflow_objects import *
from itertools import *

#TODO: after using this module do we guarantee all file system hierarchy was created ? So, replayer
	#can run fine ?
def open_to_create(tokens):
    return CREATION_FLAGS.O_CREAT in creation_flags(open_flags(tokens))

def success(call_tokens):#FIXME move this to clean_trace.py module
    return_value = int(call_tokens[-1])
    if return_value < 0:
        return False
    return True 

def fullpath(call_tokens):
    return call_tokens[6]#FIXME move this to clean_trace.py module

def dirs(fullpath):
    _dirs = []
    _dirs.append(fullpath)
    last_slash_index = fullpath.rfind("/")
    if (last_slash_index > 0):
        _dirs.extend(dirs(fullpath[:last_slash_index]))
    return _dirs

def accessed_and_created(tokens):
    """
        for a tokenized workflow line, extract the collection of touched and 
        created diretories and files as a 4-tuple of lists 
        ([touched_dirs], [touched_files], [created_dirs], [created_files])
    """
    #we do not handle close and fstat because its information was already processed on the 
    #associated open call
    if success(tokens):
        _fullpath = fullpath(tokens)
        _call = call(tokens)
        if (_call == "unlink" or _call == "stat" or _call == "read" or _call == "write" or _call == "llseek"):
            #FIXME we can make basename and dirs to manage this
            parent = parent_path(_fullpath)
            return (dirs(parent), [basename(_fullpath)], [], [])
        elif (_call == "rmdir"):
            return (dirs(_fullpath), [], [], [])
        elif _call == "mkdir":
            parent = parent_path(_fullpath)
            return (dirs(parent), [], [basename(_fullpath)], [])
        elif _call == "open":
            parent = parent_path(_fullpath)
            if open_to_create(tokens):
                return (dirs(parent), [], [], [basename(_fullpath)])
            else:
                return (dirs(parent), [basename(_fullpath)], [], [])

    return ([], [], [], [])

def fs_tree(workflow_lines):
    """ gives the fs tree as view in workflow begin """
    w_lines_by_id = dict(
                          [ (WorkflowLine(w_line.split())._id,  w_line)
                           for w_line in workflow_lines]
                         )

    def path_graph(dirs):
        """ when ["/a/b/c", "/a/b", "/a"]
            then {"/a":"/a/b", "/ab":"/a/b/c"}
        """
        def pairwise(iterable):#this code is duplicated elsewher
            a, b = tee(iterable)
            next(b, None)
            return izip(a, b)

        _graph = {}
        for (parent, child) in pairwise(reversed(dirs)):
            _graph[parent] = child
        return _graph

    def syscall(line_id):
        w_line = w_lines_by_id[line_id]
        return WorkflowLine(w_line.split()).syscall
                    
    parents_to_children = {}
    created_paths = set()

    for node_and_child in bfs(graph(workflow_lines), 1):
        child_id = int(node_and_child[1])
        node_syscall = syscall(child_id)
        ac_dirs, ac_files, c_dirs, c_files = accessed_and_created(node_syscall.split())

        for parent_dir, child_dir in path_graph(ac_dirs).iteritems():
            if not parent_dir in created_paths:
                if not parent_dir in parents_to_children:
                    parents_to_children[parent_dir] = set()
                if not child_dir in created_paths:
                    parents_to_children[parent_dir].add(child_dir)
        
    return parents_to_children
