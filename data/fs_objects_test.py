import unittest
from fs_objects import *


class TestFSObjects(unittest.TestCase):

    def assertDictEquals(self, actual, expected):
        self.assertEquals(actual.keys(), expected.keys())
        for (k, v) in actual.iteritems():
            self.assertTrue(k in expected)
            self.assertEquals(actual[k], expected[k])

    def test_fs_tree_unusual_dir_operations(self):
        lines = [
                 WorkflowLine(1, [], [2], CleanCall("0", "916", "916", "(rm)", "rmdir", "100-26", ["/ok_rmdir/lib/gp_hash_table_map_"], "0")),
                 WorkflowLine(2, [1], [3], CleanCall("0", "916", "916", "(rm)", "rmdir", "101-26", ["/error_rmdir/lib/gp_hash_table_map_2"], "-1")),
                 WorkflowLine(3, [2], [4], CleanCall("0", "1079", "921", "(automount)", "read", "106-191", ["/dir2/lib", "5", "1024"], "1024")),
                 WorkflowLine(4, [3], [5], CleanCall("0", "1079", "921", "(automount)", "read", "107-191", ["/dir2/lib2/ha", "5", "1024"], "1024")),
                 WorkflowLine(5, [4], [],  CleanCall("0", "1079", "921", "(automount)", "read", "108-191", ["/dir2/lib/ffu.txt", "5", "1024"], "1024"))
                ]

        tree = fs_tree(lines)

        expected_tree = {
            ("/ok_rmdir", "d") : set([("/ok_rmdir/lib", "d")]),
            ("/ok_rmdir/lib", "d") : set([("/ok_rmdir/lib/gp_hash_table_map_", "d")]),
            ("/dir2", "d") : set([("/dir2/lib", "d"), ("/dir2/lib2", "d")]),
            ("/dir2/lib2", "d") : set([("/dir2/lib2/ha", "f")]),
            ("/dir2/lib", "d") : set([("/dir2/lib/ffu.txt", "f")]),
            }

        self.assertDictEquals(tree, expected_tree)

    def test_fs_tree_with_non_creational_creat_flag_undefined(self):
        lines = [
             WorkflowLine(1, [], [2], CleanCall("1159", "16303", "16325", "(chrome)", "open", "319217168627818-587", 
                                            ["/dir/Safe Browsing Bloom", "32834", "420"], "43")),
             WorkflowLine(2, [1], [3], CleanCall("1159", "16303", "16325", "(chrome)", "fstat", "1319217168628495-78", 
                                            ["/dir/Safe Browsing Bloom", "43"], "0")),
             WorkflowLine(3, [2], [0], CleanCall("1159", "16303", "16325", "(chrome)", "llseek", "1319217168628495-78", 
                                            ["/dir/Safe Browsing Bloom", "43", "0", "0", "SEEK_SET"], "0"))]#it does not imply this file existed before

        tree = fs_tree(lines)
        expected_tree = { ("/dir", "d") : set()}
        self.assertDictEquals(tree, expected_tree)

    def test_fs_tree_with_non_creational_creat_flag_falsepositive(self):
        lines = [
             WorkflowLine(1, [], [2], CleanCall("1159", "16303", "16325", "(chrome)", "open", "319217168627818-587", 
                                            ["/dir/Safe Browsing Bloom", "32834", "420"], "43")),
             WorkflowLine(2, [1], [3], CleanCall("1159", "16303", "16325", "(chrome)", "fstat", "1319217168628495-78", 
                                            ["/dir/Safe Browsing Bloom", "43"], "0")),
             WorkflowLine(3, [2], [0], CleanCall("1159", "16303", "16325", "(chrome)", "llseek", "1319217168628495-78", 
                                            ["/dir/Safe Browsing Bloom", "43", "10", "0", "SEEK_SET"], "10"))]#If we are able to seek, this file already exists

        tree = fs_tree(lines)
        expected_tree = {
                          ("/dir", "d") : set([("/dir/Safe Browsing Bloom", "f")])
                        }
        self.assertDictEquals(tree, expected_tree)


    def test_fs_tree(self):
        lines = [
                 WorkflowLine(1, [], [2], CleanCall("0", "916", "916", "(rm)", "rmdir", "1319227056527181-26", ["/ok_rmdir/lib/gp_hash_table_map_"], "0")),
                 WorkflowLine(2, [1], [3], CleanCall("0", "916", "916", "(rm)", "rmdir", "1319227056527181-26", ["/error_rmdir/lib/gp_hash_table_map_2"], "-1")),
                 WorkflowLine(3, [2], [4], CleanCall("1159", "2364", "32311", "(eclipse)", "unlink", "1318539134533662-8118", ["/ok_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp"], "0")),
                 WorkflowLine(4, [3], [5], CleanCall("1159", "2364", "32311", "(eclipse)", "unlink", "1318539134533662-8118",  ["/error_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp1"], "-1")),
                 WorkflowLine(5, [4], [6], CleanCall("65534", "1856", "1867" , "(gmetad)", "stat", "1319227151896626-113", ["/ok_stat/__SummaryInfo__/cpu_idle.rrd"], "0")),
                 WorkflowLine(6, [5], [7], CleanCall("65534", "1856", "1867", "(gmetad)", "stat", "1319227151896626-113", ["/error_stat/__SummaryInfo__/cpu_idle.rrd"], "-1")),
                 WorkflowLine(7, [6], [8], CleanCall("0", "1079", "921", "(automount)", "read", "1319227058854877-191", ["/ok_read/1079/mounts", "5", "1024"], "1024")),
                 WorkflowLine(8, [7], [9], CleanCall("0", "1079", "921", "(automount)", "read", "1319227058854877-191", ["/error_read/1079/mounts", "5", "1024"], "-3")),
                 WorkflowLine(9, [8], [10], CleanCall("0", "1079", "921", "(automount)", "write", "1319227058854877-191", ["/ok_write/1079/mounts", "5", "1024"], "1024")),
                 WorkflowLine(10, [9], [11], CleanCall("0", "1079", "921", "(automount)", "write", "1319227058854877-191", ["/error_write/1079/mounts", "5", "1024"], "-3")),
                 WorkflowLine(11, [10], [12], CleanCall("0", "916", "916", "(rm)", "llseek", "1319227065620757-4", ["/ok_llseek/R-ex/file", "5", "4294967295", "4294967290", "SEEK_CUR"], "708")),
                 WorkflowLine(12, [11], [13], CleanCall("0", "916", "916", "(rm)", "llseek", "1319227065620757-4", ["/error_llseek/R-ex/file", "5", "4294967295", "4294967290", "SEEK_CUR"], "-1")),
                 WorkflowLine(13, [12], [14], CleanCall("65534", "1856", "1856", "(gmetad)", "mkdir", "1318615768915818-17", ["/ok_mkdir/rrds/__SummaryInfo__", "493"], "0")),
                 WorkflowLine(14, [13], [15], CleanCall("65534", "1856", "1856", "(gmetad)", "mkdir", "1318615768915818-17", ["/error_mkdir/rrds/__SummaryInfo__", "493"], "-17")),
                 WorkflowLine(15, [14], [16], CleanCall("0", "940", "940", "(tar)", "open", "1319227153693893-147", ["/ok_open/lib/euc_jp.pyc", "2", "384"], "5")),
                 WorkflowLine(16, [15], [17], CleanCall("0", "940", "940", "(tar)", "open", "1319227153693893-147", ["/create/lib/euc_jp.pyc", "66", "384"], "5")),#open to create
                 WorkflowLine(17, [16], [], CleanCall("0", "940", "940", "(tar)", "open", "1319227153693893-147", ["/error_open/lib/euc_jp.pyc", "32961", "384"], "-3"))
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
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(
            CleanCall("0", "916", "916", "(rm)", "rmdir", "1319227056527181-26", ["/local/ourgrid/gp_hash_table_map_"], "0"))

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
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("0", "916", "916", "(rm)", "rmdir", "1319227056527181-26", ["/local/ourgrid/gp_hash_table_map_"], "-1"))
        self.assertEquals([], ac_dirs)
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)


    def test_accessed_and_created_unlink(self):
        #FIXME what if the directory terminates with "/" ? can we guarantee we do not receive that ?
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("1159", "2364", "32311", "(eclipse)", "unlink", "1318539134533662-8118", ["/local/ourgrid/debug_no_store_hash_fn_imps.hpp"], "0"))
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
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("1159", "2364", "32311", "(eclipse)", "unlink", "1318539134533662-8118", ["/local/ourgrid/debug_no_store_hash_fn_imps.hpp"], "-1"))
        self.assertEquals([], ac_dirs)
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)


    def test_accessed_and_created_stat(self):
        #FIXME what if the directory terminates with "/" ? can we guarantee we do not receive that ?
        #FIXME stat can run over files and directories ?
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("65534", "1856", "1867", "(gmetad)", "stat", "1319227151896626-113", ["/var/__SummaryInfo__/cpu_idle.rrd"], "0"))
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
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("65534", "1856", "1867", "(gmetad)", "stat", "1319227151896626-113", ["/var/__SummaryInfo__/cpu_idle.rrd"], "-1"))
        self.assertEquals([], ac_dirs)
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_read(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("0", "1079", "921", "(automount)", "read", "1319227058854877-191", ["/proc/1079/mounts", "5", "1024"], "1024"))
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
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("0", "1079", "921", "(automount)", "read", "1319227058854877-191", ["/proc/1079/mounts", "5", "1024"], "-3"))
        self.assertEquals([], ac_dirs )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_write(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("0", "1079", "921", "(automount)", "write", "1319227058854877-191", ["/proc/1079/mounts", "5", "1024"], "1024"))
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
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("0", "1079", "921", "(automount)", "write", "1319227058854877-191", ["/proc/1079/mounts", "5", "1024"], "-3"))
        self.assertEquals([], ac_dirs )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_llseek(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(
            CleanCall("0", "916", "916", "(rm)", "llseek", "1319227065620757-4", ["/local/ourgrid/R-ex/file", "5", "4294967295", "4294967290", "SEEK_CUR"], "708"))
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
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(
            CleanCall("0", "916", "916", "(rm)", "llseek", "1319227065620757-4", ["/local/ourgrid/R-ex/file", "5", "4294967295", "4294967290", "SEEK_CUR"], "-1"))
        self.assertEquals([], ac_dirs )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_mkdir(self):
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("65534", "1856", "1856", "(gmetad)", "mkdir", "1318615768915818-17", ["/var/lib/ganglia/rrds/__SummaryInfo__", "493"], "0"))
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
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("65534", "1856", "1856", "(gmetad)", "mkdir", "1318615768915818-17", ["/var/lib/ganglia/rrds/__SummaryInfo__",  "493"], "-17"))
        self.assertEquals([], ac_dirs )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

    def test_accessed_and_created_open_non_create(self):
        #FIXME: we need flags for create and for non-create
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("0", "940", "940", "(tar)", "open", "1319227153693893-147", ["/usr/lib/euc_jp.pyc", "2", "384"], "5"))
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
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("0", "940", "940", "(tar)", "open", "1319227153693893-147", ["/usr/lib/euc_jp.pyc", "66", "384"], "5"))
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
        ac_dirs, ac_files, cr_dirs, cr_files = accessed_and_created(CleanCall("0", "940", "940", "(tar)", "open", "1319227153693893-147", ["/usr/lib/euc_jp.pyc", "32961", "384"], "-3"))
        self.assertEquals([], ac_dirs )
        self.assertEquals([], ac_files)
        self.assertEquals([], cr_dirs)
        self.assertEquals([], cr_files)

if __name__ == '__main__':
    unittest.main()
