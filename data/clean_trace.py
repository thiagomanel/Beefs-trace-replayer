#!/usr/bin/python
import sys

HOME = "/home"

class CleanCall():

    def __init__(self, uid, pid, tid, pname, call, stamp, callargs, rvalue):
        self.uid = uid
        self.pid = pid
        self.tid = tid
        self.pname = pname
        self.call = call
        tokens = stamp.split("-")
        self.__stamp_begin = long(tokens[0])
        self.__stamp_elapsed = long(tokens[1])
        self.args = callargs
        self.rvalue = rvalue

    @classmethod
    def from_str(cls, _str):
        uid = _str.split("<uid=")[1].split("\>")[0]
        pid = _str.split("<pid=")[1].split("\>")[0]
        tid = _str.split("<tid=")[1].split("\>")[0]
        pname = _str.split("<pname=")[1].split("\>")[0]
        call = _str.split("<call=")[1].split("\>")[0]
        stamp = _str.split("<stamp=")[1].split("\>")[0]

        args = []
        arg_tokens = _str.split("<arg=")[1:]
        for arg_token in arg_tokens:
            args.append(arg_token.split("\>")[0])

        rvalue = _str.split("<rvalue=")[1].split("\>")[0]
        return CleanCall(uid, pid, tid, pname, call, stamp, args, rvalue)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return " ".join(["<uid="+self.uid+"\>",
                         "<pid="+self.pid+"\>",
                         "<tid="+self.tid+"\>", 
                         "<pname="+self.pname+"\>",
                         "<call="+self.call+"\>",
                         "<stamp="+self.__stamp_str__()+"\>"] + 
                         ["<arg="+arg+"\>" for arg in self.args] +
                         ["<rvalue="+self.rvalue+"\>"])

    def fullpath(self):
        if self.call == "mkdir" or self.call == "stat" or \
            self.call == "open" or self.call == "rmdir" \
            or self.call == "unlink" or self.call == "read" \
            or self.call == "write" or self.call == "llseek":
            return self.args[0]
        raise Exception("unsupported operation " + str(self))

    def stamp(self):
        return (self.__stamp_begin, self.__stamp_elapsed)

    def fd(self):
        if self.call == "open":
            return self.rvalue
        elif self.call == "fstat":
            return self.args[-1]
        elif (self.call == "read" or self.call == "write"):
            return self.args[1]
        elif self.call == "llseek":
            return self.args[1]
        elif self.call == "close":
            return self.args[0]
        raise Exception("unsupported operation " + str(self))

    def fd_based(self):
        return (self.call == "open") or (self.call == "fstat") or \
               (self.call == "read") or (self.call == "write") or \
               (self.call == "llseek") or (self.call == "close")

    def __stamp_str__(self):
        return "-".join(map(str, self.stamp()))

    def raw_str(self):
        return " ".join([self.uid, self.pid, self.tid, self.pname,
                         self.call, self.__stamp_str__()] + 
                         self.args + 
                         [self.rvalue])

"""
def pid(tokens):
    return tokens[1]

def parent_path(fullpath):
    return fullpath[:fullpath.rfind("/")]

def basename(fullpath):
    return fullpath[(fullpath.rfind("/") + 1):]
"""

def open_flags(clean_call):
    if clean_call.call == "open":
        return int(clean_call.args[1])
    raise Exception("unsupported operation " + str(clean_call))

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
def parent_path(fullpath):
    return fullpath[:fullpath.rfind("/")]

def basename(fullpath):
    return fullpath[(fullpath.rfind("/") + 1):]

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

    def open_full_path(cleaned_call):
        return cleaned_call.args[0]

    def error(tokens, error_msg):
        return " ".join(tokens) + " error: " + error_msg

    def between(stamp, begin, end):
        ge_begin = not (begin and (stamp < begin))#ge GreaterEquals
        le_end = not (end and (stamp > end))#le LessEquals
        return ge_begin and le_end

    def call(dirty_tokens):
        return dirty_tokens[4]

    def pid(tokens):
        return tokens[1]

    #these fd calls are necessary to avoid cleaning when
    #fd is unknow
    def fstat_fd(dirty_tokens):
        return dirty_tokens[-2]

    def rw_fd(dirty_tokens):
        return dirty_tokens[-3]

    def sys_llseek_fd(dirty_tokens):
        return dirty_tokens[-5]

    def open_fd(dirty_tokens):
        return dirty_tokens[-1]

    def close_fd(dirty_tokens):
        return dirty_tokens[-2]

    def syscall_timestamp(dirty_tokens):
        return dirty_tokens[5]

    #dirty, eh !
    clean_functions = {"sys_stat64":clean_stat,
                       "vfs_rmdir":clean_rmdir,
                       "sys_mkdir":clean_mkdir,
                       "vfs_unlink":clean_unlink,
                      }

    fd_functions = {"sys_fstat64":fstat_fd,
                    "sys_open":open_fd,
                    "sys_write":rw_fd,
                    "sys_read":rw_fd,
                    "sys_close":close_fd,
                    "sys_llseek":sys_llseek_fd,
                   }

    fd_based_operations = set(["sys_fstat64", "sys_write", "sys_read", "sys_close", "sys_llseek"])

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
                path = cleaned_call.args[0]
                if home_file(path):
                    out_collector.write(str(cleaned_call) + "\n")

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
                            out_collector.write(str(fstat_call) + "\n")
                        elif _call == "sys_write":
                            write_call = clean_rw(tokens, "write", _fullpath)
                            out_collector.write(str(write_call) + "\n")
                        elif _call == "sys_read":
                            read_call = clean_rw(tokens, "read", _fullpath)
                            out_collector.write(str(read_call) + "\n")
                        elif _call == "sys_llseek":
                            seek_call = clean_sys_llseek(tokens, _fullpath)
                            out_collector.write(str(seek_call) + "\n")
                        elif _call == "sys_close":
                            del pid_fd2opencall[pid_fd]
                            close_call = clean_close(tokens)
                            out_collector.write(str(close_call) + "\n")
            elif _call == "sys_open":
                pid_fd = (pid(tokens), open_fd(tokens))
                if pid_fd in pid_fd2opencall:
                    err_collector.write(error(tokens, "File descriptor is already in use") + "\n")
                else:
                    open_call = clean_open(tokens)
                    fullpath = open_full_path(open_call)
                    if home_file(fullpath):
                        pid_fd2opencall[pid_fd] = open_call
                        out_collector.write(str(open_call) + "\n")
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
    return CleanCall(tokens[0], tokens[1], tokens[2], tokens[3], "rmdir",
                     tokens[5], [full_path(tokens[7], tokens[8])], tokens[-1])


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
        args = [fullpath, tokens[-2]]
    else:
        args = [tokens[-2]]
    return CleanCall(tokens[0], tokens[1], tokens[2], tokens[3], "fstat",
                     tokens[5], args, tokens[-1])
        
def is_reg(tokens):
    for token in tokens:
        if "S_IFREG" in token:
            return True
    return False

def clean_sys_llseek(tokens, fullpath):
   #sys_llseek has both low and high offset (I'll check if in our traces they are always the same value
   #FIXME: we need to choose between low and high offsets
    """
    when
    0 9352 9352 (trivial-rewrite) sys_llseek 1319203801723656-31 7 4294967295 4294967290 SEEK_CUR 708
    then
    0 9352 9352 (trivial-rewrite) llseek 1319203801723656-31 7 4294967295 4294967290 SEEK_CUR 708

    when
    0 23506 23506 (localedef) sys_llseek 1319229169389520-32 3 0 0 SEEK_END 1279166
    then
    0 23518 23518 (localedef) llseek 1319229170557981-32 3 0 0 SEEK_END 1282656

    when
    1159 2205 2304 (firefox-bin) sys_llseek 1319203351781638-8 31 0 459120 SEEK_SET 459120
    then
    1159 2205 2304 (firefox-bin) llseek 1319203351781638-8 31 0 459120 SEEK_SET 459120
    """
    args = []
    args.append(fullpath)
    args.extend(tokens[-5:-1])
    return CleanCall(tokens[0], tokens[1], tokens[2], tokens[3], "llseek",
                     tokens[5], args, tokens[-1])

def clean_close(tokens):
    """
    when
    0 2413 2413 (udisks-daemon) sys_close 1319227059005785-541 7 0
    returns
    0 2413 2413 (udisks-daemon) sys_close 1319227059005785-541 7 0
    """
    return CleanCall(tokens[0], tokens[1], tokens[2], tokens[3], "close",
                     tokens[5], [tokens[-2]], tokens[-1])

def clean_rw(tokens, _call, fullpath):
    """
    when
    0 18462 18475 (java) sys_write 1319227079842169-123 (/ /local/pjd_test_beefs_version/bin/ /tmp/Queenbee.lg/ 11525 S_IFREG|S_IROTH|S_IRGRP|S_IWUSR|S_IRUSR 156812) 25 5 5
    returns
    0 18462 18475 (java) write 1319227079842169-123 25 5 5
    """
    args = []
    args.append(fullpath)
    args.extend(tokens[-3:-1])
    return CleanCall(tokens[0], tokens[1], tokens[2], tokens[3], _call,
                     tokens[5], args, tokens[-1])

def clean_open(tokens):
    #interesting line -> 0 940 940 (tar) sys_open 1319227153693893-147 /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5
    """
    when 
    0 940 940 (tar) sys_open 1319227153693893-147 /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5
    returns
     0 940 940 (tar) open 1319227153693893-147 /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5
    """
    #is it possible to get empty chars in basepath, to we re-join themFIXME basepath can be made of empty space, so tokens[7] is a bad idea
    basepath = " ".join(tokens[7:-3])
    _fullpath = full_path(tokens[6], basepath)
    args = []
    args.append(_fullpath)
    args.extend(tokens[-3:-1])
    return CleanCall(tokens[0], tokens[1], tokens[2], tokens[3], "open",
                     tokens[5], args, tokens[-1])

def clean_stat(tokens):
    """
     when
     65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 / /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0
     returns
     65534 1856 1867 (gmetad) stat 1319227151896626-113 /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0
    """
    return CleanCall(tokens[0], tokens[1], tokens[2], tokens[3], "stat",
                     tokens[5], [full_path(tokens[6], tokens[7])], tokens[-1])

def clean_mkdir(tokens):
    """
    when 
    65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 / /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17
    returns
    65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17
    """
    args = [full_path(tokens[6], tokens[7]), tokens[-2]]
    return CleanCall(tokens[0], tokens[1], tokens[2], tokens[3], "mkdir",
                     tokens[5], args, tokens[-1])

def clean_unlink(tokens):
    """
    when
    0 916 916 (rm) vfs_unlink 1319227061187713-10 (/ /local/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/lib/python2.5/lib-dynload/pyexpat.so -1 null -1) 0
    returns
    0 916 916 (rm) unlink 1319227061187713-10 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/lib/python2.5/lib-dynload/pyexpat.so 0
    """
    return CleanCall(tokens[0], tokens[1], tokens[2], tokens[3], "unlink",
                     tokens[5], [full_path(tokens[7], tokens[8])], tokens[-1])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        begin = long(sys.argv[1])
        end = long(sys.argv[2])
    else:
        begin, end = None, None

    clean(sys.stdin, Collector(sys.stdout), Collector(sys.stderr), begin, end)
