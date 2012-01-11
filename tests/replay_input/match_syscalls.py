import sys
import getopt

class Matcher:
	
    def __init__(self, replay_output_lines):
	self.replay_output_lines = replay_output_lines
        self.calls = ["mkdir", "open", "close", "read", "write"]#move to a class constant

    def match(self, replay_input_line, exclude_partial_matches=True):
       	expected_syscall = self.__parse__(replay_input_line)
        partial_matches = []
	full_matches = []
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

