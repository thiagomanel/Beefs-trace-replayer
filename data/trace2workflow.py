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

    pidfid_lines = sorted(order_by_pidfid(cleaned_calls),
                             key=lambda line: line._id)#sort by _id

    fs_dep_lines = sorted(fs_dependency_order(pidfid_lines), 
                             key=lambda line: line._id)#sort by _id

    #json dumps cannot handle our data
    sys.stdout.write("[\n")
    sys.stdout.write(str(fs_dep_lines[0]))
    for w_line in fs_dep_lines[1:]:
        try:
            sys.stdout.write(",\n" + str(w_line))
        except ValueError:
            sys.stderr.write(str(w_line.clean_call))
            raise 
    sys.stdout.write("\n]")
