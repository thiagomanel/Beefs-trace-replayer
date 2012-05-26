import sys
from workflow import *
from clean_trace import *

if __name__ == "__main__":

    calls_with_size = ["write", "read", "llseek"]

    def parse_pre_replay(line):
        def parse_path(line):
            return line.split("<path=")[1].split("/>")[0]
        def parse_ftype(line):
            return line.split("<ftype=")[1].split("/>")[0]

        return parse_path(line), parse_ftype(line)

    def update_file_pos(fileinfo, syscall, rvalue):
        if syscall in ["read", "write"]:
            fileinfo[0] = fileinfo[0] + rvalue
        elif syscall == "llseek":
            fileinfo[0] = rvalue
        else:
            raise Exception("Unsupported call ", syscall)

    def file_pos(fileinfo):
        return fileinfo[0]

    def workflow_pathname(pre_replay_pathname):
        """
            It converts from pre_replay paths to workflow paths, e,g 
            when /local/thiagoepdc/espadarte_nfs//home/patrickjem/.cache/google-chrome/Default/Cache/f_0038dd
            then /home/patrickjem/.cache/google-chrome/Default/Cache/f_0038dd
        """
        return pre_replay_pathname[pre_replay_pathname.find("/home"):]

    def lead_path(pre_replay_pathname):
        return pre_replay_pathname[:pre_replay_pathname.find("/home")]
        
    """
        It finds save file sizes to pre_replay data
        Usage: python solve_pre_replay_fsize.py pre_replay_data replay_input > checked_pre_replay 2> checking_log
        replay_input is original workflow data using /home diretories, for example:
            /home/patrickjem/.cache/google-chrome/Default/Cache/f_0038dd
        pre_replay_data might have a diferente pathname, for example:
            /local/thiagoepdc/espadarte_nfs//home/patrickjem/.cache/google-chrome/Default/Cache/f_0038dd
    """
    file2safe_size = {}
    _lead_path = None
    with open(sys.argv[1]) as pre_replay_data:
        for pre_replay_line in pre_replay_data:
            path, ftype = parse_pre_replay(pre_replay_line)
            if ftype == "f":
                file2safe_size[workflow_pathname(path)] = -1
            if not _lead_path:
                _lead_path = lead_path(path)

    with open(sys.argv[2]) as workflow_file:
        open_files = {}#pid_fd->pos, path

        workflow_json = json.load(workflow_file)
        for w_line in [WorkflowLine.from_json(wline_json) 
                      for wline_json in workflow_json]:

            clean_call = w_line.clean_call
            syscall = clean_call.call

            if syscall == "open":
                to_replay_fullpath = clean_call.fullpath()
                if to_replay_fullpath in file2safe_size:
                    pid_fd = clean_call.pid, clean_call.fd()
                    if pid_fd in open_files:
                        raise Exception("Fuck, fd is already open " + str(pid_fd))
                    open_files[pid_fd] = [0, to_replay_fullpath]

            elif syscall in calls_with_size:
                to_replay_fullpath = clean_call.fullpath()
                if to_replay_fullpath in file2safe_size:
                    pid_fd = clean_call.pid, clean_call.fd()
                    fileinfo = open_files[pid_fd]
                    #amount of read or written bytes or llseek pos
                    r_value = int(clean_call.rvalue)
                    update_file_pos(fileinfo, syscall, r_value)
                    if file2safe_size[to_replay_fullpath] < file_pos(fileinfo):
                        file2safe_size[to_replay_fullpath] = file_pos(fileinfo)

            elif syscall == "close":
                pid_fd = clean_call.pid, clean_call.fd()
                if pid_fd in open_files:
                    del open_files[pid_fd]

    for filename, size in file2safe_size.iteritems():
        if not size == -1:
            #adding the leading path back
            #from /home/patrickjem/.cache/google-chrome/Default/Cache/f_0038dd
            #to   /local/thiagoepdc/espadarte_nfs//home/patrickjem/.cache/google-chrome/Default/Cache/f_0038dd
            sys.stdout.write("\t".join(["<path="+ _lead_path + filename + "/>", "<ftype=f/>", "<fsize="+str(size)+"/>"]) + "\n") 
