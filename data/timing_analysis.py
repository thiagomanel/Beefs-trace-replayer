import sys
import workflow

def bin_index(timestamp, first_stamp, bin_width):
    return (timestamp - first_stamp) / bin_width

def bin_begin(bin_index, first_stamp, bin_width):
    return first_stamp + (bin_index * bin_width)

def stamp(entry):
    return entry.clean_call.stamp()

if __name__ == "__main__":

    """ 
       It analyses trace pressure, number of event per time.
       Usage: < workflow_input us_time_window
    """
    def parse(line):
        entry = json.loads(line)
        return WorkflowLine.from_json(entry)

    events_by_bin = {}
    us_time_window = long(sys.argv[1])

    for line in sys.stdin:
        start = None
        for line in workflow_file:
            entry = parse(line)
            begin, elapsed = stamp(entry)
            if not start:
                start = begin
            i_bin = bin_index(begin, start, us_time_window)
            offset_bin = bin_begin(i_bin, start, us_time_window)
            if not offset_bin in events_by_bin:
                events_by_bin[offset_bin] = 0
            events_by_bin[offset_bin] = events_by_bin[offset_bin] + 1

    for offset in events_by_bin:#it might been out of order
        print offset, events_by_bin[offset]
