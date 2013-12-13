import sys
import json

if __name__ == "__main__":

    mk = {"args": ["/dir_to_mk"], "parents": [], "stamp": {"begin": 10.0, "elapsed": 1},
         "call": "nfsd_proc_mkdir", "rvalue": 0,
         "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"},
         "id": 1, "session_id": 1, "children": []}

    #look = {"args": ["/lookup_parent/dir_to_lookup"], "parents": [21],
    #       "stamp": {"begin": 210.0, "elapsed": 1}, "call": "nfsd_proc_lookup",
    #       "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"},
    #       "id": 22, "session_id": 1, "children": [23]}

    for i in range(1, 100):
        mk["id"] = i
        mk["args"] = ["/dir_to_mk" + str(i)]
        sys.stdout.write("\n" + json.dumps(mk).strip())

