from itertools import tee
from itertools import izip
from itertools import chain
import sys
import json
from clean_trace import *

# if things start to get complicated we should try using ReplayInput class from match_syscall.py
#TODO: open with creation semantics is different
#FIXME maybe we should move this an util module, in this module we handle input and output and
#code this fs_obj methods. Timestamp methods also. In summary, any method manipulating input and output

class WorkflowLine:
    def __init__(self, _id, session_id, parents, children, clean_call):
        self._id = _id
        self.parents = parents
        self.children = children
        self.clean_call = clean_call
        self.session_id = session_id

    def json(self):
        stamp = self.clean_call.stamp()
        #TODO: I do not remember this shit is a float, but I'll keep it
        begin = float(stamp[0])
        elapsed = stamp[1]
        return {
                "id": self._id,
                "parents": self.parents,
                "children": self.children,
                "stamp": {
                          "begin": begin,
                          "elapsed": elapsed
                         },
                "call": self.clean_call.call,
                "caller": {
                           "exec": self.clean_call.pname,
                           "uid": self.clean_call.uid,
                           "pid": self.clean_call.pid,
                           "tid": self.clean_call.tid
                          },
                "session_id": self.session_id,
                "args": self.clean_call.args,
                "rvalue": int(self.clean_call.rvalue)
              }

    @classmethod
    def from_json_safe(cls, _json):
        #we override problematic encoded string with a stub string.
        #this method is useful when we want to analyse workflow without
        #replaying it (so we do not need proper args values)

        #creates itself based on json dict defined on self.json()
        uid = _json["caller"]["uid"]
        pid = _json["caller"]["pid"]
        tid = _json["caller"]["tid"]
        pname = _json["caller"]["exec"]
        stamp_str = str(int(_json["stamp"]["begin"])) + "-" \
                    + str(_json["stamp"]["elapsed"])

        #FIXME 28/mar I added this new session_id element, but I not willing to
        #change all codebase right now. So I adding this switch here, to convert
        #old json to the new format
        if not "session_id" in _json:
           _json["session_id"] = "-1"

        try:
            _args = [ str(arg) for arg in _json["args"]]
        except UnicodeEncodeError:
            _args = ["bad_encoded_string"]

        return WorkflowLine( _json["id"],
                             int(_json["session_id"]),
                             _json["parents"],
                             _json["children"],
                             CleanCall(uid, pid, tid,
                                       pname,
                                       _json["call"],
                                       stamp_str,
                                       _args,
                                       str(_json["rvalue"]))
                            )

    @classmethod
    def from_json(cls, _json):
        #creates itself based on json dict defined on self.json()
        uid = _json["caller"]["uid"]
        pid = _json["caller"]["pid"]
        tid = _json["caller"]["tid"]
        pname = _json["caller"]["exec"]
        stamp_str = str(int(_json["stamp"]["begin"])) + "-" \
                    + str(_json["stamp"]["elapsed"])

        #FIXME 28/mar I added this new session_id element, but I not willing to
        #change all codebase right now. So I adding this switch here, to convert
        #old json to the new format
        if not "session_id" in _json:
           _json["session_id"] = "-1"

        return WorkflowLine( _json["id"],
                             int(_json["session_id"]),
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

def i_graph(wline, g, bottom_up=False):
    """
        To reduce memory consumption, build the graph line by line
    """
    if bottom_up:
        g[wline._id] = wline.parents
    else:
        g[wline._id] = wline.children

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
        i_graph(wline, _graph, bottom_up)
    return _graph

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

def write_semantics(call):
    return call in ["rmdir", "mkdir", "unlink", "write", "llseek", "open"]

def join(father, son):
    if son:
        if not son._id in father.children:
            father.children.append(son._id)
        if not father._id in son.parents:
            son.parents.append(father._id)

def update_dependency(w_line_to_update, w_line_target_parents):
    for parent in reversed(w_line_target_parents):
        clean_call = parent.clean_call
        if write_semantics(clean_call.call):
            join(parent, w_line_to_update)
            break

def sfs(workflow_lines):
    """
        FS dependency plus tid, pid ordering
    """
    generic_fs_dependency_sort(workflow_lines, True)

def weak_fs_dependency_sort(workflow_lines):
    """
        We implement the serialization algorithm based on
         "TBBT: Scalable and Accurate Trace Replay for File Server Evaluation"

        It deviates from the fs_dependency_order in such it does not depend on
        pid/fid ordering
    """
    generic_fs_dependency_sort(workflow_lines, False)

def generic_fs_dependency_sort(workflow_lines, sort_by_pidtid):

    def same_thread(w1, w2):
        return pidfidprocess(w1) == pidfidprocess(w2)

    def fs_obj(clean_call, pid_fid_to_path):

        if (clean_call.call == "mkdir") or (clean_call.call == "unlink") \
           or (clean_call.call == "rmdir"):
            filepath = clean_call.fullpath()
            parent = parent_path(filepath)
            return [filepath, parent]
        elif (clean_call.call == "stat") or (clean_call.call == "open") \
           or (clean_call.call == "write") or (clean_call.call == "read") \
           or (clean_call.call == "llseek"):
            return [clean_call.fullpath()]
        elif (clean_call.call == "fstat"):
            pidfid = (clean_call.pid, clean_call.fd())
            filepath = pid_fid_to_path[pidfid]
            return [filepath]
        else:
            raise Exception("unsupported operation " + str(clean_call))

    def update_session(wline, session_table):
        clean_call = wline.clean_call
        pidfd = (clean_call.pid, clean_call.fd())
        if not pidfd in session_table:
            session_table[pidfd] = []
        session_table[pidfd].append(wline)
        return pidfd

    if sort_by_pidtid:
        sort_by_pidfid(workflow_lines)

    lines_by_fs_obj = {}
    pid_fd_sessions = {}

    pid_fd_to_path = {}

    for w_line in workflow_lines:

        clean_call = w_line.clean_call

        if clean_call.fd_based():
            pidfd = update_session(w_line, pid_fd_sessions)

        if clean_call.call == "open":
            pid_fd_to_path[pidfd] = clean_call.fullpath()
        elif clean_call.call == "close":
            del pid_fd_to_path[pidfd]

        if not clean_call.call == "close":#see CLOSE_CASE below
            for obj in fs_obj(clean_call, pid_fd_to_path):
                if not obj in lines_by_fs_obj:
                    lines_by_fs_obj[obj] = Operations()
                lines_by_fs_obj[obj].append(w_line)

    for (obj, operations) in lines_by_fs_obj.iteritems():
        last_update_op = None
        for operation in operations:
            clean_call = operation.clean_call
            if last_update_op:
                if sort_by_pidtid:
                    if not same_thread(operation, last_update_op):
                        join(last_update_op, operation)
                else:
                    join(last_update_op, operation)
            if write_semantics(clean_call.call):
                last_update_op = operation

    session_counter = -1
    for (pidfid, operations) in pid_fd_sessions.iteritems():
        #note it's possible to have more than one open-to-close session for the
        #same pid_fd e.g:
        #pid=111 open("/foo") -> 4
        #pid=111 close(4)
        #pid=111 open("/baa") -> 4
        #pid=111 close(4)
        if not operations[0].clean_call.call == "open":
            raise Exception("Something got wrong ! We should start a session with a open syscall")

        for w_line in operations:
            if w_line.clean_call.call == "open":
                session_counter = session_counter + 1
            w_line.session_id = session_counter

    #CLOSE CASE: we keep operations sessions (from open to close).
    #we make close's parent its antecessor on session
    for (pidfid, operations) in pid_fd_sessions.iteritems():
        previous_op = None
        for operation in operations:
            if (operation.clean_call.call == "close"):
               #assuming a close cannot be the 0th on operations list
               #this code works
               if previous_op:
                   if not previous_op.clean_call.call == "close":
                       join(previous_op, operation)
            previous_op = operation

def conservative_sort(w_lines):
    #I guess cleaned calls are timestamp sorted TODO: check
    #I assume order information (parents and children) are empty lists
    def finished_before(wlines, current_pos, stamp):
        """ wlines are stamp-begin sorted, we return the last which finished
            before stamp begin. If there is no such wline, we return None
        """
        for pos in xrange(current_pos - 1, -1, -1):
            wline = wlines[pos]
            candidate_stamp = wline.clean_call.stamp()
            candidate_end = candidate_stamp[0] + candidate_stamp[1]
            stamp_begin = stamp[0]
            if (candidate_end < stamp_begin):
                return wline
        return None

    _l = len(w_lines)
    for pos in range(_l):
        if (pos % 1000 == 0):
            sys.stderr.write("pos: " + str(pos) + " len: " + str(_l) + "\n")
        current_wline = w_lines[pos]
        stamp = current_wline.clean_call.stamp()
        parent_wline = finished_before(w_lines, pos, stamp)
        if parent_wline:
            join(parent_wline, current_wline)

def pidfidprocess(wline):
    clean_call = wline.clean_call
    return (clean_call.pid, clean_call.tid, clean_call.pname)

def sort_by_pidfid(wlines):

    wlines_by_fidpidprocess = {}

    for wline in wlines:
        pfp = pidfidprocess(wline)
        if not pfp in wlines_by_fidpidprocess:
            wlines_by_fidpidprocess[pfp] = []
        wlines_by_fidpidprocess[pfp].append(wline)
        if (len(wlines_by_fidpidprocess[pfp]) > 1):
            father, son = wlines_by_fidpidprocess[pfp][-2], wlines_by_fidpidprocess[pfp][-1]
            join(father, son)
