import sys
import json
from workflow import *

if __name__ == "__main__":
    """ It outputs the operation and expected return value for
        replay input operations.

        Usage: python $0 < input_file > output
        Output format: operation_type\texpected_rvalue
    """
    sys.stdin.readline()#excluding header
    w_lines = [WorkflowLine.from_json(json.loads(line)) for line in sys.stdin]
    for w_line in w_lines:
        call_type = w_line.clean_call.call
        rvalue = w_line.clean_call.rvalue
        sys.stdout.write("\t".join([call_type, rvalue]) + "\n")
