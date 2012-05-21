from itertools import tee
from itertools import izip
from itertools import chain
from clean_trace import *
import sys
import json

# if things start to get complicated we should try using ReplayInput class from match_syscall.py
#TODO: open with creation semantics is different
#FIXME maybe we should move this an util module, in this module we handle input and output and 
#code this fs_obj methods. Timestamp methods also. In summary, any method manipulating input and output

class WorkflowLine:
    def __init__(self, _id, parents, children, clean_call):
        self._id = _id
        self.parents = parents
        self.children = children
        self.clean_call = clean_call

    def json(self):
        stamp = self.clean_call.stamp.split("-")
        begin = float(stamp[0])
        end = long(stamp[1])
        return {
                "id": self._id,
                "parents": self.parents,
                "children": self.children,
                "stamp": {
                          "begin": begin,
                          "elapsed": end
                         },
                "call": self.clean_call.call,
                "caller": {
                           "exec": self.clean_call.pname,
                           "uid": self.clean_call.uid,
                           "pid": self.clean_call.pid,
                           "tid": self.clean_call.tid
                          },
                "args": self.clean_call.args,
                "rvalue": int(self.clean_call.rvalue) 
              }

    @classmethod
    def from_json(cls, _json):
        #creates itself based on json dict defined on self.json()
        uid = _json["caller"]["uid"]
        pid = _json["caller"]["pid"]
        tid = _json["caller"]["tid"]
        pname = _json["caller"]["exec"]
        stamp_str = str(int(_json["stamp"]["begin"])) + "-" \
                    + str(_json["stamp"]["elapsed"])

        return WorkflowLine( _json["id"],
                             _json["parents"],
                             _json["children"],
                             CleanCall(uid, pid, tid,
                                       pname,
                                       _json["call"],
                                       stamp_str,
                                       [ str(arg) for arg in _json["args"]],
                                       str(_json["rvalue"]))
                            )  
                                       

    def __str__(self):
        return json.dumps(self.json(), sort_keys=True, indent=4)

def graph(workflow_lines, bottom_up=False):
    """ 
        it builds a graph based on replay workflow data. On this map-based graph, node id
        is the key and the arcs is the value as a list of ids
        trace workflow excerpt
        1 0 - 3 2 3 2 1159 16303 16318 (chrome) open 1319203757986598-1310 /home/thiagoepdc/.config/google-chrome/com.google.chrome.gUMVsk 32962 384 43
        2 2 1 1 1 3 1159 16303 16318 (chrome) fstat 1319203757987999-87 /home/thiagoepdc/.config/google-chrome/com.google.chrome.gUMVsk 43 0
    """
    _graph = {}
    for wline in workflow_lines:
        if bottom_up:
            _graph[wline._id] = wline.parents
        else:
            _graph[wline._id] = wline.children
    return _graph

def fs_dependency_order(workflow_lines):#do we assume _id or timestamp order ?
#TODO: Does it modify workflow_line or it creates a new collection
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
            self.wlines = []

        def append(self, wline):
            if not wline in self:
                self.wlines.append(wline)
	        self.ids.add(wline._id)		

        def __len__(self): return len(self.wlines)

        def __getitem__(self, item): return self.wlines[item]

        def __contains__(self, item): return item._id in self.ids

        def __str__(self): return str(self.wlines)

    def fs_obj(clean_call):

        if (clean_call.call == "mkdir") or (clean_call.call == "unlink") \
           or (clean_call.call == "rmdir"):
            filepath = clean_call.fullpath()
            parent = parent_path(filepath)
            return [filepath, parent]

        elif clean_call.call == "stat":
            return [clean_call.fullpath()]

        elif clean_call.call == "open":
            return  [(clean_call.pid, clean_call.fd()), clean_call.fullpath()]

        elif (clean_call.call == "fstat") or (clean_call.call == "write") \
              or (clean_call.call == "read") or (clean_call.call == "llseek") \
              or (clean_call.call == "close"):
            return [(clean_call.pid, clean_call.fd())]

        else: 
            raise Exception("unsupported operation " + str(line_tokens))

    def update_dependency(w_line_to_update, w_line_target_parents):
        def write_semantics(call):
            return call in ["rmdir", "mkdir", "unlink", "write", "llseek", "open"]

        for parent in reversed(w_line_target_parents):
            clean_call = parent.clean_call
            if write_semantics(clean_call.call):
               join(parent, w_line_to_update)
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
    for w_line in workflow_lines:
        clean_call = w_line.clean_call
        _fs_objs = fs_obj(clean_call)
        for obj in _fs_objs:
            if not obj in lines_by_fs_obj:
                lines_by_fs_obj[obj] = Operations()
            lines_by_fs_obj[obj].append(w_line)

    for (obj, operations) in lines_by_fs_obj.iteritems():
        for i in reversed(range(len(operations))):
            update_dependency(operations[i], operations[:i])#these list creation can hurt our performance

    return workflow_lines

def join(father, son):
    if son:
        father.children.append(son._id)
        son.parents.append(father._id)

def order_by_pidfid(cleaned_calls):
    """ From a collection of CleanCalls to a collection of
        workflow lines, ordered by pid-tid
    """
    def pidfidprocess(clean_call):
        return (clean_call.pid, clean_call.tid, clean_call.pname)
    def pairwise(iterable):
        a, b = tee(iterable)
        next(b, None)
        return izip(a, b)

    wlines_by_fidpidprocess = {}

    for (_id, cleaned_call) in enumerate(cleaned_calls):
        pfp = pidfidprocess(cleaned_call)
        if not pfp in wlines_by_fidpidprocess:
            wlines_by_fidpidprocess[pfp] = []
        wlines_by_fidpidprocess[pfp].append(WorkflowLine(_id + 1, [], [], cleaned_call))

    for lines in wlines_by_fidpidprocess.values():
        for (father, son) in pairwise(lines):
            join(father, son)
    
    #stackoverflow says it is faster
    #FIXME: unit should be broken after this change
    result = []
    map(result.extend, wlines_by_fidpidprocess.values())
    return result
