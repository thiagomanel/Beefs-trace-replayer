import unittest
from match_syscalls import Matcher
from match_syscalls import match_order
from match_syscalls import *

class TestMatchSyscalls(unittest.TestCase):

    # we to match, if it is ok then we do order match, if it ok then we do timing match

    def test_mknod_match(self):
        matcher = Matcher([parse_replay_output(line) for line in open("test_match/strace_mkdir").readlines()])
        results = matcher.match(parse_replay_input("1 0 - 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images 511 0"), False)
	#there is a single match -> [pid  7817] mkdir("/tmp/jdt-images", 0777) = 0
        self.assertEquals(len(results), 1)
        (expected_syscall, called_syscall, ok_call, ok_args, ok_rvalue) = results[0]
        self.assertTrue(ok_call)
        self.assertTrue(ok_args)
        self.assertTrue(ok_rvalue)

    def test_parse_output_callname(self):
        out = parse_replay_output("[pid 28475] 1327429172.301389 mkdir(\"/tmp/jdt-images\", 0777) = 0")
        self.assertEquals(out.name, "mkdir")
        self.assertEquals(out.args[0], "/tmp/jdt-images")
        self.assertEquals(out.args[1], "0777")
        self.assertEquals(out.retvalue, "0")

    def test_parse_mkdir_expected_call(self):
        matcher = Matcher(open("test_match/strace_mkdir").readlines())
        r_input = parse_replay_input("1 0 - 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images 511 0")
        self.assertEquals(r_input.op, "mkdir")
        self.assertEquals(r_input.args, ["/tmp/jdt-images", oct(511)])
        self.assertEquals(r_input.return_value, str(0))

    def test_match_ordering(self):
        matches = match_order("workflow_samples/workflow_single_command_mkdir", 
                              "test_order_match/workflow_single_command_mkdir.strace.output")
        
        self.assertEquals(len(matches), 1)# we have only 1 command in workflow_single_command_mkdir :)
        for (input_line, match_result, message) in matches:
             self.assertEquals("1 0 - 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images 511 0", input_line)
             self.assertTrue(match_result)

    def test_match_timing_single_command(self):
        input_lines = ["1 0 - 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images 511 0"]
        output_lines = ["[pid 28475] 1327429172.301389 mkdir(\"/tmp/jdt-images\", 0777) = 0"]

        r_input = [parse_replay_input(line) for line in input_lines]
        r_output = [parse_replay_output(clean_output)
                         for clean_output in
                         filter_and_clean_attached_calls(output_lines)]

        matches = match_timing(r_input, r_output)
	
        self.assertEquals(len(matches), 1)
        (input_call, replayed_call, match, message) = matches[0]
        self.assertEquals(input_call, r_input[0].original_line)
        self.assertEquals(replayed_call, str(r_output[0]))
        self.assertEquals(match, True)
        self.assertEquals(message, str(0))

    def __input_timestamp__(self, first, second):
        return "-".join([str(first), str(second)])

    def __output_timestamp__(self, first, second):
        return ".".join([str(first), str(second)])

    def test_match_timing_two_sequencial_command_with_zero_delta(self):

        input_delay = 479
        input_lines = ["1 0 - 1 2 1159 2364 32311 (eclipse) mkdir " + self.__input_timestamp__(10, 0) + " /tmp/jdt-images-1 511 0",
                   "2 1 1 0 - 1159 2364 32311 (eclipse) mkdir " + self.__input_timestamp__(10, input_delay) + " /tmp/jdt-images-2 511 0"]

	
        output_lines = ["[pid 28475] " + self.__output_timestamp__(0, 0) + " mkdir(\"/tmp/jdt-images-1\", 0777) = 0",
                       "[pid 28475] " + self.__output_timestamp__(0, input_delay) + " mkdir(\"/tmp/jdt-images-2\", 0777) = 0"]

        r_input = [parse_replay_input(line) for line in input_lines]
        r_output = [parse_replay_output(clean_output)
                         for clean_output in
                         filter_and_clean_attached_calls(output_lines)]

        #missing the third parameter means delta == 0
        matches = match_timing(r_input, r_output)
        self.assertEquals(len(matches), 2)

        (input_call, replayed_call, match, message) = matches[0]
        self.assertEquals(input_call, r_input[0].original_line)
        self.assertEquals(replayed_call, str(r_output[0]))
        self.assertEquals(match, True)
        self.assertEquals(message, str(0))

        (input_call, replayed_call, match, message) = matches[1]
        self.assertEquals(input_call, r_input[1].original_line)
        self.assertEquals(replayed_call, str(r_output[1]))
        self.assertEquals(match, True)
        self.assertEquals(message, str(0))

    def test_mismatch_timing_two_sequencial_command_with_zero_delta(self):

        input_delay = 479
        mismatch = -1
        in_lines = ["1 0 - 1 2 1159 2364 32311 (eclipse) mkdir " + self.__input_timestamp__(10, 0) + " /tmp/jdt-images-1 511 0",
                   "2 1 1 0 - 1159 2364 32311 (eclipse) mkdir " + self.__input_timestamp__(10, input_delay) + " /tmp/jdt-images-2 511 0"]

        out_lines = ["[pid 28475] " + self.__output_timestamp__(0, 0) + " mkdir(\"/tmp/jdt-images-1\", 0777) = 0",
                    "[pid 28475] " + self.__output_timestamp__(0, input_delay + mismatch) + " mkdir(\"/tmp/jdt-images-2\", 0777) = 0"]

        r_input = [parse_replay_input(line) for line in in_lines]
        r_output = [parse_replay_output(clean_output)
                         for clean_output in
                         filter_and_clean_attached_calls(out_lines)]

        #missing the third parameter means delta == 0
        matches = match_timing(r_input, r_output)
        self.assertEquals(len(matches), 2)

        (input_call, replayed_call, match, message) = matches[0]
        self.assertEquals(input_call, r_input[0].original_line)
        self.assertEquals(replayed_call, str(r_output[0]))
        self.assertEquals(match, True)
        self.assertEquals(message, str(0))

        (input_call, replayed_call, match, message) = matches[1]
        self.assertEquals(input_call, r_input[1].original_line)
        self.assertEquals(replayed_call, str(r_output[1]))
        self.assertEquals(match, False)
        self.assertEquals(message, str(mismatch))

if __name__ == '__main__':
    unittest.main()
