import sys
import json

if __name__ == "__main__":
   def parse(old_line):
       #e.g
       #1 0 - 1 2 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-1 511 0
       #2 1 1 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images-2 511 0
       tokens = old_line.split()
	#It's the worst format ever made
       _id = int(tokens[0])
       n_parents = int(tokens[1])
       if n_parents:
           parents = [int(parent) for parent in tokens[2:2 + n_parents]]
       else:
           parents = []

       if n_parents > 1:
           n_children_pos = 2 + n_parents
       else:
           n_children_pos = 3
 
       n_children = int(tokens[n_children_pos])
       if n_children:
           children = [int(child) for child in tokens[n_children_pos + 1: n_children_pos + 1 + n_children]]
       else:
           children = []

       if n_children > 1:
           uid_pos = n_children_pos + 1 + n_children
       else:
           uid_pos = n_children_pos + 2

       uid = int(tokens[uid_pos])
       pid = int(tokens[uid_pos + 1])
       tid = int(tokens[uid_pos + 2])
       _exec = tokens[uid_pos + 3]

       call = tokens[uid_pos + 4]

       stamp = tokens[uid_pos + 5].split("-")
       stamp_begin = float(stamp[0])
       stamp_end = long(stamp[1])

       args = tokens[uid_pos + 6:-1]
       rvalue = int(tokens[-1])

       return (_id,
               parents,
               children,
               call, 
               (_exec, pid, tid, uid),
               (args),
               (stamp_begin, stamp_end),
               rvalue
              )
       
   sys.stdin.readline()#excluding header
   dump = []
   for old_replay_line in sys.stdin:
       _id, parents, children, \
       _call, (_exec, pid, tid, uid), _args, \
       (begin, end), _rvalue = parse(old_replay_line)

       dump.append(
                   {   "id":_id,
                       "parents":parents,
                       "children":children,
                       "stamp": {
                                 "begin": begin,
                                 "elapsed": end
                                },
                       "call":_call,
                       "caller": {
                                  "exec": _exec,
                                  "uid": uid,
                                  "pid": pid,
                                  "tid": tid
                                 },
                       "args": _args,
                        "rvalue": _rvalue
                   })
   json_str = json.dumps(dump, sort_keys=True, indent=4)
   sys.stdout.write(json_str)
