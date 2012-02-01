import sys
import re

#syscall.open OK
#do_filp_open OK 
#syscall.close OK
#filp_close OK
#syscall.dup
#syscall.dup2 
#syscall.write OK
#syscall.read OK
#generic.fop.llseek OK
#kernel.function("SyS_llseek") OK
#syscall.fstat OK
#syscall.fstatfs OK
#syscall.lstat OK
#syscall.stat OK
#vfs_statfs OK
#syscall.statfs OK
#kernel.function("vfs_getxattr")
#syscall.getxattr
#kernel.function("vfs_removexattr")
#syscall.removexattr
#kernel.function("vfs_setxattr")
#syscall.setxattr
#syscall.lsetxattr
#kernel.function("vfs_listxattr")
#syscall.listxattr
#syscall.fgetxattr
#syscall.fremovexattr
#syscall.lremovexattr
#syscall.fsetxattr
#syscall.llistxattr
#syscall.flistxattr
#vfs_getattr OK
#kernel.function("vfs_mknod") OK
#syscall.mknod OK
#syscall.mkdir OK
#syscall.rename OK
#kernel.function("vfs_rmdir") OK
#syscall.rmdir OK
#syscall.symlink
#kernel.function("vfs_unlink") OK
#syscall.unlink OK
#syscall.readlink
#kernel.function("vfs_readdir") OK
#kernel.function("__generic_file_aio_read")
#kernel.function("generic_file_aio_write")
#syscall.mmap2
#syscall.munmap

CALLS = ["vfs_readdir",
         "vfs_unlink", 
         "vfs_rmdir", 
         "vfs_mknod", 
         "vfs_getattr", 
         "sys_stat",#sys_stat64
         "sys_lstat",#sys_lstat64
         "sys_fstat", #sys_fstat64
         "llseek", #we have both generic_file_llseek and sys_llseek
         "sys_read", 
         "sys_write", 
         "filp_close", 
         "sys_close", 
         "do_filp_open",
         "sys_open"]

if __name__ == "__main__":
    for line in sys.stdin:
        if not re.search("S_IFIFO|S_IFSOCK|S_IFBLK|S_IFCHR", line) and re.search("|".join(CALLS), line):
		print line.strip()
