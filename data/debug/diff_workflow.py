import sys
import json
sys.path.append("../")
from workflow import *

def load(path):
    w = []
    with open(path) as data:
        data.readline()#exclude header
        for line in data:
            w.append(WorkflowLine.from_json(json.loads(line)))
    return w

if __name__ == "__main__":
    w1 = load(sys.argv[1])
    w2 = load(sys.argv[2])
    for i in range(len(w1)):
        equals = (sorted(w1[i].children) == sorted(w2[i].children))
        if not equals:
                print "children", w1[i]._id, w1[i].children, w2[i].children
        equals = (sorted(w1[i].parents) == sorted(w2[i].parents))
        if not equals:
                print "parents", w1[i]._id, w1[i].parents, w2[i].parents
