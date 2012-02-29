import sys
from bfs import *

def graph(workflow_lines):
    """ 
        it builds a graph based on replay workflow data. On this map-based graph, node id
        is the key and the arcs is the value as a list of ids
        trace workflow excerpt
        1 0 - 3 2 3 2 1159 16303 16318 (chrome) open 1319203757986598-1310 /home/thiagoepdc/.config/google-chrome/com.google.chrome.gUMVsk 32962 384 43
        2 2 1 1 1 3 1159 16303 16318 (chrome) fstat 1319203757987999-87 /home/thiagoepdc/.config/google-chrome/com.google.chrome.gUMVsk 43 0
    """
    #FIXME REPLACE BY A CALL TO workflow_objects module
    def id_and_arcs(tokens):
        _id = int(tokens[0])
        n_parents = int(tokens[1])
        parents = []
        if n_parents:
            parents = [int(parent) for parent in tokens[2:2 + n_parents]]
        n_children = 0
        if n_parents > 1:
            n_children_pos = 2 + n_parents
        else: 
            n_children_pos = 3
        n_children = int(tokens[n_children_pos])
        children = []
        if n_children:
            children = [int(child) for child in tokens[n_children_pos + 1:n_children_pos + 1 + n_children]]
        return (_id, n_parents, parents, n_children, children)

    nodes = [id_and_arcs(line.split()) for line in workflow_lines]
    _graph = {}
    for node in nodes:
        node_id = node[0]
        parents = node[2] 
        _graph[node_id] = parents
    return _graph

if __name__ == "__main__":
    lines = sys.stdin.readlines()[1:]
    g = graph(lines)
    for node in bfs(g, 36657):
        print node[0], node[1]

