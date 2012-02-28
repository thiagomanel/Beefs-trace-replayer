import unittest
from pre_replay import *

class TestTraceWalk(unittest.TestCase):

    def test_objects_tobe_createdr(self):
        lines = [
                 "0 916 916 (rm) rmdir 1319227056527181-26 /ok_rmdir/lib/gp_hash_table_map_ 0",
                 "0 916 916 (rm) rmdir 1319227056527181-26 /error_rmdir/lib/gp_hash_table_map_2 -1",
                 "1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /ok_unlinkl/ourgrid/debug_no_store_hash_fn_imps.hpp 0",
                 "1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /error_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp1 -1",
                 "65534 1856 1867 (gmetad) stat 1319227151896626-113 /ok_stat/__SummaryInfo__/cpu_idle.rrd 0",
                 "65534 1856 1867 (gmetad) stat 1319227151896626-113 /error_stat/__SummaryInfo__/cpu_idle.rrd -1",
                 "0 1079 921 (automount) read 1319227058854877-191 /ok_read/1079/mounts 5 1024 1024", 
                 "0 1079 921 (automount) read 1319227058854877-191 /error_read/1079/mounts 5 1024 -3",
                 "0 1079 921 (automount) write 1319227058854877-191 /ok_write/1079/mounts 5 1024 1024",
                 "0 1079 921 (automount) write 1319227058854877-191 /error_write/1079/mounts 5 1024 -3",
                 "0 916 916 (rm) llseek 1319227065620757-4 /ok_llseek/R-ex/file 20 SEEK_SET 20",
                 "0 916 916 (rm) llseek 1319227065620757-4 /error_llseek/R-ex/file 0 SEEK_SET -1",
                 "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /ok_mkdir/rrds/__SummaryInfo__ 493 0",
                 "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /error_mkdir/rrds/__SummaryInfo__ 493 -17",
                 "0 940 940 (tar) open 1319227153693893-147 /ok_open/lib/euc_jp.pyc 2 384 5",
                 "0 940 940 (tar) open 1319227153693893-147 /create/lib/euc_jp.pyc 66 384 5",#open to create
                 "0 940 940 (tar) open 1319227153693893-147 /error_open/lib/euc_jp.pyc 32961 384 -3"
                ]

if __name__ == '__main__':
    unittest.main()
