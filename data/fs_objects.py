from clean_trace import *
from fileutil import *
from workflow import *
from itertools import *
from bfs import *

#TODO: after using this module do we guarantee all file system hierarchy was created ? So, replayer
	#can run fine ?
def open_to_create(clean_call):
    return CREATION_FLAGS.O_CREAT in creation_flags(open_flags(clean_call))

def dirs(fullpath):
    _dirs = []
    _dirs.append(fullpath)
    last_slash_index = fullpath.rfind("/")
    if (last_slash_index > 0):
        _dirs.extend(dirs(fullpath[:last_slash_index]))
    return _dirs

def accessed_and_created(clean_call):
    """
        for a CleanCall instance, extract the collection of touched and
        created diretories and files as a 4-tuple of lists
        ([touched_dirs], [touched_files], [created_dirs], [created_files])
    """
    def success(clean_call):
        return int(clean_call.rvalue) >= 0

    #we do not handle close and fstat because its information was already processed on the
    #associated open call
    if success(clean_call):
        _fullpath = clean_call.fullpath()
        _call = clean_call.call
        if _call == "unlink" or _call == "stat" or _call == "read" or \
            _call == "write" or _call == "llseek":
            #FIXME we can make basename and dirs to manage this
            parent = parent_path(_fullpath)
            return (dirs(parent), [_fullpath], [], [])
        elif (_call == "rmdir"):
            return (dirs(_fullpath), [], [], [])
        elif _call == "mkdir":
            parent = parent_path(_fullpath)
            return (dirs(parent), [], [_fullpath], [])
        elif _call == "open":
            parent = parent_path(_fullpath)
            if open_to_create(clean_call):
                return (dirs(parent), [], [], [_fullpath])
            else:
                return (dirs(parent), [_fullpath], [], [])

    return ([], [], [], [])

def fs_tree(workflow_lines):
    """ gives the fs tree as view in workflow begin """
    w_lines_by_id = dict([(w_line._id,  w_line) for w_line in workflow_lines])

    def path_graph(dirs):
        """ ["/a/b/c", "/a/b", "/a"] -> {"/a":"/a/b", "/a/b":"/a/b/c"} """
        def pairwise(iterable):#this code is duplicated elsewhere
            a, b = tee(iterable)
            next(b, None)
            return izip(a, b)

        _graph = {}
        if len(dirs) == 1:
            _graph[dirs[0]] = None
        else:
            for (parent, child) in pairwise(reversed(dirs)):
                _graph[parent] = child
        return _graph

    def clean_call(line_id):
        w_line = w_lines_by_id[line_id]
        return w_line.clean_call

    parents_to_children = {}
    created_paths = set()

    the_graph = graph(workflow_lines)

    #FIMXE this code does not add fake root to orphan nodes. so, bfs does not work properly.
    #so, it is a hack to add the fake root
    num_nodes = len(workflow_lines)
    orphan_nodes = set(range(1, num_nodes + 1))#at the begin we think everyone is a orphan

    for father, children in the_graph.iteritems():
        for child in children:
            if child in orphan_nodes:
                orphan_nodes.remove(child)

    #adding fake root
    fake_root_id = 0
    the_graph[fake_root_id] = []
    for orphan in orphan_nodes:
        the_graph[fake_root_id].append(orphan)

    for node_and_child in bfs(the_graph, 0):
        child_id = int(node_and_child[1])
        if (child_id == 0):
            continue#argg
        node_clean_call = clean_call(child_id)
        ac_dirs, ac_files, c_dirs, c_files = accessed_and_created(node_clean_call)

        for c_dir in c_dirs:
            created_paths.add(c_dir)
        for c_file in c_files:
            created_paths.add(c_file)

        for parent_dir, child_dir in path_graph(ac_dirs).iteritems():
            if not parent_dir in created_paths:
                if not (parent_dir, "d") in parents_to_children:
                    parents_to_children[(parent_dir, "d")] = set()
                if child_dir:
                    if not child_dir in created_paths:
                        parents_to_children[(parent_dir, "d")].add((child_dir, "d"))

        for a_file in ac_files:
            if not a_file in created_paths:
                parent = parent_path(a_file)
                if not (parent, "d") in parents_to_children:
                    parents_to_children[(parent, "d")] = set()
                parents_to_children[(parent, "d")].add((a_file, "f"))

    #accessed_and_created method is not reliable, for example
    #it is possible to directories be opened and closed, also llseeked
    #for this reason, ac_files can return directories, to get over it
    #we make a second pass to see if an acessed file was also identified as
    #directory, if so, we change its type
    #TODO is the conversely possible ? think a file is a directory
    to_change_type = []
    for parent, children in parents_to_children.iteritems():
        for path, _type in children:
            if _type is "f":
                if (path, "d") in parents_to_children:#it was described as dir before
                    to_change_type.append((parent, (path, _type)))

    for parent, child in to_change_type:
        parents_to_children[parent].remove(child)
        parents_to_children[parent].add((child[0], "d"))

    return parents_to_children
