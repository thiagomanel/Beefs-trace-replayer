import unittest
from fs_objects import *


class TestCleanTrace(unittest.TestCase):

    def test_accessed_and_created_rmdir(self):
        #FIXME what if the directory terminates with "/" ? can we guarantee we do not receive that ?
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

    def test_empty_response_to_error_terminated_rmdir(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 916 916 (rm) rmdir 1319227056527181-26 /local/ourgrid/gp_hash_table_map_ -1".split())
        self.assertEquals([], ac_dirs)
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)


    def test_accessed_and_created_unlink(self):
        #FIXME what if the directory terminates with "/" ? can we guarantee we do not receive that ?
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/ourgrid/debug_no_store_hash_fn_imps.hpp 0".split())
        self.assertEquals(
                          [
                           "/local/ourgrid",
                           "/local",                  
                          ],
                          ac_dirs
                         )
        self.assertEquals(["debug_no_store_hash_fn_imps.hpp"], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_empty_response_to_error_terminated_unlink(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/ourgrid/debug_no_store_hash_fn_imps.hpp -1".split())
        self.assertEquals([], ac_dirs)
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)


    def test_accessed_and_created_stat(self):
        #FIXME what if the directory terminates with "/" ? can we guarantee we do not receive that ?
        #FIXME stat can run over files and directories ?
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("65534 1856 1867 (gmetad) stat 1319227151896626-113 /var/__SummaryInfo__/cpu_idle.rrd 0".split())
        self.assertEquals(
                          [
                           "/var/__SummaryInfo__",
                           "/var",
                          ],
                          ac_dirs
                         )
        self.assertEquals(["cpu_idle.rrd"], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_empty_response_error_stat(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("65534 1856 1867 (gmetad) stat 1319227151896626-113 /var/__SummaryInfo__/cpu_idle.rrd -1".split())
        self.assertEquals([], ac_dirs)
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_read(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 1079 921 (automount) read 1319227058854877-191 /proc/1079/mounts 5 1024 1024".split())
        self.assertEquals(
                          [
                           "/proc/1079",
                           "/proc",
                          ],
                          ac_dirs
                         )
        self.assertEquals(["mounts"], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_empty_response_error_read(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 1079 921 (automount) read 1319227058854877-191 /proc/1079/mounts 5 1024 -3".split())
        self.assertEquals([], ac_dirs )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_write(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 1079 921 (automount) write 1319227058854877-191 /proc/1079/mounts 5 1024 1024".split())
        self.assertEquals(
                          [
                           "/proc/1079",
                           "/proc",
                          ],
                          ac_dirs
                         )
        self.assertEquals(["mounts"], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_empty_response_error_write(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 1079 921 (automount) write 1319227058854877-191 /proc/1079/mounts 5 1024 -3".split())
        self.assertEquals([], ac_dirs )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

if __name__ == '__main__':
    unittest.main()
