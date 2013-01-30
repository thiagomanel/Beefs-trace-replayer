import sys
import json
from workflow import *

if __name__ == "__main__":
    """
       Usage: python arrival_times.py < workflow_input > output

       It outputs the begin stamp of each workflow input data
    """
    def begin(call):
        return call.stamp()[0]

    def workflow_entry(line):
        _json = json.loads(line)
        return WorkflowLine.from_json(_json)

    sys.stdin.readline()#exclude header
    for line in sys.stdin:
        _workflow = workflow_entry(line)
        _call = _workflow.clean_call
        print begin(_call)#assuming id is also begin stamp order, we need to check
