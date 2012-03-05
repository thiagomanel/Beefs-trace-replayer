import unittest
from fs_objects import *


class TestFSObjects(unittest.TestCase):

    def assertDictEquals(self, actual, expected):
        self.assertEquals(actual.keys(), expected.keys())
        for (k, v) in actual.iteritems():
            self.assertTrue(k in expected)
            self.assertEquals(actual[k], expected[k])

    def test_fs_tree(self):
        lines = [
                 "1 0 - 1 2 0 916 916 (rm) rmdir 1319227056527181-26 /ok_rmdir/lib/gp_hash_table_map_ 0",
                 "2 1 1 1 3 0 916 916 (rm) rmdir 1319227056527181-26 /error_rmdir/lib/gp_hash_table_map_2 -1",
                 "3 1 2 1 4 1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /ok_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp 0",
                 "4 1 3 1 5 1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /error_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp1 -1",
                 "5 1 4 1 6 65534 1856 1867 (gmetad) stat 1319227151896626-113 /ok_stat/__SummaryInfo__/cpu_idle.rrd 0",
                 "6 1 5 1 7 65534 1856 1867 (gmetad) stat 1319227151896626-113 /error_stat/__SummaryInfo__/cpu_idle.rrd -1",
                 "7 1 6 1 8 0 1079 921 (automount) read 1319227058854877-191 /ok_read/1079/mounts 5 1024 1024",
                 "8 1 7 1 9 0 1079 921 (automount) read 1319227058854877-191 /error_read/1079/mounts 5 1024 -3",
                 "9 1 8 1 10 0 1079 921 (automount) write 1319227058854877-191 /ok_write/1079/mounts 5 1024 1024",
                 "10 1 9 1 11 0 1079 921 (automount) write 1319227058854877-191 /error_write/1079/mounts 5 1024 -3",
                 "11 1 10 1 12 0 916 916 (rm) llseek 1319227065620757-4 /ok_llseek/R-ex/file 20 SEEK_SET 20",
                 "12 1 11 1 13 0 916 916 (rm) llseek 1319227065620757-4 /error_llseek/R-ex/file 0 SEEK_SET -1",
                 "13 1 12 1 14 65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /ok_mkdir/rrds/__SummaryInfo__ 493 0",
                 "14 1 13 1 15 65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /error_mkdir/rrds/__SummaryInfo__ 493 -17",
                 "15 1 14 1 16 0 940 940 (tar) open 1319227153693893-147 /ok_open/lib/euc_jp.pyc 2 384 5",
                 "16 1 15 1 17 0 940 940 (tar) open 1319227153693893-147 /create/lib/euc_jp.pyc 66 384 5",#open to create
                 "17 1 16 0 - 0 940 940 (tar) open 1319227153693893-147 /error_open/lib/euc_jp.pyc 32961 384 -3"
                ]

        tree = fs_tree(lines)

        #assert the total number of keys
        expected_tree = {
            ("/ok_rmdir", "d") : set([("/ok_rmdir/lib", "d")]),
            ("/ok_rmdir/lib", "d") : set([("/ok_rmdir/lib/gp_hash_table_map_", "d")]),
            ("/ok_unlink", "d") : set([("/ok_unlink/ourgrid", "d")]),
            ("/ok_unlink/ourgrid", "d") : set([("/ok_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp", "f")]), 
            ("/ok_stat", "d") : set([("/ok_stat/__SummaryInfo__", "d")]),
            ("/ok_stat/__SummaryInfo__", "d") : set([("/ok_stat/__SummaryInfo__/cpu_idle.rrd", "f")]),
            ("/ok_read", "d") : set([("/ok_read/1079", "d")]),
            ("/ok_read/1079", "d") : set([("/ok_read/1079/mounts", "f")]),
            ("/ok_write", "d") : set([("/ok_write/1079", "d")]),
            ("/ok_write/1079", "d") : set([("/ok_write/1079/mounts", "f")]),
            ("/ok_llseek", "d") : set([("/ok_llseek/R-ex", "d")]),
            ("/ok_llseek/R-ex", "d") : set([("/ok_llseek/R-ex/file", "f")]),
            ("/ok_mkdir", "d") : set([("/ok_mkdir/rrds", "d")]),
            ("/ok_open", "d") : set([("/ok_open/lib", "d")]),
            ("/ok_open/lib", "d") : set([("/ok_open/lib/euc_jp.pyc", "f")]),
            ("/create", "d") : set([("/create/lib", "d")]),
            }

        self.assertDictEquals(tree, expected_tree)

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
        self.assertEquals(["/local/ourgrid/debug_no_store_hash_fn_imps.hpp"], ac_files)
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
        self.assertEquals(["/var/__SummaryInfo__/cpu_idle.rrd"], ac_files)
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
        self.assertEquals(["/proc/1079/mounts"], ac_files)
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
        self.assertEquals(["/proc/1079/mounts"], ac_files)
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
        self.assertEquals(["/local/ourgrid/R-ex/file"], ac_files)
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
        self.assertEquals(["/var/lib/ganglia/rrds/__SummaryInfo__"], cr_dirs)
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
        self.assertEquals(["/usr/lib/euc_jp.pyc"], ac_files)
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
        self.assertEquals(["/usr/lib/euc_jp.pyc"], cr_files)

#66,

    def test_accessed_and_created_empty_response_error_open(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created("0 940 940 (tar) open 1319227153693893-147 /usr/lib/euc_jp.pyc 32961 384 -3".split())
        self.assertEquals([], ac_dirs )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

if __name__ == '__main__':
    unittest.main()
