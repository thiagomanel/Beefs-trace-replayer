#!/usr/bin/python
import sys

HOME = "/home"
#"sys_lstat",
#sys_lstat64

def call(tokens):
    return tokens[4]

def pid(tokens):
    return tokens[1]

def parent_path(fullpath):
    return fullpath[:fullpath.rfind("/")]

def basename(fullpath):
    return fullpath[(fullpath.rfind("/") + 1):]

def open_fd(tokens):
    return tokens[-1]

def open_flags(tokens):
    return int(tokens[7])

def fstat_fd(tokens):
    return tokens[-2]

def rw_fd(tokens):
    return tokens[-3]

#FIXME FULLPATH IS NOT THE SAME COME FOR ALL OF THESE
def rw_fullpath(tokens):
    return tokens[-4]

def close_fd(tokens):
    return tokens[-2]

def syscall_timestamp(tokens):
    return tokens[5]

def syscall_fullpath(tokens):
    syscall = call(tokens)
    if syscall in ["read", "write"]:
        return rw_fullpath(tokens)
    elif syscall in ["unlink", "mkdir", "rmdir", "stat", "llseek", "fstat"]:
        return pathcall_fullpath(tokens)
    elif syscall in ["open"]:
         return tokens[6] 
    raise Exception("It is not possible to get full path from " + str(tokens)) 

#FIXME BOTH FD AND FULLPATH ARE AT INDEX 6 ?
def pathcall_fullpath(tokens):
    """
    unlink, mkdir, rmdir, stat and llseek are syscall calls receiving path as parameter.
    Fullpath has the same position in all of them
    """
    return tokens[6]

def llseek_fd(tokens):
    return tokens[6]

"""
  25 sys_readlink
     33 sys_statfs
    123 sys_lstat64
    491 sys_llseek
    798 generic_file_llseek -> it is important to us because write and read operation does not have the offset. llseek can change it
   1375 sys_stat64
   2260 vfs_rmdir -> it is moro common than sys_rmdir, so I use it.
   7532 vfs_readdir
  11078 sys_fstat64 -> the most of calls is related to fd=3, the standard error stream. I not sure if it goes on fs path, if not, it doesn't need to be replayed. A problem raises if the error streamwas redirect (dup'ed) to a file. If so, it seems we need to keep state to discover where this file is stored
  12257 vfs_getattr
  24517 sys_open
  25367 vfs_unlink
  28939 do_filp_open
  29313 filp_close
  29359 sys_close
  33193 sys_read
  50483 sys_write
"""

def home_file(fullpath):
    return fullpath.startswith(HOME)

class Collector():

    def __init__(self, delegate):
        self.delegate = delegate
        self.content = []
    def write(self, _str):
        if self.delegate:
            self.delegate.write(_str)
        else:
            self.content.append(_str)

    def readlines(self):
        if self.delegate:
            return self.delegate.readlines()
        return [line.strip() for line in self.content]

    def __len__(self):
        if self.delegate:
            return len(self.delegate)
        return len(self.content)

    def __getitem__(self, index):
        if self.delegate:
            return self.delegate[index]
        return self.content[index].strip()

def clean(lines, out_collector, err_collector, begin=None, end=None):
    """ It cleans lines out and appending cleaned lines to out_collector.
        Lines that cannot be cleaned are appended to err_collector.
        Lines earlier than begin and later than end are ignored.
    """

    def open_full_path(cleaned_open):
        return cleaned_open.split()[6]

    def error(tokens, error_msg):
        return " ".join(tokens) + " error: " + error_msg

    def between(stamp, begin, end):
        ge_begin = not (begin and (stamp < begin))#ge GreaterEquals
        le_end = not (end and (stamp > end))#le LessEquals
        return ge_begin and le_end

    #dirty, eh !
    clean_functions = {"sys_stat64":clean_stat,
                       "vfs_rmdir":clean_rmdir,
                       "sys_mkdir":clean_mkdir,
                       "vfs_unlink":clean_unlink,
                       "generic_file_llseek":clean_llseek
                      }

    fd_functions = {"sys_fstat64":fstat_fd,
                    "sys_open":open_fd,
                    "sys_write":rw_fd,
                    "sys_read":rw_fd,
                    "sys_close":close_fd,
                   }

    fd_based_operations = set(["sys_fstat64", "sys_write", "sys_read", "sys_close"])

    pid_fd2opencall = {}
    cleaned = []
    errors = []

    for line in lines:
        tokens = line.split()
        _call = call(tokens)
        try:
            _stamp = long(syscall_timestamp(tokens).split("-")[0])
        except (ValueError, IndexError):#I saw a missed-timestamp line, it causes a IndexError
            sys.stderr.write(" ".join(["problems on parsing", line, "\n"]))
            continue
        if between(_stamp, begin, end):
            if _call in clean_functions:
                cleaned_call = clean_functions[_call](tokens)
                if home_file(pathcall_fullpath(cleaned_call.split())):
                    out_collector.write(cleaned_call + "\n")
            elif _call in fd_based_operations:
                pid_fd = (pid(tokens), fd_functions[_call](tokens))
                if not pid_fd in pid_fd2opencall:
                    err_collector.write(error(tokens, "file descriptor not found") + "\n")
                else:
                    open_call = pid_fd2opencall[pid_fd]
                    _fullpath = open_full_path(open_call)
                    if home_file(_fullpath):
                        if _call == "sys_fstat64":
                            fstat_call = clean_fstat(tokens, fullpath)
                            out_collector.write(fstat_call + "\n")
                        elif _call == "sys_write":
                            write_call = clean_rw(tokens, "write", _fullpath)
                            out_collector.write(write_call + "\n")
                        elif _call == "sys_read":
                            read_call = clean_rw(tokens, "read", _fullpath)
                            out_collector.write(read_call + "\n")
                        elif _call == "sys_close":
                            del pid_fd2opencall[pid_fd]
                            close_call = clean_close(tokens)
                            out_collector.write(close_call + "\n")
            elif _call == "sys_open":
                pid_fd = (pid(tokens), open_fd(tokens))
                if pid_fd in pid_fd2opencall:
                    err_collector.write(error(tokens, "File descriptor is already in use") + "\n")
                else:
                    open_call = clean_open(tokens)
                    fullpath = open_full_path(open_call)
                    if home_file(fullpath):
                        pid_fd2opencall[pid_fd] = open_call
                        out_collector.write(open_call + "\n")
            else:
                err_collector.write(error(tokens, "unknow operation") + "\n")

def full_path(pwdir, basepath):
    """
    fullpath is not mandatory at syscall level. we can create fullpaths using pwd when basepath points to basenames
    """
    if not basepath.startswith('/'):
        return pwdir + basepath
    return basepath

def clean_rmdir(tokens):
    """
    when
    0 916 916 (rm) vfs_rmdir 1319227056527181-26 (/ /local/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_ 0  2982629) 0
    returns
    0 916 916 (rm) rmdir 1319227056527181-26 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_ 0
    """
    return " ".join(tokens[:4] + ["rmdir"] + [tokens[5]] + [full_path(tokens[7], tokens[8])] + [tokens[-1]])


def clean_fstat(tokens, fullpath):
    """
    when 
    65534 1856 1867 (gmetad) sys_fstat64 1319227151912074-154 5 0
    returns
    65534 1856 1867 (gmetad) fstat 1319227151912074-154 5 0
    or 
    65534 1856 1867 (gmetad) fstat 1319227151912074-154 fullpath 5 0
    if fullpath is available. Note that we keep fd anyway
    """
    if fullpath:
        return " ".join(tokens[:4] + ["fstat"] + [tokens[5]] + [fullpath] + tokens[6:])
    else:
        return " ".join(tokens[:4] + ["fstat"] + [tokens[5]] + tokens[6:])
        
def is_reg(tokens):
    for token in tokens:
        if "S_IFREG" in token:
            return True
    return False

def clean_llseek(tokens):
    """
    when
    0 940 940 (tar) generic_file_llseek 1319227140807676-6 (/ /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ /etc/group/ 1006 S_IFREG|S_IROTH|S_IRGRP|S_IWUSR|S_IRUSR 384707) 0 SEEK_CUR 0
    returns
    0 940 940 (tar) llseek 1319227140807676-6 /etc/group 1006 0 SEEK_CUR 0
    """
    _fullpath = full_path(tokens[7], tokens[8])
    if is_reg(tokens):#it seems we are adding a extra "/" to files. if we are sure if is a regular file we remove this
        if _fullpath.endswith("/"):
            _fullpath = _fullpath[:-1]
    return " ".join(tokens[:4] + ["llseek"] + [tokens[5]] + [_fullpath] + tokens[-3:])

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
    65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17
    """
    return " ".join(tokens[:4] + ["mkdir"] + [tokens[5]] + [full_path(tokens[6], tokens[7])] + tokens[-2:])

def clean_unlink(tokens):
    """
    when
    0 916 916 (rm) vfs_unlink 1319227061187713-10 (/ /local/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/lib/python2.5/lib-dynload/pyexpat.so -1 null -1) 0
    returns
    0 916 916 (rm) unlink 1319227061187713-10 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/lib/python2.5/lib-dynload/pyexpat.so 0
    """
    return " ".join(tokens[:4] + ["unlink"] + [tokens[5]] + [full_path(tokens[7], tokens[8])] + [tokens[-1]])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        begin = long(sys.argv[1])
        end = long(sys.argv[2])
    else:
        begin, end = None, None

    clean(sys.stdin, Collector(sys.stdout), Collector(sys.stderr), begin, end)
