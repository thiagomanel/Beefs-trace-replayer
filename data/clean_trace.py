#!/usr/bin/python
import sys

HOME = "/home"


#"vfs_unlink",
 #        "vfs_rmdir",
   #      "vfs_getattr",
    #     "sys_stat",#sys_stat64
     #    "sys_lstat",#sys_lstat64
      #   "sys_fstat", #sys_fstat64

def full_path(pwdir, basepath):
    """
    it is not mandatory to receive fullpath (at syscall level). but we can create fullpaths using pwd when basepath points to basenames
    """
    if not basepath.startswith('/'):
        return pwdir + basepath
    return basepath

def clean_stat(tokens):
    """
     when
     65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 / /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0
     returns
     65534 1856 1867 (gmetad) stat 1319227151896626-113 /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0
    """
    return " ".join(tokens[:4] + ["stat"] + [tokens[5]] + [full_path(tokens[6], tokens[7])] + [tokens[-1]])

def clean_mkdir(tokens):
    """
    when 
    65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 / /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17
    returns
    65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17
    """
    return " ".join(tokens[:4] + ["mkdir"] + [tokens[5]] + [full_path(tokens[6], tokens[7])] + [tokens[-2]] + [tokens[-1]])

def clean_unlink(tokens):
    """
    when
    1159 2364 32311 (eclipse) sys_unlink 1318539134533662-8118  (/ /local/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0
    returns
    1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp 0
    """
    return " ".join(tokens[:4] + ["unlink"] + [tokens[5]] + [full_path(tokens[7], tokens[8])] + [tokens[-1]])
