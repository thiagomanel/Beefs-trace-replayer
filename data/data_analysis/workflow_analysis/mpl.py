import sys
from workflow import *
from clean_trace import *

__BEGIN__ = True

def mpl(request_tuples):
    #we assume timestamp sorted tuples
    concurrent_request_ids = set()
    mpl = 0

    for request in request_tuples:
        (workflow_id, request_type, stamp) = request
        if (request_type is __BEGIN__):
            concurrent_request_ids.add(workflow_id)
            mpl = max(mpl, len(concurrent_request_ids))
        else:
            concurrent_request_ids.remove(workflow_id)

    return mpl

def win_mpl(request_tuples):
    #we assume timestamp sorted tuples
    #FIXME: refactor. in window based, we can have the end of a request without
    #its beggining tuple. I don't want to add a if in map.remove because it
    #can hide key_error bugs
    concurrent_request_ids = set()
    mpl = 0

    for request in request_tuples:
        (workflow_id, request_type, stamp) = request
        if (request_type is __BEGIN__):
            concurrent_request_ids.add(workflow_id)
            mpl = max(mpl, len(concurrent_request_ids))
        else:
            if workflow_id in concurrent_request_ids:
               concurrent_request_ids.remove(workflow_id)
            else:
                #here is the situation we hand just the end tuple in the map
                #we can have an by-one-error
                mpl = max(mpl, len(concurrent_request_ids) + 1)

    return mpl

def requests_from_trace_input(line):
    w_line = WorkflowLine.from_json_safe(json.loads(in_line))
    begin_stamp, elapsed = w_line.clean_call.stamp()
    request_begin = (w_line._id, __BEGIN__, begin_stamp)
    request_end = (w_line._id, not __BEGIN__, begin_stamp + elapsed)
    return (request_begin, request_end)

def group_request_by_window(requests, us_window):
    by_window = {}
    first_request = requests[0]
    _, _, stamp = first_request
    last_stamp = stamp
    by_window[last_stamp] = []

    for request in requests:
        _id, is_begin_request, stamp = request
        if (stamp) > (last_stamp + us_window):
            last_stamp = last_stamp + us_window
            by_window[last_stamp] = []
        by_window[last_stamp].append(request)

    return by_window

def requests_from_trace_output(_id, line):

    def parse(secs_str, u_secs_str):
    #FIXME: it's duplicated in output_latency but we are missing a dependecy to
    #workflow_objects, so a copied it here
        """when 1331665020 738759 returns 1331665020738759"""
        usecs = long(secs_str) * 1000000
        if long(u_secs_str) > 999999:#padding problems
            raise Exception(" ".join(["padding problems", secs_str, u_secs_str]))
        return usecs + long(u_secs_str)

    def stamps():
        tokens = line.split()
        begin = parse(tokens[0], tokens[1])
        end = parse(tokens[2], tokens[3])
        return begin, end

    begin_stamp, end_stamp = stamps()
    request_begin = (_id, __BEGIN__, begin_stamp)
    request_end = (_id, not __BEGIN__, end_stamp)
    return (request_begin, request_end)

if __name__ == "__main__":
    """
        It defines mpl for input data. We considere response time values equal
        to captured data.
        Usage: python $0 [in, out] [max, by_window] < file > file2
    """
    #TODO: we can give mpl by a time window
    request_tuples = []
    tracein_or_traceout = sys.argv[1]
    mode = sys.argv[2]

    if tracein_or_traceout == "in":
        sys.stdin.readline()#excluding header
        for in_line in sys.stdin:
            r_begin, r_end = requests_from_trace_input(in_line)
            request_tuples.append(r_begin)
            request_tuples.append(r_end)
    elif tracein_or_traceout == "out":
        counter = 1
        for in_line in sys.stdin:
            r_begin, r_end = requests_from_trace_output(counter, in_line)
            request_tuples.append(r_begin)
            request_tuples.append(r_end)
            counter = counter + 1
    else:
        sys.stderr.write("invalid parameter\n")
        exit(1)

    sorted_tuples = sorted(request_tuples, key=lambda request: request[2])#sort by timestamp
    if mode == "max":
        print mpl(sorted_tuples)
    elif mode == "by_window":
        req_bins = group_request_by_window(sorted_tuples, 1000000)
        for _bin in req_bins:
            print _bin, win_mpl(req_bins[_bin])
