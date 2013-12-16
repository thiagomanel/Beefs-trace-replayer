import sys
import json
from workflow import *
from clean_trace import *

#ACCESS - OK
#RMDIR - OK
#FSSTAT -
#GETATTR - OK
#RENAME - OK
#LINK  -
#SYMLINK
#READDIR
#READDIRPLUS - OK
#REMOVE  - OK
#COMMIT - OK
#LOOKUP - OK
#READ - OK
#WRITE - OK
#READLINK
#CREAT - TODO
#SETATTR - OK
#MKDIR - OK
#MKNOD

def raw_to_workflow(lineid, rawline):

    def tokenize(line):
        new_tokens = []
        left_mark_off_tokens = line.split("<")[1:]
        for token in left_mark_off_tokens:
            new_tokens.append(token.split(">")[0])
        return new_tokens

    def to_call(tokens):
        def _id():
            return tokens[0].split()[0:3]
        def pname():
            return tokens[0][3]
        def call():
            return tokens[1]
        def stamp():
            begin = long(tokens[-3])
            end = long(tokens[-2])
            elapsed = end - begin
            return "-".join([tokens[-3], str(elapsed)])
            #return "-".join([tokens[-3], tokens[-2]])
        def args():
            return tokens[2:-3]
        def rvalue():
            return tokens[-1]

        callname = call()
        if callname in ["nfsd3_proc_fsstat", "nfsd3_proc_link",\
                        "nfsd3_proc_symlink","nfsd3_proc_readdir",\
                        "nfsd3_proc_readlink", "nfsd3_proc_creat",\
                        "nfsd3_proc_mknod"]:
            return None

        uid, pid, tid = _id()
        _args = args()
        if callname in ["nfsd3_proc_rmdir", "nfsd3_proc_remove",\
                        "nfsd3_proc_lookup", "nfsd3_proc_mkdir",\
                        "nfsd3_proc_readdirplus"]:
            _args = ["/".join(_args)]
        elif callname == "nfsd3_proc_rename":
            parent_old, parent_new, name_old, name_new  = _args
            fullpath_old = "/".join([parent_old, name_old])
            fullpath_new = "/".join([parent_new, name_new])
            _args = [fullpath_old, fullpath_new]
        elif callname == "nfsd3_proc_setattr":
            #just to mark we implemented setattr, no need to transform args
            pass

        return CleanCall(uid, pid, tid, pname(), callname, stamp(), _args,\
                         rvalue())

    tokens = tokenize(rawline)
    try:
        _call = to_call(tokens)
    except ValueError as e:
        print "error-> " + rawline
        raise e
    if _call:
        return WorkflowLine(lineid, -1, [], [], _call)
    else:
        return None

def join_setattr_probes(args_probe, path_probe):
    #joined line gets args from earlier call and path from current
    _args = args_probe.split()[-6:-1]
    _path = path_probe.split()[:-3]
    _stamp = path_probe.split()[-3:]
    return " ".join(_path + _args + _stamp)

if __name__ == "__main__":
    """
        Usage: $0 time_window_min < rawfile > workflow
    """
    #during collection we were not able to get the full setattr information
    #so, we have two seattr probes for a single call. One has the args:
# <0 15770 15770 (nfsd)> <nfsd3_proc_setattr> <null> <40> <0> <0> <0> <0>  <1386962495259405>
    #and the second, the full name:
#<0 15770 15770 (nfsd)> <nfsd3_proc_setattr> <fullname> <1386962495259405> <1386962495259441> <0>
    #We need to join them. We use the start timestamp to find related calls.

    time_window_min = int(sys.argv[1])
    window_usec = None
    first_stamp = None
    if (time_window_min > 0):
       window_usec = time_window_min * 60 * 1000000

    setattr_lines = {}
    id_wline = 1
    for line in sys.stdin:
        if "nfsd3_proc_setattr" in line:
            if "null" in line:
                start_stamp = line.split()[-1]
                setattr_lines[start_stamp] = line
                continue
            else:
                #here we join the two related lines
                start_stamp = line.split()[-3]
                args_line = setattr_lines[start_stamp]
                line = join_setattr_probes(args_line, line)

        w_line = raw_to_workflow(id_wline, line)
        if w_line:
            if window_usec:
                stamp_begin, elapsed = w_line.clean_call.stamp()
                if not first_stamp:
                    first_stamp = stamp_begin
                if (stamp_begin - first_stamp) > window_usec:
                    break

            id_wline = id_wline + 1
            json_str = json.dumps(w_line.json())
            sys.stdout.write(json_str.strip() + "\n")
