import unittest
from clean_trace import *

class TestCleanTrace(unittest.TestCase):

    def test_clean_unlink(self):
        self.assertEquals(
            clean_unlink("1159 2364 32311 (eclipse) sys_unlink 1318539134533662-8118  (/ /local/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0".split()), 
                         "1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp 0")

        self.assertEquals(
            clean_unlink("1159 2364 32311 (eclipse) sys_unlink 1318539134533662-8118  (/ /local/ /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0".split()),
                         "1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp 0")

    def test_clean_mkdir(self):
        self.assertEquals(
          clean_mkdir(
                "65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 / /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17".split()),
                "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17")

        self.assertEquals(
          clean_mkdir(
                "65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 /var/lib/ ganglia/rrds/__SummaryInfo__ 493 -17".split()),
                "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17")

    def test_clean_stat(self):
         self.assertEquals(
           clean_stat(
              "65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 / /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0".split()),
              "65534 1856 1867 (gmetad) stat 1319227151896626-113 /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0")

         self.assertEquals(
           clean_stat(
              "65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 /var/lib/ ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0".split()),
              "65534 1856 1867 (gmetad) stat 1319227151896626-113 /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0")

    def test_clean_open(self):
        self.assertEquals(
            clean_open("0 940 940 (tar) sys_open 1319227153693893-147 /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5".split()),
                       "0 940 940 (tar) open 1319227153693893-147 /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5")

        self.assertEquals(
            clean_open("0 940 940 (tar) sys_open 1319227153693893-147 /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ /usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5".split()),
                       "0 940 940 (tar) open 1319227153693893-147 /usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5")

    def clean_close(self):
        self.assertEquals(
             clean_close("0 2413 2413 (udisks-daemon) sys_close 1319227059005785-541 7 0"),
             "0 2413 2413 (udisks-daemon) close 1319227059005785-541 7 0")

    def test_clean_lines(self):
        lines_tokens = [ line.split() for line in 
                        ["1159 2364 32311 (eclipse) sys_unlink 1318539134533662-8118  (/ /local/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0", 
                         "1159 2364 32311 (eclipse) sys_unlink 1318539134533662-8118  (/ /local/ /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0",
                         "65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 / /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17",
                         "65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 /var/lib/ ganglia/rrds/__SummaryInfo__ 493 -17",
                         "65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 / /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0",
                         "65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 /var/lib/ ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0"]]

        cleaned_lines = clean(lines_tokens)

        self.assertEquals(cleaned_lines[0],
                          "1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp 0")
        self.assertEquals(cleaned_lines[1],
                          "1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp 0")
        self.assertEquals(cleaned_lines[2],
                           "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17")
        self.assertEquals(cleaned_lines[3],
                           "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17")
        self.assertEquals(cleaned_lines[4],
                           "65534 1856 1867 (gmetad) stat 1319227151896626-113 /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0")
        self.assertEquals(cleaned_lines[5],
                           "65534 1856 1867 (gmetad) stat 1319227151896626-113 /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0")


if __name__ == '__main__':
    unittest.main()
