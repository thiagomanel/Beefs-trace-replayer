import sys
from workflow import *
from bfs import *

if __name__ == "__main__":
    """
        usage: python $0 < workflow
    """
    sys.stdin.readline()#excluding head
    _graph = {}
    for line in sys.stdin:
        wline = WorkflowLine.from_json_safe(json.loads(line))
        print "\t".join([str(wline._id), str(len(wline.children))])
