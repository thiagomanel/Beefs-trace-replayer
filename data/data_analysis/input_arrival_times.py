import sys
import json
from workflow import *
from clean_trace import *

if __name__ == "__main__":
    """
       Usage: python input_arrival_times.py < workflow > output
       It outputs traced requests begin stamps
    """
    arrival_times = []
    sys.stdin.readline()#exclude header
    for in_line in sys.stdin:
        _json = json.loads(in_line)
        w_line = WorkflowLine.from_json(_json)

        begin_stamp, elapse = w_line.clean_call.stamp()
        arrival_times.append(begin_stamp)

    sorted_arrival = sorted(arrival_times)
    for i in xrange(1, len(sorted_arrival)):
        inter_arrival = sorted_arrival[i] - sorted_arrival[i - 1]
        sys.stdout.write("\t".join([str(inter_arrival)]) + "\n")
