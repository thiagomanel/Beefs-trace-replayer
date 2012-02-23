import sys
from order_trace import *

def list2str(_list):
    if _list:
       return str(_list).replace("[", "").replace("]", "").replace(",", "")
    else:
       return "-"

def trace_line2workflowstr(line):
#1 0 [] 3 [2, 3, 2] 1159 16303 16318 (chrome) open 1319203757986598-1310 /home/thiagoepdc/.config/google-chrome/com.google.chrome.gUMVsk 32962 384 43
    n_parents = line[1]
    parents = line[2]
    n_children = line[3]
    children = line[4]
    syscall = line[5:]
    return " ".join([str(line[0])] + [str(n_parents)] + [list2str(parents)] + [str(n_children)] + [list2str(children)] + map(str, syscall)) 

if __name__ == "__main__":
    #python trace2workflow.py < file.clean > file.pidfid_order
    #FIXME do not print pidfid order result, pass them to fsdependency instead
    lines = sys.stdin.readlines()
    pidfid_lines = sorted(order_by_pidfid(lines), key=lambda line: line[0])#sort by _id
    fs_dep_lines = sorted(fs_dependency_order(pidfid_lines), key=lambda line: line[0])#sort by _id
    n_commands = len(fs_dep_lines)
    sys.stdout.write(str(n_commands) + "\n")
    for o_line in fs_dep_lines:
        sys.stdout.write(trace_line2workflowstr(o_line))
