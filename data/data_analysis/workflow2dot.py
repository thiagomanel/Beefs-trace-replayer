import sys
import json
from workflow import *

def workflow_entry(line):
    _json = json.loads(line)
    return WorkflowLine.from_json(_json)

def parse_children(workflow_line):
    parsed = []
    for child in workflow_line.children:
        parsed.append(str(workflow_line._id) + " -> " + str(child) + " ;")
    if not workflow_line.parents:
        parsed.append("0" " -> " + str(workflow_line._id) + " ;")
    return parsed   

if __name__ == "__main__":
    """
       It formats workflow data into .dot language
       Usage: python workflow2dot.py < workflow_input > output
    """
    # dot format
    # digraph graphname {
    #     a -> b -> c;
    #     b -> d;
    #  }
    sys.stdin.readline()#exclude header

    connections = []
    for line in sys.stdin:
        entry = workflow_entry(line)
        connections.extend(parse_children(entry))

    sys.stdout.write("digraph workflow {\n")
    for connection in connections:
        sys.stdout.write(connection + "\n")
    sys.stdout.write("}\n")
