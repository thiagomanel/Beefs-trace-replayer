import sys
import json

if __name__ == "__main__":
   def parse(old_line):
       #it's able to parse string used in loader_unittest. It's not safe
       #to use anything more complex
       
       #e.g 0 2097 2097 (udisks-daemon) close 1318539063006403-37 7 0
       tokens = old_line.split()

       uid = int(tokens[0])
       pid = int(tokens[1])
       tid = int(tokens[2])
       _exec = tokens[3]

       call = tokens[4]

       stamp = tokens[5].split("-")
       stamp_begin = float(stamp[0])
       stamp_end = long(stamp[1])

       args = tokens[6:-1]
       rvalue = int(tokens[-1])

       return (call, 
               (_exec, pid, tid, uid),
               (args),
               (stamp_begin, stamp_end),
               rvalue
              )
       
   count = 0
   for old_replay_line in sys.stdin:
       _call, (_exec, pid, tid, uid), _args, (begin, end), _rvalue = parse(old_replay_line)
       with open(_call + str(count), 'w') as out:
           json_str = json.dumps([
                   {   "id":1,
                       "parents":[],
                       "children":[],
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
                   }
                       ], sort_keys=True, indent=4)
           out.write(json_str)
           count = count + 1
 
