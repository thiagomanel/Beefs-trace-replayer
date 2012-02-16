import unittest
from fs_objects import *


class TestCleanTrace(unittest.TestCase):

    def test_accessed_and_created_rmdir(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 916 916 (rm) rmdir 1319227056527181-26 /local/ourgrid/gp_hash_table_map_ 0".split())
        self.assertEquals(
                          [
                           "/local/ourgrid/gp_hash_table_map_", 
                           "/local/ourgrid", 
                           "/local"
                          ],
                          ac_dirs
                         )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)


if __name__ == '__main__':
    unittest.main()
