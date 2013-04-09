import sys
from workflow import *
from bfs import *

def is_leaf(graph, node):#sugar
    return not children(graph, node)

def children(graph, node):#sugar
    try:
        return graph[node]
    except KeyError:
        sys.stdout.write("Fuck, a key error. node:" + str(node) + "\n")
        exit(1)

def i_longest_path_size(graph, node):
    level_counter = 0
    new_parent = None
    for p, n in bfs(graph, node):
        if (p != None) and (p != new_parent):
            level_counter = level_counter + 1
            new_parent = p
    return level_counter

def longest_path_size(graph, node):
    """
       Find the size of longest path in a tree
       Thee is represented as a dict {parent_id:children_ids_list}. See
       workflow.py to check graph building
    """
    if is_leaf(graph, node):
        return 0
    else:
        max_path = 0
        for child in children(graph, node):
            try:
                max_path = max(max_path, longest_path_size(graph, child))
            except RuntimeError:
                sys.stdout.write("stackoverflow root: " + str(node) + " child: " +
                                 str(child) + "\n")
                exit(1)
        return 1 + max_path

if __name__ == "__main__":
    """
        usage: python graph_metrics.py < workflow
    """
    sys.setrecursionlimit(2000000)
    sys.stdin.readline()#excluding head

    _graph = {}
    for line in sys.stdin:
        wline = WorkflowLine.from_json_safe(json.loads(line))
        i_graph(wline, _graph)

    if not _graph:
        sys.stdout.write("Problems on input data\n")
        exit(1)

    path_sizes = []
    for root_child in _graph[1]:
        path_sizes.append(i_longest_path_size(_graph, root_child))
    print path_sizes
