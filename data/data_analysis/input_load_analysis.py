import sys
from workflow_objects import *

if __name__ == "__main__":
    """
       Usage: python input_load_analysis.py ["w", "r"] first_stamp us_bin_width filepath machine_name
       "w" for workflow data and r for raw data (actually any kind of sorted trace 
       if timestamp is the 6th token

       It outputs the number of operations within a bin_width e.g for a 5 secs
       timestamp:
           1319203757986598 5 machine_name
           1319203832986598 16 machine_name
           1319204032986598 301 machine_name
           1319204037986598 106 machine_name
    """
    def stamp(stamp_str):
        return long(stamp_str.split("-")[0])

    def timestamp(data_type, line):
        if data_type is "r":
            return stamp(line.split()[5])
        elif data_type is "w":
            return stamp(WorkflowLine(line.split()).syscall.split()[5])

    def bin_index(timestamp, first_stamp, bin_width):
        return (timestamp - first_stamp) / bin_width

    def bin_begin(bin_index, first_stamp, bin_width):
        return first_stamp + (bin_index * bin_width)

    data_type = sys.argv[1]
    if not data_type in ["r", "w"]: raise Exception("we need data type, r or w")

    first_stamp = long(sys.argv[2])
    bin_width = int(sys.argv[3])
    filepath = sys.argv[4]
    machine_name = sys.argv[5]

    bin_counter = {}

    with open(filepath, 'r') as data:

        if data_type is "w":
            lines = data.readline()#excluding header

        for line in data:
            line_stamp = timestamp(data_type, line)
            b_index = bin_index(line_stamp, first_stamp, bin_width)
            b_begin  = bin_begin(b_index, first_stamp, bin_width)

            if not b_begin in bin_counter:
                bin_counter[b_begin] = 0
            bin_counter[b_begin] = bin_counter[b_begin] + 1

    for key in sorted(bin_counter.keys()):
        print key, bin_counter[key], machine_name
