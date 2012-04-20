import sys
from workflow_objects import *
from clean_trace import *

if __name__ == "__main__":

    calls_with_size = ["write", "read"]

    def parse_pre_replay(line):
        tokens = line.split()
        return tokens[0], tokens[1]

    def update_file_pos(fileinfo, bytes_to_advance):
        fileinfo[0] = fileinfo[0] + bytes_to_advance

    def file_pos(fileinfo):
        return fileinfo[0]

    """
    It find save file sizes to pre_replay data
    Usage: python solve_pre_replay_fsize.py pre_replay_data replay_input > checked_pre_replay 2> checking_log
    # replay_input is original workflow data using /home diretories, for example, /home/patrickjem/.cache/google-chrome/Default/Cache/f_0038dd
    # pre_replay_data might have a diferente pathname, for example, /local/nfs_manel/patrickjem/.cache/google-chrome/Default/Cache/f_0038dd
    """
    file2safe_size = {}
    with open(sys.argv[1]) as pre_replay_data:
        for pre_replay_line in pre_replay_data:
            path, ftype = parse_pre_replay(pre_replay_line)
            if ftype == "f":
                file2safe_size["/home" + path[16:]] = -1#excluding the head, see comment above

    with open(sys.argv[2]) as replay_input:
        open_files = {}#pid_fd->pos, path
        replay_input.readline()#excluding header
        for workflow_line in replay_input:
            traced_line_tokens = WorkflowLine(workflow_line.split()).syscall.split()

            syscall = call(traced_line_tokens)

            if syscall == "open":
                to_replay_fullpath = syscall_fullpath(traced_line_tokens)
                if to_replay_fullpath in file2safe_size:
                    pid_fd = pid(traced_line_tokens), open_fd(traced_line_tokens)
                    if pid_fd in open_files:
                        raise Exception("Fuck, this fd is already open " +
                        str(pid_fd))
                    open_files[pid_fd] = [0, to_replay_fullpath]
            elif syscall in calls_with_size:
                #read 1319217168628597-20878 /home/thiagoepdc/.config/google-chrome/Safe 43 100 100
                to_replay_fullpath = syscall_fullpath(traced_line_tokens)
                if to_replay_fullpath in file2safe_size:
                    pid_fd = pid(traced_line_tokens), traced_line_tokens[-3]
                    fileinfo = open_files[pid_fd]
                    r_value = int(traced_line_tokens[-1])#amount of read or written bytes
                    update_file_pos(fileinfo, r_value)
                    if file2safe_size[to_replay_fullpath] < file_pos(fileinfo):
                        file2safe_size[to_replay_fullpath] = file_pos(fileinfo)
            elif syscall == "close":
                pid_fd = pid(traced_line_tokens), close_fd(traced_line_tokens)
                if pid_fd in open_files:
                    del open_files[pid_fd]

    for filename, size in file2safe_size.iteritems():
        if not size == -1:
            #from /home/manoelfmn/.macromedia/Flash_Player/macromedia.com/support/flashplayer/sys/settings.sol
            #to   /local/nfs_manel/manoelfmn/.macromedia/Flash_Player/macromedia.com/support/flashplayer/sys/settings.sol
            print "/local/nfs_manel" + filename[5:], "f", size
