import sys
import getopt

def match(exp_call, actual_call):
    return (match_call_name(exp_call[0], call_name(actual_call)), 
               match_args(exp_call[1], call_args(actual_call)), 
               match_retvalue(exp_call[2], retvalue(actual_call))
           )
#by now, only "==", more comming
def match_call_name(exp_call_name, actual_call_name):
    return exp_call_name == actual_call_name
def call_name(call):
    return call.split("(")[0].strip()

def match_args(exp_args, actual_args):
    return exp_args == actual_args
def call_args(call):#buggy if arg string has ( or )
    try:
	par1_removed = call.split("(")[1]
	args = par1_removed.split(")")[0]
	args = args.split(",")
	args = [x.strip("\" ") for x in args]
	if call_name(call) == "stat":
	    del args [1:]
	return args
    except IndexError:
	return ""

def match_retvalue(exp_rval, actual_rval):
    return exp_rval == actual_rval
def retvalue(call):
    try:
	#it is possible to have more than one "=" in a strace output e.g stat, so taking the last token
	result_and_errors = call.split("=")[-1].strip()
	retvalue = result_and_errors.split(" ")[0].strip()
	return retvalue
    except IndexError:#strace can output bad-formatted strings (I saw no reason splitted lines)
	return ""

def parse_workload_line(workload_line):
    tokens = workload_line.split()
    op = tokens[4]
    args = tokens[6:-1]
    if op == "mkdir":
	args[-1] = str(oct(int(args[-1])))
    
    return (tokens[4], args, tokens[-1])

if __name__ == "__main__":
#FIXME: how to test timing and ordering ??
    #python match_syscalls.py replay_strace_output replay_input -v
    opts, args = getopt.getopt(sys.argv[1:], "-v")
    
    replay_strace_output = open(args[0], 'r').readlines()
    replay_input = open(args[1], 'r')
    verbose = ("-v", "") in opts

    for replay_line in replay_input:
        expected_syscall = parse_workload_line(replay_line) #naive case, a single input call in a input file
	complete_match = False
    	candidate_matches = []
	for called_syscall in replay_strace_output:
       	    (ok_call, ok_args, ok_rvalue) = match(expected_syscall, called_syscall)
	    if ok_call:#to be a candidate a call name match is enough
	        candidate_matches.append([expected_syscall, called_syscall, ok_call, ok_args, ok_rvalue])
	    complete_match = complete_match or ( sum([ok_call, ok_args, ok_rvalue]) == len([ok_call, ok_args, ok_rvalue]) )

	print '[RUN]\texpected={expected}\tMATCH={match}'.format(expected=expected_syscall, match=complete_match)
        if verbose:
	    print 'candidates'
     	    for candidate in candidate_matches:
    	        print '\tactual\t{actual}'.format(actual=candidate[1].strip())
	        print '\tcall_name\t{ok_name}'.format(ok_name=candidate[2])
	        print '\targs\t{ok_args}'.format(ok_args=candidate[3])
	        print '\trvalue\t{ok_rvalue}\n'.format(ok_rvalue=candidate[4])

