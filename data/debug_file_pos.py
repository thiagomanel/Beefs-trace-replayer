import sys
from workflow_objects import *
from clean_trace import *

if __name__ == "__main__":
    """ We faced a problem of unexpected end of file. After a long run,
         our replay reaches the end of a file for an specific fd but replay
         input says there is data remaining.
         I guess two things might happen:
             1 - pre_replay data is not ok (file should be great) BTW - we can construct a
                 more complex pre_replayer and pre_replayer_checker to ensure all files have
                 a safe lenght 
             2 - we are messing with concurrent file descriptors to the same file (I checked and
                 it's true we have one fd open to write and other to read at the same time)
    """
    file_pos = {} #pid_fd:pos
    calls_with_size = ["write", "read"]

    with open(sys.argv[1]) as replay_input:
        for workflow_line in replay_input:
            traced_line_tokens = WorkflowLine(workflow_line.split()).syscall.split()
            syscall = call(traced_line_tokens)

            if syscall == "open":#here we initiate file.pos
                to_replay_fullpath = syscall_fullpath(traced_line_tokens)
                pid_fd = pid(traced_line_tokens), open_fd(traced_line_tokens)
                if pid_fd in file_pos:
                    raise Exception("Fuck, this fd is already open " + str(pid_fd))
                file_pos[pid_fd] = 0
                print workflow_line.strip(), "#" + str(file_pos[pid_fd])
            elif syscall in calls_with_size:#here we update file.pos
                #read 1319217168628597-20878 /home/thiagoepdc/.config/google-chrome/Safe 43 100 100
                to_replay_fullpath = syscall_fullpath(traced_line_tokens)
                pid_fd = pid(traced_line_tokens), traced_line_tokens[-3]
                r_value = int(traced_line_tokens[-1])#amount of read or written bytes
                file_pos[pid_fd] = file_pos[pid_fd] + r_value
                print workflow_line.strip(), "#" + str(file_pos[pid_fd])
            elif syscall == "close":
                pid_fd = pid(traced_line_tokens), close_fd(traced_line_tokens)
                if pid_fd in file_pos:
                    del file_pos[pid_fd]
