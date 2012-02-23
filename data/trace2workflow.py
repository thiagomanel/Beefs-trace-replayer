import sys
from order_trace import *

if __name__ == "__main__":
    #python order_trace.py < file.clean > file.pidfid_order
    #FIXME do not print pidfid order result, pass them to fsdependency instead
    lines = sys.stdin.readlines()
    pidfid_lines = sorted(order_by_pidfid(lines), key=lambda line: line[0])#sort by _id
    fs_dep_lines = sorted(fs_dependency_order(pidfid_lines), key=lambda line: line[0])#sort by _id
    for o_line in fs_dep_lines:
        sys.stdout.write(" ".join(map(str, o_line)))
