import sys

def match(exp_call, actual_call):
    return (match_call_name(exp_call[0], call_name(actual_call)), 
               match_args(exp_call[1], call_args(actual_call)), 
               match_retvalue(exp_call[2], retvalue(actual_call))
           )
#by now, only "==", more comming
def match_call_name(exp_call_name, actual_call_name):
    return exp_call_name == actual_call_name
def call_name(call):
    return call.split("(")[0]

def match_args(exp_args, actual_args):
    return exp_args == actual_args
def call_args(call):#buggy if arg string has ( or )
    try:
	par1_removed = call.split("(")[1]
	args = par1_removed.split(")")[0]
	return args.split(",")
    except IndexError:
	return ""

def match_retvalue(exp_rval, actual_rval):
    return exp_rval == actual_rval
def retvalue(call):
    try:
	result_and_errors = call.split("=")[1]
	return result_and_errors.split(" ")[0]
    except IndexError:#strace can output bad-formatted strings (I saw no reason splitted lines)
	return ""

def parse_workload_line(workload_line):
    tokens = workload_line.split()
    return (tokens[4], tokens[5:8], tokens[-1])

if __name__ == "__main__":

#FIXME: how to test timing and ordering ??
    replay_strace_output = open(sys.argv[1], 'r')
    replay_input = open(sys.argv[2], 'r')
    expected_syscall = parse_workload_line(replay_input.readline()) #naive case, a single input call in a input file
    matches = []
    for called_syscall in replay_strace_output:
        (ok_call, ok_args, ok_rvalue) = match(expected_syscall, called_syscall)
	if ok_call:
	    matches.append([expected_syscall, called_syscall, ok_call, ok_args, ok_rvalue])
#it will be good to print: 
#exp_name actual name bool
#exp_args actual args bool
#exp_rvalue actual_rvalue bool

    if matches:
	for match in matches:
	    print match
    else:
	print "No matches for:", expected_syscall 

