from itertools import tee
from itertools import izip
from itertools import chain
from clean_trace import call

#if things start to get complicated we should try using ReplayInput class from match_syscall.py

def pidfidprocess(tokens):
    return (tokens[1], tokens[2], tokens[3])

def fs_dependency_order(lines):#do we assume _id or timestamp order ?

    class Operations():
        """
        this class groups a collection of operations which have a particular
        relationship. For example, operation over the same file system object.
        We do not allow duplicated lines and expose a list to iterate over the
        same append order
        """
        def __init__(self):
            self.ids = set()
            self.lines = []

        def append(self, line):
            if not line in self:
                self.lines.append(line)
	        self.ids.add(line[0])		

        def __len__(self):
            return len(self.lines)

        def __getitem__(self, item):
            return self.lines[item]

        def __contains__(self, item):
            return item[0] in self.ids

    def fs_obj(line_tokens):
        if call(line_tokens) == "mkdir":
            filepath = line_tokens[6]
            parent = filepath[:filepath.rfind("/")]
            return [filepath, parent]
        if call(line_tokens) == "stat":
            return [line_tokens[6]]
        else: 
            raise Exception("unsupported operation " + str(line_tokens))

    def write_semantics(call):
        return (call == "rmdir") or (call == "mkdir") or (call == "unlink") or (call == "write") or (call == "llseek")

    def update_dependency(to_update, target_parents):
        for parent in target_parents:
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
    for line in lines:
        syscall = line[-1]
        _fs_objs = fs_obj(syscall.split())
        for obj in _fs_objs:
            if not obj in lines_by_fs_obj:
                lines_by_fs_obj[obj] = Operations()
            lines_by_fs_obj[obj].append(line)

    for (obj, operations) in lines_by_fs_obj.iteritems():
        for i in reversed(range(len(operations))):
            update_dependency(operations[i], operations[:i])

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

    return chain(lines_by_fidpidprocess.values())
