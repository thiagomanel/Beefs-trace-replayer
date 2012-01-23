import sys
import getopt
from fileutil import access_mode
from fileutil import creation_flags
from fileutil import mode_and_flags

class Matcher:
	
    def __init__(self, replay_output_lines):
	self.replay_output_lines = replay_output_lines
        self.calls = ["mkdir", "open", "close", "read", "write"]#move to a class constant

    def match(self, replay_input_line, exclude_partial_matches=True):
       	expected_syscall = self.__parse__(replay_input_line)
        partial_matches = []
	full_matches = []
        #Since we now the syscalls were dispacthed by pthread we can make
        #strace parse easier by using only calls that start by "[pid " token 
        #e.g [pid 32237] mkdir("/tmp/jdt-images", 0777) = 0
        for called_syscall in self.replay_output_lines:
            (ok_call, ok_args, ok_rvalue) = self.__match__(expected_syscall, 
                                                           called_syscall)
            if (ok_call and ok_args and ok_rvalue):
                full_matches.append([expected_syscall,
                                     called_syscall,
                                     ok_call, ok_args, ok_rvalue]
                                    )
            elif ok_call:
                partial_matches.append([expected_syscall,
                                        called_syscall,
                                        ok_call, ok_args, ok_rvalue]
                                      )
        
        if exclude_partial_matches:
            return full_matches
        else:
            return full_matches + partial_matches

    def __match__(self, exp_call, actual_call):
        return (self.__match_call_name__(exp_call[0], self.__call_name__(actual_call)), 
                self.__match_args__(exp_call[1], self.__call_args__(actual_call)), 
                self.__match_retvalue__(exp_call[2], self.__retvalue__(actual_call))
               )

    def __parse__(self, replay_input_line):#naive case, a single input call in a input file
	print replay_input_line
        tokens = replay_input_line.split()
        op = tokens[4]
        args = tokens[6:-1]
        return_value = tokens[-1]
        if op == "mkdir":
	    args[-1] = str(oct(int(args[-1])))
        elif op == "open":#FIXME TEST ME
	    #we are assuming strace always prints access_mode before c_flags
            #args is a 3 token str list e.g [/var/spool/cron/crontabs', '34816', '0']
            #    we want the second token
            flags_number = int(args[1])
            args[1] = mode_and_flags(flags_number)
    
        return (op, args, return_value)

    def __match_call_name__(self, exp_call_name, actual_call_name):
        return exp_call_name == actual_call_name

    def __call_name__(self, call):
	# due to attached process, strace output changes, i.e
	# [pid  7817] mkdir("/tmp/jdt-images", 0777) = 0
	# mkdir("/tmp/jdt-images", 0777) = 0
        before_sep = call.split("(")[0]
	return before_sep.split()[-1].strip()

    def __match_args__(self, exp_args, actual_args):
        return exp_args == actual_args

    def __call_args__(self, call):#buggy if arg string has ( or )
        try:
	    par1_removed = call.split("(")[1]
	    args = par1_removed.split(")")[0]
	    args = args.split(",")
	    args = [x.strip("\" ") for x in args]
	    if self.__call_name__(call) == "stat":
	        del args [1:]
	    return args
        except IndexError:
	    return ""

    def __match_retvalue__(self, exp_rval, actual_rval):
        return exp_rval == actual_rval

    def __retvalue__(self, call):
        try:
	    #it is possible to have more than one "=" in a strace output e.g stat, so taking the last token
	    result_and_errors = call.split("=")[-1].strip()
	    retvalue = result_and_errors.split(" ")[0].strip()
	    return retvalue
        except IndexError:#strace can output bad-formatted strings (I saw no reason splitted lines)
	    return ""

class WorkflowElement:

    def __init__(self, my_id, parents_ids, children_ids, call):
        self.my_id = my_id
        self.parents_ids = parents_ids
        self.children_ids = children_ids
        self.call = calls

class Workflow:

    def __init__(replay_input_lines):
        self.elements = {}
        for line in replay_input_lines:
            el = self.__build_element__(line)
            self.elements[el.my_id] = el

    def __parse_id__(self, tokens):
        return (int(tokens[0]), tokens[1:])

    def __parse_ids__(self, num_ids, line_tokens):
        if num_ids:
            return ([int(x) for x in line_tokens[0:num_ids]], token[num_ids])
        else:
            return ([], tokens[1:])

    def __build_element__(self, line):
        #our format is a piece of shit. Consuming tokens makes it easy to be parsed, that is the reason i'm returning a 
	#new tokens collection
        tokens = line.split()
        (el_id, tokens) = self.__parse_id__(tokens)

        num_parents = int(tokens[0])
        tokens = tokens[1:]

        (parents_ids, tokens) =  self.__parse_ids__(num_parents, tokens)

        num_childs = int(tokens[0])
        tokens = tokens[1:]
        (children_ids, tokens) =  self.__parse_ids__(num_childs, tokens)

        call = " ".join(tokens)
        return WorkflowElement(el_id, parents_ids, children_ids, call)

    def succ(self, el_id):
        if (self.elements[el_id].children_ids):
            _succ = [self.succ(child_id) for child_id in self.elements[el_id].children_ids]
            return _succ.extend(self.elements[el_id].children_ids)
        else:
            return None

    def pred(self, el_id):
        if (self.elements[el_id].parents_ids):
            _pred = [self.pred(parent_id) for parent_id in self.elements[el_id].parents_ids]
            return _pred.extend(self.elements[el_id].parents_ids)
        else:
            return None

"""
    def __iter__(self):
        return None
    def next(self):
        return None"""
    

class OrderMatcher:

    def __init__(self, replay_output_path):
        self.matcher = Matcher(open(replay_output_path).readlines())

    def __map2output__(self, replay_input):
        input2output = {}
        for replay_line in replay_input:
            line_2_match = " ".join(replay_line.split()[5:])
            result = self.matcher.match(line_2_match, False)
            if (not len(result) == 1):
                raise Exception("Missing an one-to-one match for: " + replay_line)
            (expected_call, actual_call, ok_call, ok_args, ok_rvalue) = result[0]
            input2output[replay_line] = actual_call
        return input2output

    def __pred__(self, line, input_lines):
        return None

    def __succ__(self, input_line, output_lines):
        return None

    def __match_line__(input_line, output_lines):
        return None

    def match(self, replay_input_path):
        result = []
        replay_input = open(replay_input_path).readlines()[1:]
        in2out = self.__map2output__(replay_input)
        for r_input_line in self.__map2output__(replay_input).keys():#replace this for by a comprehension
            result.append(self.__match_line__(r_input_line, ))
        return result

#
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

