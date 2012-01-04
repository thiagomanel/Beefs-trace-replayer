import unittest
from match_syscalls import Matcher

class TestMatchSyscalls(unittest.TestCase):

    def test_mknod_match(self):
        matcher = Matcher(open("test_match/strace_mknod").readlines())
        results = matcher.match("1159 2364 32311 (eclipse) mkdir 1318539134542649-479 /tmp/jdt-images 511 0")
        self.assertTrue(len(results) > 0)

    def test_parse_output_callname(self):
        matcher = Matcher(open("test_match/strace_mknod").readlines())
        name = matcher.__call_name__("[pid 28475] mkdir(\"/tmp/jdt-images\", 0777) = 0")
        self.assertEquals(name, "mkdir")


if __name__ == '__main__':
    unittest.main()
