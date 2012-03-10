import sys
import getopt
from fileutil import access_mode
from fileutil import creation_flags
from fileutil import mode_and_flags

#CALLS = ["mkdir", "open", "close", "read", "write"]

"""
strace has some garbage, we want only the lines likewise this 
[pid 17769] 1327429172.301389 mkdir("/tmp/jdt-images", 0777) = 0
after filter this method produces 
1327429172.301389 mkdir("/tmp/jdt-images", 0777) = 0
"""
def filter_and_clean_attached_calls(replayed_lines):

    def clean_attached_call(output_line):
        return output_line.split("]")[1].strip()

    return map(clean_attached_call, 
               filter(lambda x: x.startswith("[pid"), replayed_lines))

class Replay_Input:#ugly but helps me

    def __init__(self, el_id, parents_ids, children_ids, timestamp, op, 
                 args, return_value, original_line):
        self.el_id = el_id
        self.parents_ids = parents_ids
        self.children_ids = children_ids
        self.begin_us = timestamp[0]
        self.end_us = timestamp[0] + timestamp[1]
        self.op = op
        self.args = args
        self.return_value = return_value
        self.original_line = original_line

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
        timestamp = map(long, tokens[5].split("-"))
        args = tokens[6:-1]
        return_value = tokens[-1]
        if op == "mkdir":
            args[-1] = str(oct(int(args[-1])))
        elif op == "open":#FIXME TEST ME
	#we are assuming strace always prints access_mode before c_flags args is a 3 token str list e.g [/var/spool/cron/crontabs', '34816', '0'] we want the second token
           flags_number = int(args[1])
           args[1] = mode_and_flags(flags_number)
        return (timestamp, op, args, return_value)

    ((el_id, parents_ids, children_ids), call) = parse_header(line)
    (timestamp, op, args, return_value) = parse_call(call)
    return Replay_Input(el_id, parents_ids, children_ids, timestamp, op, args, return_value, line)


class ReplayOutput:

    def __init__(self, timestamp, name, args, retvalue):
        self.timestamp = timestamp
        self.name = name
        self.args = args
        self.retvalue = retvalue

    def __str__(self):
        return " ".join([str(self.timestamp), self.name, str(self.args), str(self.retvalue)])

"""
[pid 17769] 1327429172.301389 mkdir("/tmp/jdt-images", 0777) = 0

timestamp = (long(1327429172), long(301389))
name = "mkdir"
args ["/tmp/jdt-images", "0777"]
retvalue = "0"
"""
def parse_replay_output(line):

    def timestamp(call):
        stamp_str = call.split("(")[0].split()[-2].strip()
        seconds_and_micros = stamp_str.split(".")
        return map(long, seconds_and_micros)

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

    return ReplayOutput(timestamp(line), name(line), args(line), retvalue(line))

class Matcher:
	
    def __init__(self, replay_output):
	self.replayed_calls = replay_output

    def match(self, replay_input, exclude_partial_matches=True):
        partial_matches = []
	full_matches = []
        expected_syscall = (replay_input.op, replay_input.args, replay_input.return_value)
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
        return (self.__match_call_name__(exp_op, actual_call.name), 
                self.__match_args__(exp_args, actual_call.args), 
                self.__match_retvalue__(exp_r_value, actual_call.retvalue)
               )
    
    def __match_call_name__(self, exp_call_name, actual_call_name):
        return exp_call_name == actual_call_name

    def __match_args__(self, exp_args, actual_args):
        return exp_args == actual_args
    
    def __match_retvalue__(self, exp_rval, actual_rval):
        return exp_rval == actual_rval


class Workflow:
    
    FAKE_ROOT_ID = 0

    def __init__(self, replay_input):
        self.__root = Replay_Input(self.FAKE_ROOT_ID, [], [], (0, 0), "fake_op", 
                                 None, None, "fake_line")

        if not all([element.el_id for element in replay_input]):
            raise Exception("An input line with id equals to zero was found")

        map(self.__bind_root_as_parent__, filter(self.__orphan__, replay_input))
        
        self.__elements = dict((el.el_id, el) for el in replay_input)

        self.__root.begin_us = self.__eldest__().begin_us
        self.__root.end_us = self.__eldest__().end_us

        self.__elements[self.FAKE_ROOT_ID] = self.__root

    def __bind_root_as_parent__(self, element):
        element.parents_ids.append(self.__root.el_id)
        self.__root.children_ids.append(element.el_id)

    def __eldest__(self):
        return min(self.__elements.values(), key=lambda x:x.end_us)

    def __orphan__(self, element):
        return not element.parents_ids

    def element(self, element_id):
        return self.__elements[element_id]

    def elements(self):
        return self.__elements.values()

    def __iter__(self):
        return self.__elements.values().__iter__()

    def succ(self, el_id):
        if (self.element(el_id).children_ids):
            _succ = [self.succ(child_id) 
                     for child_id in self.element(el_id).children_ids]
            return _succ.extend(self.element(el_id).children_ids)
        else:
            return []

    def pred(self, el_id):
        if (self.element(el_id).parents_ids):
            _pred = []
            for parent_id in self.element(el_id).parents_ids:
                _pred.extend(self.pred(parent_id)) 
            _pred.extend(self.element(el_id).parents_ids)
            return _pred
        else:
            return []

    def root(self):
        return self.element(self.FAKE_ROOT_ID)


def in2out(replay_input, replay_output):
    matcher = Matcher(replay_output)
    input_id2output = {}
    for r_input in replay_input:
        result = matcher.match(r_input, True)
        if (not len(result) == 1):
           raise Exception("Missing an one-to-one match for: " + r_input.original_line)
        (expected_call, actual_call, ok_call, ok_args, ok_rvalue) = result[0]
        line_id = r_input.el_id
        input_id2output[line_id] = actual_call
    return input_id2output


def match_order(replay_input_path, replay_output_path):
#should be receive a string list instead of paths ?
    """
    A call respect order when it was dispatched before its successors
    and after its antecessors
    """

    class OrderMatcher:

        def __init__(self, workflow, input_id2output):
            self.__workflow = workflow
            self.__input_id2output = input_id2output

        def __output__(self, input_line_ids):
            return [self.__input_id2output[line_id] for line_id in input_line_ids]

        """ Assert that target_line was replayed before all test_lines """
        def __before__(self, target_line, test_lines):
            target_stamp = target_line.timestamp
            test_stamps = [line.timestamp for line in test_lines]
            return all([(target_stamp < stamp) for stamp in test_stamps])

        def __after__(self, target_output, test_outputs):#duplicated code with before FIXME
            target_stamp = target_output.timestamp
            test_stamps = [line.timestamp for line in test_outputs]
            return all([(target_stamp > stamp) for stamp in test_stamps])#does it work ? FIXME

        def match(self):
            result = []
            for _id in [element.el_id for element in self.__workflow 
                                          if not element is self.__workflow.root()]:

                pred_ids = self.__workflow.pred(_id)
                if Workflow.FAKE_ROOT_ID in pred_ids: pred_ids.remove(Workflow.FAKE_ROOT_ID)
                succ_ids = self.__workflow.succ(_id)
                if Workflow.FAKE_ROOT_ID in succ_ids: succ_ids.remove(Workflow.FAKE_ROOT_ID)

                result.append([self.__workflow.element(_id).original_line,
                              self.__after__(self.__output__([_id])[0], 
                                             self.__output__(pred_ids))
                              and
                              self.__before__(self.__output__([_id])[0],
                                              self.__output__(succ_ids)),
                              ""])
            return result
                            
            
    replay_input = [parse_replay_input(line.strip()) 
                    for line in open(replay_input_path).readlines()[1:]]

    replay_output = [parse_replay_output(clean_output) 
                     for clean_output in 
                     filter_and_clean_attached_calls(
                         [line.strip() for line in open(replay_output_path).readlines()])]

    input_id2output = in2out(replay_input, replay_output)
    workflow = Workflow(replay_input)
    matcher = OrderMatcher(workflow, input_id2output)
    root_input = workflow.root()
    input_id2output[root_input.el_id] = fake_replay_output(root_input)
    return matcher.match()

def fake_replay_output(replay_input):
    #convert from in.timestamp to out.timestamp FIXME
    return ReplayOutput((replay_input.end_us , replay_input.end_us),
                        "FAKE",
                        replay_input.args,
                        replay_input.return_value)

def match_timing(replay_input, replay_output):
    """
    A replayed call respect timing when ...
    """
    def input_delay(one, two):
        return one.end_us - two.end_us

    def output_delay(one, two):
        """
        seconds since epoch.microseconds
        1328016624.544599 fstat64(3, {st_mode=S_IFREG|0644, st_size=256324, ...}) = 0
        1328016624.544687 mmap2(NULL, 256324, PROT_READ, MAP_PRIVATE, 3, 0) = 0xb766b000
        """
        def us_since_epoch(output_stamp):
            return (output_stamp[0] * 1000000 + output_stamp[1])

        return us_since_epoch(one.timestamp) - us_since_epoch(two.timestamp)

    def output(r_input):
        return input_id2output[r_input.el_id]

    """ 
    match input_ont against input_two
    returning a (input_line, replayed_line, match, message) tuple
    """
    def match(input_one, input_two):
        (match, mismatch_amount) = assert_timing(input_one, input_two)
        return (input_two.original_line,
                str(output(input_two)),
                match,
                str(mismatch_amount))

    def assert_timing(input_one, input_two):
        if input_one.el_id is Workflow.FAKE_ROOT_ID:
            return (True, 0)
        else:
            mismatch = input_delay(input_one, input_two) - output_delay(
                                                             output(input_one),  
                                                             output(input_two))
            return (abs(mismatch) <= delta, mismatch)

    def visit(replay_input):
        children = [workflow.element(child_id) 
                    for child_id in replay_input.children_ids]
        my_check = [match(replay_input, child) for child in children]
        for child in children:
            child_check = visit(child)
            if child_check:
                my_check.extend(child_check)
        return my_check

    delta = 0

    workflow = Workflow(replay_input)
    input_id2output = in2out(replay_input, replay_output)
    root_input = workflow.root()
    input_id2output[root_input.el_id] = fake_replay_output(root_input)
    return visit(root_input)

""" """
if __name__ == "__main__":
    #FIXME: how to test timing and ordering ??
    #python match_syscalls.py replay_strace_output replay_input -v
    opts, args = getopt.getopt(sys.argv[1:], "-v")
    
    replay_strace_output = [parse_replay_output(line) 
                            for line in open(args[0], 'r').readlines()]
    replay_input = open(args[1], 'r').readlines()[1:]#first line is head
    verbose = ("-v", "") in opts

    matcher = Matcher(replay_strace_output)

    for replay_line in replay_input:
	line_2_match = " ".join(replay_line.split())
        result = matcher.match(parse_replay_input(line_2_match), not verbose)
	for (expected_call, actual_call, ok_call, ok_args, ok_rvalue) in result:
	    print '[RUN]\texpected={expected}\tactual={actual}'.format(expected=expected_call, actual=actual_call)
  	    print '\tactual\t{actual}'.format(actual=actual_call)
	    print '\tcall_name\t{ok_name}'.format(ok_name=ok_call)
	    print '\targs\t{ok_args}'.format(ok_args=ok_args)
	    print '\trvalue\t{ok_rvalue}\n'.format(ok_rvalue=ok_rvalue)

