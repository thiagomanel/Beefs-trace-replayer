import sys
from workflow import *
from clean_trace import *

if __name__ == "__main__":
    """
       It converts from a cleaned data file to workflow data.

       Usage: python trace2workflow.py "wfs"|"c" < file.clean > output
            wfs and c are Zhu's fs dependency (we call it weak fs in code) and
            conservative polices
    """
    lines = sys.stdin.readlines()
    cleaned_calls = [CleanCall.from_str(line) for line in lines]
    workflow_lines = []
    for (_id, cleaned_call) in enumerate(cleaned_calls):
        workflow_lines.append(WorkflowLine(_id + 1, [], [], cleaned_call))

    police = sys.argv[1]
    if police == "wfs":
         new_lines = weak_fs_dependency_sort(w_lines)
    elif police == "c":
        new_lines = conservative_sort(w_lines)

    #json dumps cannot handle our data
    sys.stdout.write(str(len(new_lines)))
    for w_line in new_lines:
         #this json is different from default workflow  __str__ no \n lines
         json_str = json.dumps(w_line.json())
         sys.stdout.write("\n" + json_str.strip())
