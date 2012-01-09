import unittest
from match_syscalls import Matcher

class TestMatchSyscalls(unittest.TestCase):

    def test_mknod_match(self):
        matcher = Matcher(open("test_match/strace_mkdir").readlines())
        results = matcher.match("1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images 511 0", False)
	#there is a single match -> [pid  7817] mkdir("/tmp/jdt-images", 0777) = 0
        self.assertEquals(len(results), 1)
        (expected_syscall, called_syscall, ok_call, ok_args, ok_rvalue) = results[0]
        self.assertTrue(ok_call)
        self.assertTrue(ok_args)
        self.assertTrue(ok_rvalue)

    def test_parse_output_callname(self):
        matcher = Matcher(open("test_match/strace_mkdir").readlines())
        name = matcher.__call_name__("[pid 28475] mkdir(\"/tmp/jdt-images\", 0777) = 0")
        self.assertEquals(name, "mkdir")

    def test_parse_mkdir_expected_call(self):
        matcher = Matcher(open("test_match/strace_mkdir").readlines())
        (op, args, return_value) = matcher.__parse__("1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images 511 0")
        self.assertEquals(op, "mkdir")
        self.assertEquals(args, ["/tmp/jdt-images", oct(511)])
        self.assertEquals(return_value, str(0))  

if __name__ == '__main__':
    unittest.main()