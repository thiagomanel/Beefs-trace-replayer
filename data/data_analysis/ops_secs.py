import sys
from workflow_objects import *

if __name__ == "__main__":
    """it outputs the number of operations within a timeframe e.g for a 5 secs
       timestamp:

       0 10
       5 0
       10 1
       
       Usage: python ops_secs.py ["w", "r"] us_timeframe filepath
       "w" for workflow data and r for raw data (actually any kind of sorted trace 
       if timestamp is the 6th token
    """
    def stamp(stamp_str):
        return long(stamp_str.split("-")[0])

    def timestamp(data_type, line):
        if data_type is "r":
            return stamp(line.split()[5])
        elif data_type is "w":
            return stamp(WorkflowLine(line.split()).syscall.split()[5])

    data_type = sys.argv[1]
    if not data_type in ["r", "w"]: raise Exception("we need data type, r or w")

    timeframe = int(sys.argv[2])
    filepath = sys.argv[3]
    frame_to_count = {}
    with open(filepath, 'r') as data:

        if data_type is "w":
            lines = data.readlines()[1:]
        else:
            lines = data.readlines()

        first_stamp = 0
        for line in lines:
            line_stamp = timestamp(data_type, line)
            if not first_stamp:
                first_stamp = line_stamp
            us_since_begin = line_stamp - first_stamp
            frame = us_since_begin / timeframe
            if not frame in frame_to_count:
                frame_to_count[frame] = 0
            frame_to_count[frame] = frame_to_count[frame] + 1

    for key in sorted(frame_to_count.keys()):
        print key, frame_to_count[key]
