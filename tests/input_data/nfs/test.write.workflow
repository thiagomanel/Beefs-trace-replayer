3
{"args": ["/dir_to_mk"], "parents": [], "stamp": {"begin": 10.0, "elapsed": 1}, "call": "nfsd_proc_mkdir", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 1, "session_id": 1, "children": [2]}
{"args": ["/dir_to_mk/path_to_creat", "511"], "parents": [1], "stamp": {"begin": 60.0, "elapsed": 1}, "call": "nfsd_proc_creat", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 2, "session_id": 1, "children": [3]}
{"args": ["/dir_to_mk/path_to_creat", "4096", "0", "0"], "parents": [2], "stamp": {"begin": 80.0, "elapsed": 1}, "call": "nfsd_proc_write", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 3, "session_id": 1, "children": []}
