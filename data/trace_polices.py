import sys
import json
from workflow import *
from clean_trace import *

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
    police = sys.argv[1]
    w_lines = [clean_order(wline) for wline in \
                [WorkflowLine.from_json(json.loads(line)) for line in sys.stdin]]

    if police == "wfs":
        new_lines = sorted(weak_fs_dependency_sort(w_lines),
                               key=lambda line: line._id)#sort by _id
    elif police == "c":
        new_lines = sorted(conservative_sort(w_lines), 
                             key=lambda line: line._id)#sort by _id

    #json dumps cannot handle our data
    sys.stdout.write("[\n")
    sys.stdout.write(str(new_lines[0]))
    for w_line in new_lines[1:]:
        try:
            sys.stdout.write(",\n" + str(w_line))
        except ValueError:
            sys.stderr.write(str(w_line.clean_call))
            raise 
    sys.stdout.write("\n]")
