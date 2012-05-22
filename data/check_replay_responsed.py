import sys
import json
from workflow import *

def actual_rvalue(out_line):
    return out_line.split()[-1]

def expected_rvalue(workflow_line):
    return workflow_line.clean_call.rvalue
    
def is_rw(workflow_line):
    call = workflow_line.clean_call.call
    return (call == "write") or (call == "read")

if __name__ == "__main__":
    """
    It checks replay actual responses against the expected ones for write
    and read operations
    """
    r_input_path = sys.argv[1]
    r_output_path = sys.argv[2]

    with open(r_input_path) as workflow_file:
        workflow_json = json.load(workflow_file)
        w_lines = [WorkflowLine.from_json(wline_json)\
                      for wline_json in workflow_json]

        with open(r_output_path) as r_output:
            r_output.readline()#it skips fake root line
            for w_line in w_lines:
                out_line = r_output.readline()
                if is_rw(w_line):
                    r_expected = expected_rvalue(w_line)
                    r_actual = actual_rvalue(out_line)
                    sys.stdout.write(" ".join([str(r_expected == r_actual),
                                        str(w_line._id),
                                        r_expected, r_actual,
                                        "# " + out_line.strip() + " #"]) + "\n")
