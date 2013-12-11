import sys
import json
from workflow import *
from clean_trace import *

#ACCESS - OK
#RMDIR - OK
#FSSTAT
#GETATTR - OK
#RENAME - OK
#LINK
#SYMLINK
#READDIR
#READDIRPLUS
#REMOVE  - OK
#COMMIT - OK
#LOOKUP - OK
#READ - OK
#WRITE - OK
#READLINK
#CREAT -
#SETATTR - we missed the nfsd probes to get the name
#MKDIR
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
                        "nfsd3_proc_readdirplus", "nfsd3_proc_readlink",\
                        "nfsd3_proc_creat", "nfsd3_proc_setattr",\
                        "nfsd3_proc_mkdir", "nfsd3_proc_mknod"]:
            return None

        uid, pid, tid = _id()
        _args = args()
        if callname in ["nfsd3_proc_rmdir", "nfsd3_proc_remove",\
                        "nfsd3_proc_lookup"]:
            _args = ["/".join(_args)]
        elif callname == "nfsd3_proc_rename":
            parent_old, parent_new, name_old, name_new  = _args
            fullpath_old = "/".join([parent_old, name_old])
            fullpath_new = "/".join([parent_new, name_new])
            _args = [fullpath_old, fullpath_new]

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

if __name__ == "__main__":
    id_wline = 1
    for line in sys.stdin:
        w_line = raw_to_workflow(id_wline, line)
        if w_line:
            id_wline = id_wline + 1
            json_str = json.dumps(w_line.json())
            sys.stdout.write(json_str.strip() + "\n")
