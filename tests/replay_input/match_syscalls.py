import sys
import getopt
from fileutil import access_mode
from fileutil import creation_flags
from fileutil import mode_and_flags

#CALLS = ["mkdir", "open", "close", "read", "write"]

""" strace has some garbage, we want only the lines likewise this 
        [pid 17769] 1327429172.301389 mkdir("/tmp/jdt-images", 0777) = 0
        after filter this method produces 
        1327429172.301389 mkdir("/tmp/jdt-images", 0777) = 0
"""
def filter_replayed(replay_output):
    #we keep calls dispatched by child processes
    return [line.split("]")[1].strip() for line in replay_output if line.startswith("[pid")]

def parse_replay_input(line):

    def parse_id(tokens):
        return (int(tokens[0]), tokens[1:])

    def parse_ids(num_ids, tokens):
        if num_ids:
            return ([int(x) for x in tokens[0:num_ids]], tokens[num_ids:])
        else:
            return ([], tokens[1:])

    def parse_header(line):
    #our format is a piece of shit. Consuming tokens makes it easy to be parsed
        tokens = line.split()
        (el_id, tokens) = parse_id(tokens)

        num_parents = int(tokens[0])
        tokens = tokens[1:]

        (parents_ids, tokens) =  parse_ids(num_parents, tokens)

        num_childs = int(tokens[0])
        tokens = tokens[1:]
        (children_ids, tokens) = parse_ids(num_childs, tokens)

        call = " ".join(tokens)
        return ((el_id, parents_ids, children_ids), call)

    def parse_call(line):
        tokens = line.split()
        op = tokens[4]
        args = tokens[6:-1]
        return_value = tokens[-1]
        if op == "mkdir":
            args[-1] = str(oct(int(args[-1])))
        elif op == "open":#FIXME TEST ME
	#we are assuming strace always prints access_mode before c_flags args is a 3 token str list e.g [/var/spool/cron/crontabs', '34816', '0'] we want the second token
           flags_number = int(args[1])
           args[1] = mode_and_flags(flags_number)
        return (op, args, return_value)

    (line_header, call) = parse_header(line)
    return (line_header, parse_call(call))

def parse_replay_output(line):
# [pid 17769] 1327429172.301389 mkdir("/tmp/jdt-images", 0777) = 0

# timestamp = (long(1327429172), long(301389))
# name = "mkdir"
# args ["/tmp/jdt-images", "0777"]
# retvalue = "0"
    def timestamp(call):
        stamp_str = call.split("(")[0].split()[-2].strip()
        seconds_and_nanos = stamp_str.split(".")
        return map(long, seconds_and_nanos)

    def retvalue(call):
    #it is possible to have more than one "=" in a strace output e.g stat, so taking the last token
        try:
            result_and_errors = call.split("=")[-1].strip()
            retvalue = result_and_errors.split(" ")[0].strip()
            return retvalue
        except IndexError:#strace can output bad-formatted strings (I saw no reason splitted lines)
            return ""

    def args(call):#buggy if arg string has ( or )
        try:
            par1_removed = call.split("(")[1]
            args = par1_removed.split(")")[0]
            args = args.split(",")
            args = [x.strip("\" ") for x in args]
            if name(call) == "stat":#super ugly
                del args [1:]
            return args
        except IndexError:
            return ""

    def name(call):
        before_sep = call.split("(")[0]
        return before_sep.split()[-1].strip()

    return (timestamp(line), name(line), args(line), retvalue(line))

class Matcher:
	
    def __init__(self, replay_output_lines):
	self.replayed_calls = [parse_replay_output(outputline) 
                                  for outputline in replay_output_lines]

    def match(self, replay_input_line, exclude_partial_matches=True):
        partial_matches = []
	full_matches = []
       	(line_header, expected_syscall) = parse_replay_input(replay_input_line)
        for actual_syscall in self.replayed_calls:
            (ok_call, ok_args, ok_rvalue) = self.__match__(expected_syscall, 
                                                           actual_syscall)
            if all((ok_call, ok_args, ok_rvalue)):
                full_matches.append([expected_syscall,
                                     actual_syscall,
                                     ok_call, ok_args, ok_rvalue])
            elif ok_call:
                partial_matches.append([expected_syscall,
                                        actual_syscall,
                                        ok_call, ok_args, ok_rvalue])
        
        if exclude_partial_matches:
            return full_matches
        else:
            return full_matches + partial_matches

    def __match__(self, exp_call, actual_call):
        (exp_op, exp_args, exp_r_value) = exp_call
        (timestamp, actual_op, actual_args, actual_r_value) = actual_call
        return (self.__match_call_name__(exp_op, actual_op), 
                self.__match_args__(exp_args, actual_args), 
                self.__match_retvalue__(exp_r_value, actual_r_value)
               )
    
    def __match_call_name__(self, exp_call_name, actual_call_name):
        return exp_call_name == actual_call_name

    def __match_args__(self, exp_args, actual_args):
        return exp_args == actual_args
    
    def __match_retvalue__(self, exp_rval, actual_rval):
        return exp_rval == actual_rval


class WorkflowElement:

    def __init__(self, my_id, parents_ids, children_ids, call, line):#ugly but helps me
        self.my_id = my_id
        self.parents_ids = parents_ids
        self.children_ids = children_ids
        self.call = call
        self.line = line

class Workflow:
    def __init__(self, replay_input_lines):
        self.elements = dict((el.my_id, el) for el in map(self.__build_element__, replay_input_lines))

    def __build_element__(self, line):
        ((line_id, parents_ids, children_ids), call) = parse_replay_input(line)
        return WorkflowElement(line_id, parents_ids, children_ids, call, line)

    def succ(self, el_id):
        if (self.elements[el_id].children_ids):
            _succ = [self.succ(child_id) for child_id in self.elements[el_id].children_ids]
            return _succ.extend(self.elements[el_id].children_ids)
        else:
            return []

    def pred(self, el_id):
        if (self.elements[el_id].parents_ids):
            _pred = [self.pred(parent_id) for parent_id in self.elements[el_id].parents_ids]
            return _pred.extend(self.elements[el_id].parents_ids)
        else:
            return []


""" """
def match_order(replay_input_path, replay_output_path):

    def in2out(replay_input, replay_output):#we can remove from this class to the upper level
        matcher = Matcher(replay_output)
        input_id2output = {}
        for replay_line in replay_input:
            result = matcher.match(replay_line, False)
            if (not len(result) == 1):
               raise Exception("Missing an one-to-one match for: " + replay_line)
            (expected_call, actual_call, ok_call, ok_args, ok_rvalue) = result[0]
            (line_header, line_call) = parse_replay_input(replay_line)
            line_id = line_header[0]
            input_id2output[line_id] = actual_call
        return input_id2output

    class OrderMatcher:

        def __init__(self, workflow, input_id2output):
            self.__workflow = workflow
            self.__input_id2output = input_id2output

        def __output__(self, input_line_ids):#parameter is a iterable but we are handling as an single object FIXME
            return [self.__input_id2output[line_id] for line_id in input_line_ids]

        """ Assert that target_line was replayed before all test_lines """
        def __before__(self, target_line, test_lines):
            target_stamp = self.__timestamp__(target_line)
            test_stamps = [self.__timestamp__(line) for line in test_lines]
            return all([(target_stamp < stamp) for stamp in test_stamps])

        def __timestamp__(self, output):
            return output[0][0]#ugly

        def __after__(self, target_output, test_outputs):#duplicated code with before
            target_stamp = self.__timestamp__(target_output)
            test_stamps = [self.__timestamp__(line) for line in test_outputs]
            return all([(target_stamp > stamp) for stamp in test_stamps])#does it work ?

        def match(self):
            result = []
            for (el_id, el) in self.__workflow.elements.iteritems():#FIXME: it would be nice to have Workflow implementing iter protocol
                pred_ids = self.__workflow.pred(el_id)
                succ_ids = self.__workflow.succ(el_id)
                result.append([el.line,
                              self.__after__(self.__output__([el_id]), 
                                             self.__output__(pred_ids))
                              and
                              self.__before__(self.__output__([el_id]),
                                              self.__output__(succ_ids)),
                              ""])
            return result
                            
            
    replay_input = [line.strip() for line in open(replay_input_path).readlines()[1:]]
    replay_output = filter_replayed([line.strip() 
                                      for line in open(replay_output_path).readlines()])

    input_id2output = in2out(replay_input, replay_output)
    matcher = OrderMatcher(Workflow(replay_input), input_id2output)
    return matcher.match()

""" """
if __name__ == "__main__":
    #FIXME: how to test timing and ordering ??
    #python match_syscalls.py replay_strace_output replay_input -v
    opts, args = getopt.getopt(sys.argv[1:], "-v")
    
    replay_strace_output = open(args[0], 'r').readlines()
    replay_input = open(args[1], 'r').readlines()[1:]#first line is head
    verbose = ("-v", "") in opts

    matcher = Matcher(replay_strace_output)

    for replay_line in replay_input:
	line_2_match = " ".join(replay_line.split()[5:])
        result = matcher.match(line_2_match, not verbose)
	for (expected_call, actual_call, ok_call, ok_args, ok_rvalue) in result:
	    print '[RUN]\texpected={expected}\tactual={actual}'.format(expected=expected_call, actual=actual_call)
  	    print '\tactual\t{actual}'.format(actual=actual_call.strip())
	    print '\tcall_name\t{ok_name}'.format(ok_name=ok_call)
	    print '\targs\t{ok_args}'.format(ok_args=ok_args)
	    print '\trvalue\t{ok_rvalue}\n'.format(ok_rvalue=ok_rvalue)

