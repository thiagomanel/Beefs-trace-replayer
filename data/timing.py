import json
import sys
from bfs import *
from workflow import *

if __name__ == "__main__":
    """
       It changes the expected begin of trace calls to reflect 
       timing polices.

       Usage: python timing.py workflow_path > new_workflow
    """
    def parse(line):
        entry = json.loads(line)
        return WorkflowLine.from_json(entry)

    def stamp(workflow_entry):
        stamp = workflow_entry.clean_call.stamp.split("-")
        return float(stamp[0]), long(stamp[1])

    def update_stamp(workflow_entry, workflow):

        def entry_by_id(entry_id):
            return workflow[entry_id]

        def check_new_begin(new_begin, entry):
            old_entry_begin, old_entry_elapsed = stamp(entry)
            if old_entry_begin <= new_entry_begin:
                sys.stderr.write("new begin=%d is latter than old=%d id=%s\n" \
                                  % (new_entry_begin, old_entry_begin,
                                     workflow_entry._id))
                exit(1)

        def parent(entry):
            def finish_later(entries_id):
               def finish(entry_id):
                   begin, elapsed = stamp(entry_by_id(entry_id))
                   return begin + elapsed
               return max(entries_id, key=finish)

            if entry.parents:
                later_parent_id = finish_later(entry.parents)
                return entry_by_id(later_parent_id)
            return None

        _parent = parent(workflow_entry)
        if _parent:
            parent_begin, parent_elapsed = stamp(_parent)
            #FIXME this should be modularized to allow different timing polices
            new_entry_begin = parent_begin + parent_elapsed
            check_new_begin(new_entry_begin, workflow_entry)
            old_begin, old_elapsed = stamp(entry)
            workflow_entry.clean_call.stamp = "-".join([str(new_entry_begin), \
                                                        str(old_elapsed)])
        
    with open(sys.argv[1]) as workflow_file:
        workflow = {}
        for line in workflow_file:
            entry = parse(line)
            workflow[entry._id] = entry
            update_stamp(entry, workflow)
            print json.dumps(entry.json())
