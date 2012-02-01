import unittest
from clean_trace import *

class TestCleanTrace(unittest.TestCase):

    def test_clean_unlink(self):
        self.assertEquals(
                          clean_unlink("1159 2364 32311 (eclipse) sys_unlink 1318539134533662-8118 /home/thiagoepdc/ /home/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images/1.png 0".split()), 
                          "1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /home/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images/1.png 0")

    def test_clean_unlink_No_home_is_None(self):
        #assertIsNone is just python 2.7
        self.assertFalse(clean_unlink("1159 2364 32311 (eclipse) sys_unlink 1318539134533662-8118 /local/thiagoepdc/ 1.png 0".split()))
        self.assertFalse(clean_unlink("1159 2364 32311 (eclipse) sys_unlink 1318539134533662-8118 /home/thiagoepdc/ /local/thiagoepdc/workspace_beefs/.metadata/.plugins/org.eclipse.jdt.ui/jdt-images/1.png 0".split()))

if __name__ == '__main__':
    unittest.main()
