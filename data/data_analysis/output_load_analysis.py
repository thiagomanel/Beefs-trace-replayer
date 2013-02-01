#!/bin/bash
import sys

def parse(replay_out_line):

    (dispatch_begin_sec, dispatch_begin_us,
    dispatch_end_sec, dispatch_end_us,
    replay_delay,
    exp_value,
    actual_rvalue) = replay_out_line.split()

    return long(dispatch_begin_sec), long(dispatch_begin_us),\
           long(dispatch_end_sec), long(dispatch_end_us),\
           float(replay_delay),\
           int(exp_value),\
           int(actual_rvalue)\

def bin_offset(timestamp, first_stamp, bin_width):
    def bin_index():
        return (timestamp - first_stamp) / bin_width

    return first_stamp + (bin_index() * bin_width)

def emit_count(counter, offset):
    if not offset in counter:
        counter[offset] = 0
    counter[offset] = counter[offset] + 1

#counter functions return a {time_stamp:event_count} dict of the 
#number of running and dispatch operations by timestamp
def running_count(replay, time_window):
    replay_begin = replay[0][0]
    bin_counter = {}

    for replay_event in replay:
        dispatch_begin = replay_event[0]
        dispatch_end = replay_event[2]
        
        start_offset = bin_offset(dispatch_begin, replay_begin, time_window)
        end_offset = bin_offset(dispatch_end, replay_begin, time_window)

        for offset in range(start_offset, end_offset + 1):
            emit_count(bin_counter, offset)

    return bin_counter

def dispatch_count(replay, time_window):

    replay_begin = replay[0][0]
    bin_counter = {}

    for replay_event in replay:
        dispatch_begin = replay_event[0]
        offset = bin_offset(dispatch_begin, replay_begin, time_window)
        emit_count(bin_counter, offset)
    return bin_counter

if __name__ == "__main__":
    """
       It analyses replay output load
        Usage: python output_load_analysis.py < replay_out > analysis.out
    """
    replay_out = [parse(line) for line in sys.stdin]

    count = dispatch_count(replay_out, 1)
    _min = -1
    for key in sorted(count.keys()):
        if (_min == -1):
            _min = key
        print (key - _min), key, count[key], "dispatch"

    count = running_count(replay_out, 1)
    _min = -1
    for key in sorted(count.keys()):
        if (_min == -1):
            _min = key
        print (key - _min), key, count[key], "running"
