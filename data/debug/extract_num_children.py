import sys
import json
sys.path.append("../")
from workflow import *

if __name__ == "__main__":
    """ It outputs children length for each request.

        Usage: python $0 < input_file > output
        Output format: id\tnum_children
    """
    sys.stdin.readline()#excluding header
    for line in sys.stdin:
        w_line = WorkflowLine.from_json(json.loads(line))
        _id = w_line._id
        num_children = len(w_line.children)
        print "\t".join([str(_id), str(num_children)])
