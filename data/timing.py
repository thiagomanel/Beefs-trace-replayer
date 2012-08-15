import json
import sys
from bfs import *
from workflow import *

if __name__ == "__main__":
    """
       Usage: python timing.py workflow_path > new_workflow
    """
    def parse(line):
        entry = json.loads(line)
        return WorkflowLine.from_json(entry)

    def stamp(workflow_entry):
        stamp = workflow_entry.clean_call.stamp.split("-")
        return float(stamp[0]), long(stamp[1])

    def update_stamp(workflow_entry, workflow):

        def check_new_begin(new_begin, entry):
            old_entry_begin, old_entry_elapsed = stamp(entry)
            if old_entry_begin <= new_entry_begin:
                sys.stderr.write("new begin=%d is latter than old=%d id=%s" \
                                  % (new_entry_begin, old_entry_begin,
                                     workflow_entry._id))
                exit(1)
            
        parent_id = workflow_entry.parents[0]._id
        parent = workflow[parent_id]
        parent_begin, parent_elapsed = stamp(parent)

        new_entry_begin = parent_begin + parent_elapsed
        check_new_begin(new_entry_begin, workflow_entry)

        old_begin, old_elapsed = stamp(entry)
        workflow_entry.clean_call.stamp = "-".join([str(new_entry_begin), \
                                                    str(old_elapsed)])
        
    with open(sys.argv[1]) as workflow_file:
        for line in workflow_file:
            entry = load(line)
            for entry in workflow:
                update_stamp(entry, workflow)
                print json.dumps(entry.json())
