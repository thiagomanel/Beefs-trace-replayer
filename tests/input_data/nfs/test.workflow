13
{"args": ["/", "dir_to_create"], "parents": [], "stamp": {"begin": 10.0, "elapsed": 1}, "call": "nfsd_proc_mkdir", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 1, "session_id": 1, "children": [2]}
{"args": ["/dir_to_mk"], "parents": [1], "stamp": {"begin": 20.0, "elapsed": 1}, "call": "nfsd_proc_readdir", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 2, "session_id": 1, "children": [3]}
{"args": ["/dir_to_readdirplus"], "parents": [2], "stamp": {"begin": 30.0, "elapsed": 1}, "call": "nfsd_proc_mkdir", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 3, "session_id": 1, "children": [4]}
{"args": ["/dir_to_readdirplus"], "parents": [3], "stamp": {"begin": 40.0, "elapsed": 1}, "call": "nfsd_proc_readdirplus", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 4, "session_id": 1, "children": [5]}
{"args": ["/dir_to_readdirplus"], "parents": [4], "stamp": {"begin": 50.0, "elapsed": 1}, "call": "nfsd_proc_rmdir", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 5, "session_id": 1, "children": [6]}
{"args": ["/dir_to_mk/", "path_to_creat", "552"], "parents": [5], "stamp": {"begin": 60.0, "elapsed": 1}, "call": "nfsd_proc_creat", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 6, "session_id": 1, "children": [7]}
{"args": ["/dir_to_mk/path_to_creat", "0"], "parents": [6], "stamp": {"begin": 70.0, "elapsed": 1}, "call": "nfsd_proc_access", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 7, "session_id": 1, "children": [8]}
{"args": ["/dir_to_mk/path_to_creat", "4096", "0", "0"], "parents": [7], "stamp": {"begin": 80.0, "elapsed": 1}, "call": "nfsd_proc_write", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 8, "session_id": 1, "children": [9]}
{"args": ["/dir_to_mk/path_to_creat", "4096", "0", "0"], "parents": [8], "stamp": {"begin": 90.0, "elapsed": 1}, "call": "nfsd_proc_read", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 9, "session_id": 1, "children": [10]}
{"args": ["/dir_to_mk/path_to_creat", "/dir_to_mk/link"], "parents": [9], "stamp": {"begin": 100.0, "elapsed": 1}, "call": "nfsd_proc_link", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 10, "session_id": 1, "children": [11]}
{"args": ["/dir_to_mk/link", "4096"], "parents": [10], "stamp": {"begin": 110.0, "elapsed": 1}, "call": "nfsd_proc_readlink", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 11, "session_id": 1, "children": [12]}
{"args": ["/dir_to_mk", "/dir_to_mk_renamed"], "parents": [11], "stamp": {"begin": 120.0, "elapsed": 1}, "call": "nfsd_proc_rename", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 12, "session_id": 1, "children": [13]}
{"args": ["/dir_to_mk_renamed", "/dir_to_mk_renamed_sl"], "parents": [12], "stamp": {"begin": 130.0, "elapsed": 1}, "call": "nfsd_proc_symlink", "rvalue": 0, "caller": {"tid": "0", "pid": "0", "uid": "0", "exec": "(nfsd)"}, "id": 13, "session_id": 1, "children": []}
