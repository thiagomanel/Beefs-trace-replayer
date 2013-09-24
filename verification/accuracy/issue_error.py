import sys

def parse(secs_str, u_secs_str):
    """ when 1331665020 738759 returns 1331665020738759 """
    usecs = long(secs_str) * 1000000
    if long(u_secs_str) > 999999:#padding problems
        raise Exception(" ".join(["padding problems", secs_str, u_secs_str]))
    return usecs + long(u_secs_str)

if __name__ == "__main__":
    """
        It computes the issue error: the time interval between
        the expected and actual dispatch timestamps;

        Usage: python $0 < replay.out > out
    """
    for line in sys.stdin:
        tokens = line.split()
        begin_stamp = parse(tokens[0], tokens[1])
        end_stamp = parse(tokens[2], tokens[3])
        schedule_stamp = parse(tokens[4], tokens[5])
        delay = float(tokens[6])

        issue_error = begin_stamp - (schedule_stamp + max(0, delay))

        print "\t".join([str(begin_stamp), str(end_stamp), str(schedule_stamp), str(delay), str(issue_error)])
