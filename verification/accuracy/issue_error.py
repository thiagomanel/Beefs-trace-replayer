import sys
from workflow import *

def output_stamp(output_line):
    def parse(secs_str, u_secs_str):
        """ when 1331665020 738759 returns 1331665020738759 """
        usecs = long(secs_str) * 1000000
        if long(u_secs_str) > 999999:#padding problems
            raise Exception(" ".join(["padding problems", secs_str, u_secs_str]))
        return usecs + long(u_secs_str)

    tokens = output_line.split()
    begin = parse(tokens[0], tokens[1])
    end = parse(tokens[2], tokens[3])
    return begin, end

if __name__ == "__main__":
    """
        It computes the issue error: the time interval between
        the expected and actual dispatch timestamps;

        Usage: python $0 replay.workflow replay.out > out
    """
    workflow_path = sys.argv[1]
    replay_out = sys.argv[2]

    workflow = {}
    workflow_start = float("inf")
    with open(workflow_path, 'r') as data:
        lines = data.readline()#excluding header
        for line in data:
            _json = json.loads(line)
            wline = WorkflowLine.from_json(_json)
            begin, end = wline.clean_call.stamp()
            workflow[long(wline._id)] = wline
            workflow_start = min(workflow_start, begin)

    replay = {}
    replay_start = float("inf")
    with open(replay_out, 'r') as data:
        data.readline()
        count = 1
        for output_line in data:
            begin, end = output_stamp(output_line)
            replay[count] = (begin, end)
            replay_start = min(replay_start, begin)
            count = count + 1

    for i in range(1, len(workflow)):
        (r_begin, _) = replay[i]

        w_element = workflow[i]
        (w_begin, _) = w_element.clean_call.stamp()

        parent_id, r_parent_begin, w_parent_begin, r_delay, w_delay, E =\
                -1, -1, -1, -1, -1, -1

        if w_element.parents:
            parent_id = w_element.parents[0]
            (r_parent_begin, _) = replay[parent_id]

            parent = workflow[parent_id]
            (w_parent_begin, _) = parent.clean_call.stamp()
            r_delay = r_begin - r_parent_begin
            w_delay = w_begin - w_parent_begin
            E = r_delay - w_delay

        print "\t".join([str(i),\
                         str(parent_id),\
                         str(r_begin), str(w_begin),\
                         str(r_parent_begin), str(w_parent_begin),\
                         str(r_delay), str(w_delay),\
                         str(E)])
