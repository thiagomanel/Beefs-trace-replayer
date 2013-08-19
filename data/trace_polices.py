import sys
import json
from workflow import *

def clean_order(workflow_line):
    workflow_line.parents = []
    workflow_line.children = []
    return workflow_line

if __name__ == "__main__":
    """
       It applies an ordering police to a trace workflow, erasing any police
       already in place.

       Usage: python trace_polices.py "wfs"|"c" < worfklow.data > workflow.new.data
         wfs and c are Zhu's fs dependency (we call it weak fs in code) and conservative polices
    """
    sys.stdin.readline()#excluding head

    w_lines = [clean_order(wline) for wline in \
                [WorkflowLine.from_json(json.loads(line)) for line in sys.stdin]]

    policy = sys.argv[1]
    if policy == "wfs":
        weak_fs_dependency_sort(w_lines)
    elif policy == "c":
        conservative_sort(w_lines)
    elif policy == "sfs":
        sfs(w_lines)

    #we need a conservative check. i'm afraid of a single chaing
    #json dumps cannot handle our data
    sys.stdout.write(str(len(w_lines)))
    for w_line in w_lines:
        #this json layout is different from default workflow  __str__
        #no \n lines
        json_str = json.dumps(w_line.json())
        sys.stdout.write("\n" + json_str.strip())
