import sys
import json
from workflow import *
from clean_trace import *

if __name__ == "__main__":
    """
       This scripts checks if conservative police code lead to a single chain,
       meaning that we have elementN as the only child of elementN -1 for the whole
       workflow.

       Usage: python check_conservative.py < worfklow.data
    """
    sys.stdin.readline()#excluding head
    w_lines = [WorkflowLine.from_json(json.loads(line)) for line in sys.stdin]

    for current_line in w_lines:
        parents = current_line.parents
        children = current_line.children
        if (not len(parents) == 1) or (not parents[0] == current_line._id - 1)\
            or (not len(children) == 1) or (not children[0] == current_line._id + 1):
            print "notchained", current_line._id, parents, children
