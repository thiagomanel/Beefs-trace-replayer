import sys
from latency import *
from clean_trace import *

if __name__ == "__main__":
    """
    It receives the workflow input and output data and writes to stdout a 7-tuple
    for each command:
        (cmd_workflow_begin, cmd_workflow_end, replay_begin, replay_end, 
         delta_from_input, delta_from_replay, waiting_delay)
    time measured as microsends

    output data is 5-token format based on timeval struct:
         (cmd_begin_secs, cmd_being_usecs, cmd_end_secs, cmd_end_usecs, sleep_delay_usecs)
    """
    def out_stamps(out_line):
        tokens = out_line.split()
        begin = parse(tokens[0], tokens[1])
        end = parse(tokens[2], tokens[3])
        return begin, end

    def waiting_delay(out_line):
        return float(out_line.split()[-1])

    def in_stamps(traced_syscall):
        syscall = traced_syscall.split()
        stamp_tokens = syscall_timestamp(syscall).split("-")
        begin = long(stamp_tokens[0])
        end = begin + long(stamp_tokens[1])
        return begin, end

    def newest_parent(w_line, stamps):
        """ Returns parent_id for w_line's parent that terminates as last """
        parents_stamps = dict()
        for parent_id in w_line.parents:
            parents_stamps[parent_id] = stamps[parent_id]
        return max(parents_stamps.keys(), key=lambda x:parents_stamps[x][-1])#end stamp

    def parent_delta(parent_id, child_id, stamps):
        parent_begin, parent_end = stamps[parent_id]
        child_begin, child_end = stamps[child_id]
        return (child_begin - parent_end)

    replay_in_path = sys.argv[1]
    replay_out_path = sys.argv[2]

    with open(replay_in_path) as r_in_file:
        with open(replay_out_path) as r_out_file:
            r_in_file.readline()#excluding header

            id2w_line = {}

            input_stamps = {}
            output_stamps = {}

            for in_line in r_in_file:
                w_line = WorkflowLine(in_line.split())
                out_line = r_out_file.readline()

                current_id = w_line._id

                input_stamps[current_id] = in_stamps(w_line.syscall)
                output_stamps[current_id] = out_stamps(out_line)

                in_begin, in_end = input_stamps[current_id]
                out_begin, out_end = output_stamps[current_id]

                if w_line.parents:
                    parent_id = newest_parent(w_line, input_stamps)
                    delta_from_input = parent_delta(parent_id, current_id, input_stamps)
                    delta_from_replay = parent_delta(parent_id, current_id, output_stamps)
                else:#FIXME this root's children case is wrong it does not mean 0
                    delta_from_input = 0
                    delta_from_replay = 0

                waiting_dlay = waiting_delay(out_line)

                sys.stdout.write("\t".join([str(in_begin), str(in_end),
                                            str(out_begin), str(out_end),
                                            str(delta_from_input), str(delta_from_replay), 
                                            str(waiting_dlay)]) + "\n")
