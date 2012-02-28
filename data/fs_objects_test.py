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

    def test_accessed_and_created_llseek(self):
        #FIXME LLSEEK run for both files and directories
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 916 916 (rm) llseek 1319227065620757-4 /local/ourgrid/R-ex/file 20 SEEK_SET 20".split())
        self.assertEquals(
                          [
                           "/local/ourgrid/R-ex",
                           "/local/ourgrid",
                           "/local"
                          ],
                          ac_dirs
                         )
        self.assertEquals(["file"], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_empty_response_error_llseeek(self):
        #FIXME check if our systap scripts is really outputing return value
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 916 916 (rm) llseek 1319227065620757-4 /local/ourgrid/R-ex/file 0 SEEK_SET -1".split())
        self.assertEquals([], ac_dirs )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_mkdir(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /var/lib/ganglia/rrds/__SummaryInfo__ 493 0".split())
        self.assertEquals(
                          [
                           "/var/lib/ganglia/rrds",
                           "/var/lib/ganglia",
                           "/var/lib",
                           "/var",
                          ],
                          ac_dirs
                         )
        self.assertEquals([], ac_files)
        self.assertEquals(["__SummaryInfo__"], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_empty_response_error_mkdir(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17".split())
        self.assertEquals([], ac_dirs )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_open_non_create(self):
        #FIXME: we need flags for create and for non-create
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 940 940 (tar) open 1319227153693893-147 /usr/lib/euc_jp.pyc 2 384 5".split())
        self.assertEquals(
                          [
                           "/usr/lib",
                           "/usr",
                          ],
                          ac_dirs
                         )
        self.assertEquals(["euc_jp.pyc"], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_open_create(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 940 940 (tar) open 1319227153693893-147 /usr/lib/euc_jp.pyc 66 384 5".split())
        self.assertEquals(
                          [
                           "/usr/lib",
                           "/usr",
                          ],
                          ac_dirs
                         )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals(["euc_jp.pyc"], cr_files)

#66,

    def test_accessed_and_created_empty_response_error_open(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 940 940 (tar) open 1319227153693893-147 /usr/lib/euc_jp.pyc 32961 384 -3".split())
        self.assertEquals([], ac_dirs )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

if __name__ == '__main__':
    unittest.main()
