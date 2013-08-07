import sys
import json
from workflow import *

def actual_rvalue(out_line):
    return out_line.split()[-2].strip()

if __name__ == "__main__":
    """
    It checks replay actual responses against the expected ones for write
    and read operations.
    Usage: python check_replay_responsed.py r_input_expected r_output
    """
    r_input_expected_path = sys.argv[1]
    r_output_path = sys.argv[2]

    with open(r_output_path) as r_output:
        r_output.readline()#it skips fake root line
        with open(r_input_expected_path) as r_input_expected:
            for expected_line in r_input_expected:

                expected_op = expected_line.split()[0].strip()
                expected = expected_line.split()[1].strip()

                actual = actual_rvalue(r_output.readline())
                if expected_op == "read" or expected_op == "write":
                    sys.stdout.write(" ".join([str(expected == actual),
                                               expected, actual]) + "\n")
                else:
                    sys.stdout.write("#\n")
