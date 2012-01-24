import sys
import getopt
from fileutil import access_mode
from fileutil import creation_flags
from fileutil import mode_and_flags

CALLS = ["mkdir", "open", "close", "read", "write"]

class Matcher:
	
    def __init__(self, replay_output_lines):
	self.replay_output_lines = replay_output_lines

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
            if all((ok_call, ok_args, ok_rvalue)):
                full_matches.append([expected_syscall,
                                     called_syscall,
                                     ok_call, ok_args, ok_rvalue])
            elif ok_call:
                partial_matches.append([expected_syscall,
                                        called_syscall,
                                        ok_call, ok_args, ok_rvalue])
        
        if exclude_partial_matches:
            return full_matches
        else:
            return full_matches + partial_matches

    def __match__(self, exp_call, actual_call):
        return (self.__match_call_name__(exp_call[0], 
                                         self.__call_name__(actual_call)), 
                self.__match_args__(exp_call[1], 
                                    self.__call_args__(actual_call)), 
                self.__match_retvalue__(exp_call[2], 
                                        self.__retvalue__(actual_call))
               )

    def __parse__(self, replay_input_line):#naive case, a single input call in a input file
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
        self.call = call

class Workflow:

    def __init__(self, replay_input_lines):
        self.elements = {}
        for line in replay_input_lines:
            el = self.__build_element__(line)
            self.elements[el.my_id] = el

    def __parse_id__(self, tokens):
        return (int(tokens[0]), tokens[1:])

    def __parse_ids__(self, num_ids, tokens):
        if num_ids:
            return ([int(x) for x in tokens[0:num_ids]], tokens[num_ids:])
        else:
            return ([], tokens[1:])

    def __build_element__(self, line):
#our format is a piece of shit. Consuming tokens makes it easy to be parsed, that is the reason i'm returning a new tokens collection
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
""" """
def match_order(replay_input_path, replay_output_path):

    class OrderMatcher:

        def __init__(self, replay_input, replay_output):
            self.__replay_input = replay_input
            self.__workflow = Workflow(replay_input)
            self.__input2output = self.__build_in2out_map__(replay_input, 
                                         self.__filter_replayed__(replay_output))

	""" strace has some garbage, we want only the lines likewise this 
            [pid 17769] 1327429172.301389 mkdir("/tmp/jdt-images", 0777) = 0
            after filter this method produces 
            1327429172.301389 mkdir("/tmp/jdt-images", 0777) = 0
        """
        def __filter_replayed__(self, replay_output):
            replayed_calls = []
            for outputline in replay_output:
                if outputline.startswith("[pid"):
                    replayed_calls.append(outputline.split("]")[1].strip())
            return replayed_calls

        def __build_in2out_map__(self, replay_input, replay_output):
            matcher = Matcher(replay_output)
            input2output = {}
            for replay_line in replay_input:
                line_2_match = " ".join(replay_line.split()[5:])
                result = matcher.match(line_2_match, False)
                if (not len(result) == 1):
                    raise Exception("Missing an one-to-one match for: " + replay_line)
                (expected_call, actual_call, ok_call, ok_args, ok_rvalue) = result[0]
                input2output[replay_line] = actual_call
            return input2output

        def __output__(self, input_line):
            if input_line:
                return self.__input2output[input_line]
            else:
                return []

        def __input_line_id__(self, input_line):
            return int(input_line.split()[0])

        def __pred__(self, line):
            return self.__workflow.pred(self.__input_line_id__(line))

        def __succ__(self, line):
            return self.__workflow.succ(self.__input_line_id__(line))

        def __timestamp__(self, outputline):#FIXME there is more than one place parsing strace output, refactor
            #1327429172.301389 mkdir("/tmp/jdt-images", 0777) = 0
            stamp = outputline.split()[0].split(".")
            return (long(stamp[0]), long(stamp[1]))

        """ Assert that target_line was replayed before all test_lines """
        def __replayed_before__(self, target_line, test_lines):
            target_stamp = self.__timestamp__(target_line)
            test_stamps = [self.__timestamp__(line) for line in test_lines]
            return all([(target_stamp < stamp) for stamp in test_stamps])

        def __replayed_after__(self, target_line, test_lines):
            target_stamp = self.__timestamp__(target_line)
            test_stamps = [self.__timestamp__(line) for line in test_lines]
            return all([(target_stamp > stamp) for stamp in test_stamps])

        def match(self):
            result = []
            for input_line in self.__replay_input:
                pred = self.__pred__(input_line)
                succ = self.__succ__(input_line)
                result.append([input_line,
                              self.__replayed_after__(self.__output__(input_line),
                                                      self.__output__(pred))
                              and
                              self.__replayed_before__(self.__output__(input_line),
                                                       self.__output__(succ)),
                              ""])
            return result
                            
            
    replay_input = [line.strip() for line in open(replay_input_path).readlines()[1:]]
    replay_output = [line.strip() for line in open(replay_output_path).readlines()]
    matcher = OrderMatcher(replay_input, replay_output)
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

