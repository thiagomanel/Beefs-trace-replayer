import sys
import json
from workflow import *

def stamp(stamp_str):
   return long(stamp_str.split("-")[0])

def timestamp(line):
    _json = json.loads(line)
    _workflow = WorkflowLine.from_json(_json)
    _call = _workflow.clean_call
    return stamp(_call.stamp)

def bin_index(timestamp, first_stamp, bin_width):
    return (timestamp - first_stamp) / bin_width

def bin_begin(bin_index, first_stamp, bin_width):
    return first_stamp + (bin_index * bin_width)

if __name__ == "__main__":
    """
       Usage: python input_load_analysis.py us_bin_width filepath > out
    """
    bin_width = int(sys.argv[1])
    filepath = sys.argv[2]

    bin_counter = {}

    with open(filepath, 'r') as data:
        lines = data.readline()#excluding header
        first_stamp = None
        for line in data:
            line_stamp = timestamp(line)
            if not first_stamp:
                first_stamp = line_stamp
            b_index = bin_index(line_stamp, first_stamp, bin_width)
            b_begin  = bin_begin(b_index, first_stamp, bin_width)

            if not b_begin in bin_counter:
                bin_counter[b_begin] = 0
            bin_counter[b_begin] = bin_counter[b_begin] + 1

    _min = None
    for key in sorted(bin_counter.keys()):
        if not _min:
            _min = key
        print (key - _min), key, bin_counter[key]