import sys
from latency import *
from clean_trace import *

if __name__ == "__main__":
    """
    It receives the workflow input and output data and writes to stdout a 2-tuple
    for each command:
        (cmd_workflow_delay, replay_delay) time measured in microsends

    output data follows a 5-token format, delay being the 5th
    """
    def out_delay(out_line):
        return float(out_line.split()[-1])

    def out_stamps(out_line):
        tokens = out_line.split()
        begin = parse(tokens[0], tokens[1])
        end = parse(tokens[2], tokens[3])
        return begin, end
    
    def in_stamps(traced_syscall):
        syscall = traced_syscall.split()
        stamp_tokens = syscall_timestamp(syscall).split("-")
        begin = long(stamp_tokens[0])
        end = begin + long(stamp_tokens[1])
        return begin, end

    def newest_parent(w_line, w_lines_stamps):
        parents_stamps = dict()
        for parent_id in w_line.parents:
            parents_stamps[parent_id] = w_lines_stamps[parent_id]
        return max(parents_stamps.keys(), key=lambda x:parents_stamps[x])    

    replay_in_path = sys.argv[1]
    replay_out_path = sys.argv[2]

    with open(replay_in_path) as r_in_file:
        with open(replay_out_path) as r_out_file:
            r_in_file.readline()#excluding header

            w_line2begin = {}
            for in_line in r_in_file:
                w_line = WorkflowLine(in_line.split())
                in_begin, in_end = in_stamps(w_line.syscall)
                w_line2begin[w_line._id] = in_begin
                if w_line.parents:
                    parent_id = newest_parent(w_line, w_line2begin)
                    in_delay = in_begin - w_line2begin[parent_id]
                else:
                    in_delay = 0

                out_line = r_out_file.readline()
                out_dlay = out_delay(out_line)
                sys.stdout.write("\t".join([str(in_delay), str(out_dlay)]) + "\n")
