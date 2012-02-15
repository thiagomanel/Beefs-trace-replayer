import unittest
from fs_objects import *


class TestCleanTrace(unittest.TestCase):

    def test_accessed_and_created_rmdir(self):
        self.assertEquals(accessed_and_created([]), None)


if __name__ == '__main__':
    unittest.main()
