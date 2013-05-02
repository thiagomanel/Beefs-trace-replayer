import sys
from clean_trace import *

def latency(replay_output_line):
    tokens = replay_output_line.split()
    begin = parse(tokens[0], tokens[1])
    end = parse(tokens[2], tokens[3])
    return end - begin

def parse(secs_str, u_secs_str):
    """when 1331665020 738759 returns 1331665020738759"""
    usecs = long(secs_str) * 1000000
    if long(u_secs_str) > 999999:#padding problems
        raise Exception(" ".join(["padding problems", secs_str, u_secs_str]))
    return usecs + long(u_secs_str)

if __name__ == "__main__":
    """"
         Usage: python latency.py replay_output replay.data > latency.out
         It gives the per-operation latency based on replayer output e.g
           1331666684 740701 1331666684 740702
           1331666684 740792 1331666684 740797
           1331666684 747064 1331666684 747068
        It also output syscall type if replay_data is available
        For the above excerpt we have e.g
           1 read
           5 read
           4 close

    """
    replay_output = open(sys.argv[1])
    with open(sys.argv[1]) as replay_output:
        with open(sys.argv[2]) as replay_input:
            replay_input.readline()#discarding header
            replay_output.readline()
            for r_output_line in replay_output:
                r_input = replay_input.readline()
                _latency = latency(r_output_line)
                _syscall = call(WorkflowLine(r_input.split()).syscall.split())
                sys.stdout.write("\t".join([str(_latency), _syscall]) + "\n")
