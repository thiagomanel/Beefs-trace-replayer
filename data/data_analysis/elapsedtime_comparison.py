import sys
from latency import *
from clean_trace import *

if __name__ == "__main__":
    """
    It receives the workflow input and output data and writes to stdout a 4-tuple
    for each command:
        (cmd_workflow_begin, cmd_workflow_end, replay_begin, replay_end)
    time measured as microsends
    """
    def out_stamps(out_line):
        tokens = out_line.split()
        begin = parse(tokens[0], tokens[1])
        end = parse(tokens[2], tokens[3])
        return begin, end

    def in_stamps(in_line):
        syscall = WorkflowLine(in_line.split()).syscall.split()
        stamp_tokens = syscall_timestamp(syscall).split("-")
        begin = long(stamp_tokens[0])
        end = begin + long(stamp_tokens[1])
        return begin, end

    replay_in_path = sys.argv[1]
    replay_out_path = sys.argv[2]
    with open(replay_in_path) as r_in_file:
        with open(replay_out_path) as r_out_file:
            r_in_file.readline()#excluding header
            for in_line in r_in_file:
                out_line = r_out_file.readline()
                _in_stamps = in_stamps(in_line)
                _out_stamps = out_stamps(out_line)
                sys.stdout.write("\t".join([str(_in_stamps[0]), str(_in_stamps[1]),
                                            str(_out_stamps[0]), str(_out_stamps[1])]) + "\n")
    

