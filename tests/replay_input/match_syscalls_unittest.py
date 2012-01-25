import unittest
from match_syscalls import Matcher
from match_syscalls import match_order
from match_syscalls import *

class TestMatchSyscalls(unittest.TestCase):

    def test_mknod_match(self):
        matcher = Matcher(open("test_match/strace_mkdir").readlines())
        results = matcher.match("1 0 - 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images 511 0", False)
	#there is a single match -> [pid  7817] mkdir("/tmp/jdt-images", 0777) = 0
        self.assertEquals(len(results), 1)
        (expected_syscall, called_syscall, ok_call, ok_args, ok_rvalue) = results[0]
        self.assertTrue(ok_call)
        self.assertTrue(ok_args)
        self.assertTrue(ok_rvalue)

    def test_parse_output_callname(self):
        (op_name, args, r_value) = parse_replay_output("[pid 28475] mkdir(\"/tmp/jdt-images\", 0777) = 0")
        self.assertEquals(op_name, "mkdir")
        self.assertEquals(args[0], "/tmp/jdt-images")
        self.assertEquals(args[1], "0777")
        self.assertEquals(r_value, "0")

    def test_parse_mkdir_expected_call(self):
        matcher = Matcher(open("test_match/strace_mkdir").readlines())
        (line_header, (op, args, return_value)) = parse_replay_input("1 0 - 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images 511 0")
        self.assertEquals(op, "mkdir")
        self.assertEquals(args, ["/tmp/jdt-images", oct(511)])
        self.assertEquals(return_value, str(0))

    def test_match_ordering(self):
        matches = match_order("workflow_samples/workflow_single_command_mkdir", 
                              "test_order_match/workflow_single_command_mkdir.strace.output")
        
        self.assertEquals(len(matches), 1)# we have only 1 command in workflow_single_command_mkdir :)
        for (input_line, match_result, message) in matches:
             self.assertEquals("1 0 - 0 - 1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images 511 0", input_line)
             self.assertTrue(match_result)


if __name__ == '__main__':
    unittest.main()
