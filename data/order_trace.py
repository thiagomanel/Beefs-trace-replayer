from itertools import tee
from itertools import izip
from itertools import chain
from clean_trace import *

# if things start to get complicated we should try using ReplayInput class from match_syscall.py
#TODO: open with creation semantics is different
#FIXME maybe we should move this an util module, in this module we handle input and output and 
#code this fs_obj methods. Timestamp methods also. In summary, any method manipulating input and output

def pidfidprocess(tokens):
    return (tokens[1], tokens[2], tokens[3])

def fs_dependency_order(lines):#do we assume _id or timestamp order ?
    """
    We assume:
        - there are not operations over a fd that was not properly opened before
    """
    class Operations():
        """
        Operations which have a particular relationship. For example, operations
        over the same file system object.  We do not allow duplicated lines and 
        expose a list to iterate over the same append order
        """
        def __init__(self):
            self.ids = set()
            self.lines = []

        def append(self, line):
            if not line in self:
                self.lines.append(line)
	        self.ids.add(line[0])		

        def __len__(self): return len(self.lines)

        def __getitem__(self, item): return self.lines[item]

        def __contains__(self, item): return item[0] in self.ids

        def __str__(self): return str(self.lines)

    def fs_obj(line_tokens):

        def open_full_path(tokens):
            return tokens[6]

        if call(line_tokens) == "mkdir":
            filepath = pathcall_fullpath(line_tokens)
            parent = parent_path(filepath)
            return [filepath, parent]
        elif call(line_tokens) == "stat":
            return [pathcall_fullpath(line_tokens)]
        elif call(line_tokens) == "open":
            return  [(pid(line_tokens), open_fd(line_tokens)), open_full_path(line_tokens)]
        elif call(line_tokens) == "fstat":
            return [(pid(line_tokens), fstat_fd(line_tokens))]
        elif call(line_tokens) == "llseek":
            return [pathcall_fullpath(line_tokens)]
        elif call(line_tokens) == "rmdir":
            filepath = pathcall_fullpath(line_tokens)
            parent = parent_path(filepath)
            return [filepath, parent]
        elif call(line_tokens) == "unlink":
            filepath = pathcall_fullpath(line_tokens)
            parent = parent_path(filepath)
            return [filepath, parent]
        elif (call(line_tokens) == "write") or (call(line_tokens) == "read"):
            return [(pid(line_tokens), rw_fd(line_tokens))]
        elif (call(line_tokens) == "close"):
            return [(pid(line_tokens), close_fd(line_tokens))]
        else: 
            raise Exception("unsupported operation " + str(line_tokens))

    def write_semantics(call):
        return (call == "rmdir") or (call == "mkdir") or (call == "unlink") or (call == "write") or (call == "llseek") or (call == "open")

    def update_dependency(to_update, target_parents):
        for parent in reversed(target_parents):
            op_line = parent[-1]
            _call = call(op_line.split())
            if write_semantics(_call):
               join(parent, to_update)
               break
    
    """
    we assume lines have been ordered by pidfid algorithm
    
    op                structure              type
    -----------------------------------------------
    stat                obj                  read
    fstat               obj                  read
    rmdir               parent, [obj]        write
    mkdir               parent               write
    unlink              parent, [obj]        write
    open                
    close
    write               obj                  write
    read                obj                  read 
    llseek              obj                  write
    open/create         obj                  write
    -----------------------------------------------
    """
    lines_by_fs_obj = {}
    pid_fd2fs_obj = {}
    #FIXME we can create a map_by_fsobt method and after that the order method
    for line in lines:
        syscall = line[-1]
        _fs_objs = fs_obj(syscall.split())
        for obj in _fs_objs:
            if not obj in lines_by_fs_obj:
                lines_by_fs_obj[obj] = Operations()
            lines_by_fs_obj[obj].append(line)

    for (obj, operations) in lines_by_fs_obj.iteritems():
        for i in reversed(range(len(operations))):
            update_dependency(operations[i], operations[:i])#these list creation can hurt our performance

    return lines

def join(father, son):
    if son:
        father[3] = father[3] + 1
        father[4].append(son[0])
        son[1] = son[1] + 1
        son[2].append(father[0])

def order_by_pidfid(lines):

    def pairwise(iterable):
        a, b = tee(iterable)
        next(b, None)
        return izip(a, b)

    lines_by_fidpidprocess = {}

    for (_id, line) in enumerate(lines):
        pfp = pidfidprocess(line.split())
        if not pfp in lines_by_fidpidprocess:
            lines_by_fidpidprocess[pfp] = []
        lines_by_fidpidprocess[pfp].append([_id + 1, 0, [], 0, [], line])

    for lines in lines_by_fidpidprocess.values():
        for (father, son) in pairwise(lines):
            join(father, son)
    
    #stackoverflow says it is faster
    #FIXME: unit should be broken after this change
    result = []
    map(result.extend, lines_by_fidpidprocess.values())
    return result
