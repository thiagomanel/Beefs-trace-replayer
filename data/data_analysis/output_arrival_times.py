import sys
import json
from workflow import *
from output_latency import *
from clean_trace import *

if __name__ == "__main__":
    """
       Usage: python output_arrival_times.py < replay.out > output
       It outputs replayed requests begin stamp
    """
    def out_stamps(out_line):
        tokens = out_line.split()
        begin = parse(tokens[0], tokens[1])
        end = parse(tokens[2], tokens[3])
        return begin, end

    replay_in_path = sys.argv[1]
    replay_out_path = sys.argv[2]

    for out_line in sys.stdin:
        id2w_line = {}
        output_stamps = {}

        current_id = w_line._id
        output_stamps[current_id] = out_stamps(out_line)

        out_begin, out_end = output_stamps[current_id]

        sys.stdout.write("\t".join([w_line.clean_call.call,
                                        str(in_begin), str(in_end),
                                        str(out_begin), str(out_end),
                                        str(delta_from_input), str(delta_from_replay),
                                        str(waiting_dlay)]) + "\n")
