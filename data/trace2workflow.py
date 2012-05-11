import sys
from workflow import *
from clean_trace import *

if __name__ == "__main__":
    """
       It converts from a cleaned data file to workflow data. To do so, input is ordered
       using pid fid order and fs dependency algorithms.

       Usage: python trace2workflow.py < file.clean > file.pidfid_order
    """
    #FIXME do not print pidfid order result, pass them to fsdependency instead
    lines = sys.stdin.readlines()
    cleaned_calls = [CleanCall.from_str(line) for line in lines]

    pidfid_lines = sorted(order_by_pidfid(cleaned_calls), key=lambda line: line._id)#sort by _id
    sys.stderr.write("pid fid order done\n")

    fs_dep_lines = sorted(fs_dependency_order(pidfid_lines), key=lambda line: line._id)#sort by _id
    sys.stderr.write("fs dep order done\n")

    n_commands = len(fs_dep_lines)
    sys.stdout.write(str(n_commands) + "\n")
    for o_line in fs_dep_lines:
        sys.stdout.write(str(o_line) + "\n")
