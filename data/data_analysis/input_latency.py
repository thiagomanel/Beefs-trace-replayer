import sys
import json
from workflow import *

if __name__ == "__main__":
    """
       Usage: python input_latenc.py < workflow_input > output
       It outputs a line for each input operation latency
       output format:
            syscall_name\tlatency
    """
    def workflow_entry(line):
        _json = json.loads(line)
        return WorkflowLine.from_json(_json)

    sys.stdin.readline()#exclude header
    for line in sys.stdin:
        _workflow = workflow_entry(line)
        syscall = _workflow.clean_call.call
        (begin, elapsed) = _workflow.clean_call.stamp()
        print "\t".join([syscall, str(elapsed)])
