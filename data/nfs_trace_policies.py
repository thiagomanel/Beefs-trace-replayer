import sys
import json
from workflow import *

if __name__ == "__main__":
    """
       It applies an ordering police to a trace workflow, erasing any police
       already in place.

       Usage: python $0 "fs"|"c" time_window_min < worfklow.data > workflow.new.data
         fs and c are Zhu's fs dependency and conservative polices
    """
    w_lines = [WorkflowLine.from_json(json.loads(line)) for line in sys.stdin]

    policy = sys.argv[1]
    if policy == "fs":
        nfs_fs_sort(w_lines)
    elif policy == "c":
        conservative_sort(w_lines)

    sys.stdout.write(str(len(w_lines)))
    for w_line in w_lines:
        #this json layout is different from default workflow  __str__
        #no \n lines
        json_str = json.dumps(w_line.json())
        sys.stdout.write("\n" + json_str.strip())
