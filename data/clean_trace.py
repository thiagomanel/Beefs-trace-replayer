#!/usr/bin/python
import sys

HOME = "/home"

#"vfs_rmdir",
#"vfs_getattr",
#"sys_lstat",#sys_lstat64
#"sys_fstat", #sys_fstat64

def clean(lines_tokens):

    def call(tokens):
        return tokens[4]

    def pid(open_tokens):
        return open_tokens[1]

    def open_fd(open_tokens):
        return open_tokens[-1]

    def open_full_path(cleaned_open):
        return cleaned_open.split()[6]

    def rw_fd(tokens):
        return tokens[-3]

    pid_fd2fullpath = {}
    cleaned = []

    for tokens in lines_tokens:
        _call = call(tokens)
        if _call == "sys_stat64":
            cleaned.append(clean_stat(tokens))
        elif _call == "sys_mkdir":
            cleaned.append(clean_mkdir(tokens))
        elif _call == "sys_unlink":
            cleaned.append(clean_unlink(tokens))
        elif _call == "sys_open":
            open_call = clean_open(tokens)
            pid_fd = (pid(open_call), open_fd(open_call))
            if pid_fd in pid_fd2fullpath:
                raise Exception(pid_fd, "is alread in use")
            pid_fd2fullpath[pid_fd] = open_call
            cleaned.append(open_call)
        elif _call == "sys_close":
            cleaned.append(clean_close(tokens))
        elif _call == "sys_write":
            pid_fd = (pid(tokens), rw_fd(tokens))
            pid_fd2fullpath[pid_fd] = open_call
            write_call = clean_rw(tokens, "write", open_full_path(open_call))
            cleaned.append(write_call)
        elif _call == "sys_read":
            pid_fd = (pid(tokens), rw_fd(tokens))
            pid_fd2fullpath[pid_fd] = open_call
            write_call = clean_rw(tokens, "read", open_full_path(open_call))
            cleaned.append(write_call)

    return cleaned

def full_path(pwdir, basepath):
    """
    fullpath is not mandatory at syscall level. but we can create fullpaths using pwd when basepath points to basenames
    """
    if not basepath.startswith('/'):
        return pwdir + basepath
    return basepath

def clean_close(tokens):
    """
    when
    0 2413 2413 (udisks-daemon) sys_close 1319227059005785-541 7 0
    returns
    0 2413 2413 (udisks-daemon) sys_close 1319227059005785-541 7 0
    """
    return " ".join(tokens[:4] + ["close"] + tokens[5:])

def clean_rw(tokens, _call, fullpath):
    """
    when
    0 18462 18475 (java) sys_write 1319227079842169-123 (/ /local/pjd_test_beefs_version/bin/ /tmp/Queenbee.lg/ 11525 S_IFREG|S_IROTH|S_IRGRP|S_IWUSR|S_IRUSR 156812) 25 5 5
    returns
    0 18462 18475 (java) write 1319227079842169-123 25 5 5
    """
    return " ".join(tokens[:4] + [_call] + [tokens[5]] + [fullpath] + tokens[-3:])

def clean_open(tokens):
    #interesting line -> 0 940 940 (tar) sys_open 1319227153693893-147 /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5
    """
    when 
    0 940 940 (tar) sys_open 1319227153693893-147 /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5
    returns
     0 940 940 (tar) open 1319227153693893-147 /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5
    """
    return " ".join(tokens[:4] + ["open"] + [tokens[5]] + [full_path(tokens[6], tokens[7])] + tokens[-3:])

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
    return " ".join(tokens[:4] + ["mkdir"] + [tokens[5]] + [full_path(tokens[6], tokens[7])] + tokens[-2:])

def clean_unlink(tokens):
    """
    when
    1159 2364 32311 (eclipse) sys_unlink 1318539134533662-8118  (/ /local/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0
    returns
    1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp 0
    """
    return " ".join(tokens[:4] + ["unlink"] + [tokens[5]] + [full_path(tokens[7], tokens[8])] + [tokens[-1]])
