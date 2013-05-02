import sys
from output_latency import *
from clean_trace import *
from workflow import *

if __name__ == "__main__":
    """
        It receives the workflow input and output data and writes to stdout a 7-tuple
        for each command:
            (op, cmd_workflow_begin, cmd_workflow_end, replay_begin,
             replay_end, delta_from_input, delta_from_replay, waiting_delay)

        time measured as microseconds
    """
    def out_stamps(out_line):
        tokens = out_line.split()
        begin = parse(tokens[0], tokens[1])
        end = parse(tokens[2], tokens[3])
        return begin, end

    def waiting_delay(out_line):
        return float(out_line.split()[-1])

    def in_stamps(clean_call):
        begin, elapsed = clean_call.stamp()
        return begin, begin + elapsed

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

            #it seems odd but some replay input lines have bad formatted lines. e.g
            #71 2 70 60 1 108 1005 20784 20802 (firefox-bin) read 1319217113783416--49191262834 /home/antonio/.mozilla/firefox/epi74ttu.default/urlclassifier3.sqlite 27 16 16
            # which show a doubled "-" in timestamp 1319217113783416--49191262834
            # as they are very rare, we just skip this line and send a report to stderr

            for in_line in r_in_file:
                _json = json.loads(in_line)
                w_line = WorkflowLine.from_json(_json)

                out_line = r_out_file.readline()

                current_id = w_line._id
                try:
                    input_stamps[current_id] = in_stamps(w_line.clean_call)
                except ValueError:
                    sys.stderr.write("Error " + in_line + "\n")
                    continue

                output_stamps[current_id] = out_stamps(out_line)

                in_begin, in_end = input_stamps[current_id]
                out_begin, out_end = output_stamps[current_id]

                if w_line.parents:
                    try:
                        parent_id = newest_parent(w_line, input_stamps)
                    except KeyError:#It we had a ValueError before, parent is not available
                        sys.stderr.write("Error, parent not tracked " + in_line + "\n")
                        continue

                    delta_from_input = parent_delta(parent_id, current_id, input_stamps)
                    delta_from_replay = parent_delta(parent_id, current_id, output_stamps)
                else:#FIXME this root's children case is wrong it does not mean 0
                    delta_from_input = 0
                    delta_from_replay = 0

                waiting_dlay = waiting_delay(out_line)

                sys.stdout.write("\t".join([w_line.clean_call.call,
                                            str(in_begin), str(in_end),
                                            str(out_begin), str(out_end),
                                            str(delta_from_input), str(delta_from_replay),
                                            str(waiting_dlay)]) + "\n")
