import unittest
import os
from pre_replay import *

class TestTraceWalk(unittest.TestCase):

    def fs_object(to_create):
        return to_create[0]

    def fs_type(to_create):
        return to_create[1]

    def test_find_timestamp(self):
        lines = [
                 "1 0 - 1 2 0 916 916 (rm) rmdir 1000-26 /ok_rmdir/lib/gp_hash_table_map_ 0",
                 "2 1 1 1 3 0 916 916 (rm) rmdir 1001-26 /error_rmdir/lib/gp_hash_table_map_2 -1",
                 "3 1 2 1 4 1159 2364 32311 (eclipse) unlink 1002-8118 /ok_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp 0",
                 "4 1 3 1 5 1159 2364 32311 (eclipse) unlink 1003-8118 /error_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp1 -1",
                 "5 1 4 1 6 65534 1856 1867 (gmetad) stat 1004-113 /ok_stat/__SummaryInfo__/cpu_idle.rrd 0",
                 "6 1 5 1 7 65534 1856 1867 (gmetad) stat 1005-113 /error_stat/__SummaryInfo__/cpu_idle.rrd -1",
                 "7 1 6 1 8 0 1079 921 (automount) read 1006-191 /ok_read/1079/mounts 5 1024 1024",
                 "8 1 7 1 9 0 1079 921 (automount) read 1007-191 /ok_read/1079/mounts 5 1024 1024",
                 "9 1 8 1 10 0 1079 921 (automount) write 1008-191 /ok_write/1079/mounts 5 1024 1024",
                 "10 1 9 1 11 0 1079 921 (automount) write 1009-191 /error_write/1079/mounts 5 1024 -3",
                 "11 1 10 1 12 0 916 916 (rm) llseek 1010-4 /ok_llseek/R-ex/file 20 SEEK_SET 20",
                 "12 1 11 1 13 0 916 916 (rm) llseek 1011-4 /error_llseek/R-ex/file 0 SEEK_SET -1",
                 "13 1 12 1 14 65534 1856 1856 (gmetad) mkdir 1012-17 /ok_mkdir/rrds/__SummaryInfo__ 493 0",
                 "14 1 13 1 15 65534 1856 1856 (gmetad) mkdir 1013-17 /error_mkdir/rrds/__SummaryInfo__ 493 -17",
                 "15 1 14 1 16 0 940 940 (tar) open 1014-147 /ok_open/lib/euc_jp.pyc 2 384 5",
                 "16 1 15 1 17 0 940 940 (tar) open 1015-147 /create/lib/euc_jp.pyc 66 384 5",#open to create
                 "17 1 16 0 - 0 940 940 (tar) open 1016-147 /error_open/lib/euc_jp.pyc 32961 384 -3"
                ]

        file2timestamps = find_timestamps("", [
                          "/ok_stat/__SummaryInfo__/cpu_idle.rrd",
                          "/ok_read/1079/mounts",
                          "/ok_write/1079/mounts",
                          "/ok_llseek/R-ex/file"],
                        lines)

        self.assertEquals(file2timestamps["/ok_stat/__SummaryInfo__/cpu_idle.rrd"], None)
        self.assertEquals(file2timestamps["/ok_read/1079/mounts"], "1006-191")
        self.assertEquals(file2timestamps["/ok_write/1079/mounts"], "1008-191")
        self.assertEquals(file2timestamps["/ok_llseek/R-ex/file"], "1010-4")

    def test_find_file_size(self):
        pass

    def test_fsobjects_to_be_created(self):
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

        #test if a path cannot be shown twice
        to_create_dirs, to_create_files = build_namespace("/tmp/replay", lines)
        self.assertTrue("/ok_rmdir/lib" in to_create_dirs)

    def test_create_dir_on_open(self):
        # it was due a bug on replay
        if os.path.exists("/tmp/test/home/tiagohsl/.java/"):
            os.removedirs("/tmp/test/home/tiagohsl/.java/")
        os.makedirs("/tmp/test/home/tiagohsl/.java/")

        lines = [
                 "1 0 - 0 - 1007 19656 19834 (eclipse) open 1319217018156867-563 /home/tiagohsl/.java/.userPrefs/.user.lock.tiagohsl 65 384 108",
                 "2 0 - 0 - 1007 23211 23221 (chromium-browse) open 1319217020939991-757 /home/tiagohsl/.config/chromium/Default/Cookies-journal 32834 420 79"]

        to_create_dirs, to_create_files = build_namespace("/tmp/test", lines)
        print to_create_dirs, to_create_files
        self.assertTrue("/tmp/test/home/tiagohsl/.java/.userPrefs" in to_create_dirs)
        self.assertTrue("/tmp/test/home/tiagohsl/.config" in to_create_dirs)
        self.assertTrue("/tmp/test/home/tiagohsl/.config/chromium" in to_create_dirs)
        self.assertTrue("/tmp/test/home/tiagohsl/.config/chromium/Default" in to_create_dirs)

        os.rmdir("/tmp/test/home/tiagohsl/.java/")
        os.rmdir("/tmp/test/home/tiagohsl/")
        os.rmdir("/tmp/test/home")
        os.rmdir("/tmp/test/")

if __name__ == '__main__':
    unittest.main()
