#!/usr/bin/python
import sys

HOME = "/home"


#"vfs_unlink",
 #        "vfs_rmdir",
  #       "vfs_mknod",
   #      "vfs_getattr",
    #     "sys_stat",#sys_stat64
     #    "sys_lstat",#sys_lstat64
      #   "sys_fstat", #sys_fstat64

def clean_mkdir(tokens):
    pass

def clean_unlink(tokens):
    """
    when
    1159 2364 32311 (eclipse) sys_unlink 1318539134533662-8118  (/ /local/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0
    returns
    1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp 0
    """
    if not tokens[8].startswith('/'):
        fullpath = tokens[7] + tokens[8]
    else:
        fullpath = tokens[8]

    return " ".join(tokens[:4] + ["unlink"] + [tokens[5]] + [fullpath] + [tokens[-1]])
