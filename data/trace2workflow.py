import sys
from workflow import *

if __name__ == "__main__":
    """
       It converts from a cleaned data file to workflow data.

       Usage: python trace2workflow.py "wfs"|"c"|"sfs" < file.clean > output
            wfs and c are Zhu's fs dependency (we call it weak fs in code) and
            conservative polices, sfs is a modified zhu police using pid fid
            dependency
    """
    cleaned_calls = [CleanCall.from_str(line) for line in sys.stdin]
    w_lines = []
    for (_id, cleaned_call) in enumerate(cleaned_calls):
        w_lines.append(WorkflowLine(_id + 1, -1, [], [], cleaned_call))

    police = sys.argv[1]
    if police == "wfs":
        weak_fs_dependency_sort(w_lines)
    elif police == "c":
        conservative_sort(w_lines)
    elif police == "sfs":
        sfs(w_lines)
    else:
        sys.stderr.write("wrong parameter\n")
        exit(1)

    #json dumps cannot handle our data
    sys.stdout.write(str(len(w_lines)))
    for w_line in w_lines:
         #this json is different from default workflow  __str__ no \n lines
        try:
            json_str = json.dumps(w_line.json())
            sys.stdout.write("\n" + json_str.strip())
        except ValueError:
            sys.stderr.write(str(w_line.clean_call.stamp()))
            sys.exit(1)
