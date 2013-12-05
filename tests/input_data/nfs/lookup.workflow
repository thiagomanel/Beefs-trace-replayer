4
{"args": ["/lookup_parent"], "parents": [], "stamp": {"begin": 10.0, "elapsed": 1}, "call": "nfsd_proc_mkdir", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 1, "session_id": 1, "children": [2]}
{"args": ["/lookup_parent/dir_to_lookup"], "parents": [1], "stamp": {"begin": 20.0, "elapsed": 1}, "call": "nfsd_proc_mkdir", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 2, "session_id": 1, "children": [3]}
{"args": ["/lookup_parent/dir_to_lookup"], "parents": [2], "stamp": {"begin": 30.0, "elapsed": 1}, "call": "nfsd_proc_lookup", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 3, "session_id": 1, "children": [4]}
{"args": ["/thereisnosuchpath"], "parents": [3], "stamp": {"begin": 40.0, "elapsed": 1}, "call": "nfsd_proc_lookup", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 4, "session_id": 1, "children": []}
