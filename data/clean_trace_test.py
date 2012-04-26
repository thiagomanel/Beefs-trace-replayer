import unittest
from clean_trace import *

class TestCleanTrace(unittest.TestCase):

    def test_fstat(self):
        self.assertEquals(
             clean_fstat("65534 1856 1867 (gmetad) sys_fstat64 1319227151912074-154 5 0".split(), None).raw_str(),
                         "65534 1856 1867 (gmetad) fstat 1319227151912074-154 5 0")

    def test_rmdir(self):
        self.assertEquals(
            clean_rmdir("0 916 916 (rm) vfs_rmdir 1319227056527181-26 (/ /local/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_ 0  2982629) 0".split()).raw_str(),
                         "0 916 916 (rm) rmdir 1319227056527181-26 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_ 0")

    def test_clean_unlink(self):
        self.assertEquals(
            clean_unlink("1159 2364 32311 (eclipse) unlink 1318539134533662-8118  (/ /local/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0".split()).raw_str(), 
                         "1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp 0")

        self.assertEquals(
            clean_unlink("1159 2364 32311 (eclipse) unlink 1318539134533662-8118  (/ /local/ /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0".split()).raw_str(),
                         "1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp 0")

    def test_clean_mkdir(self):
        self.assertEquals(
          clean_mkdir(
                "65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 / /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17".split()).raw_str(),
                "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17")

        self.assertEquals(
          clean_mkdir(
                "65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 /var/lib/ ganglia/rrds/__SummaryInfo__ 493 -17".split()).raw_str(),
                "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17")

    def test_clean_stat(self):
         self.assertEquals(
           clean_stat(
              "65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 / /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0".split()).raw_str(),
              "65534 1856 1867 (gmetad) stat 1319227151896626-113 /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0")

         self.assertEquals(
           clean_stat(
              "65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 /var/lib/ ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0".split()).raw_str(),
              "65534 1856 1867 (gmetad) stat 1319227151896626-113 /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0")

    def test_clean_open(self):
        self.assertEquals(
            clean_open("0 940 940 (tar) sys_open 1319227153693893-147 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5".split()).raw_str(),
                       "0 940 940 (tar) open 1319227153693893-147 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5")

        self.assertEquals(
            clean_open("0 940 940 (tar) sys_open 1319227153693893-147 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ /home/usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5".split()).raw_str(),
                       "0 940 940 (tar) open 1319227153693893-147 /home/usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5")

    def test_clean_close(self):
        self.assertEquals(
             clean_close("0 2413 2413 (udisks-daemon) sys_close 1319227059005785-541 7 0".split()).raw_str(),
             "0 2413 2413 (udisks-daemon) close 1319227059005785-541 7 0")

    def test_process_open_write_close(self):
        lines = [
                 "0 940 940 (tar) sys_open 1319227082315205-101 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ bin/sync 32961 448 5",
                 "0 940 940 (tar) sys_write 1319227082315340-189 (/ /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/bin/sync/ 0 S_IFREG|S_IRWXU 1376472) 5 5120 5120",
                 "0 940 940 (tar) sys_close 1319227082316153-73 5 0"]

        out, err = Collector([]), Collector([])
        clean(lines, out, err)
        cleaned_lines = out
        self.assertEquals(len(cleaned_lines), 3)
        self.assertEquals(CleanCall.from_str(cleaned_lines[0]).raw_str(),
              "0 940 940 (tar) open 1319227082315205-101 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/bin/sync 32961 448 5")
        self.assertEquals(CleanCall.from_str(cleaned_lines[1]).raw_str(),
              "0 940 940 (tar) write 1319227082315340-189 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/bin/sync 5 5120 5120")
        self.assertEquals(CleanCall.from_str(cleaned_lines[2]).raw_str(), "0 940 940 (tar) close 1319227082316153-73 5 0")

    def test_process_open_write_close_missing_write_args(self):
        #Sometimes write operations does not come with the full args list see below from a real trace
        #FULL ARGS -> 0 18462 18475 (java) sys_write 1319227079842169-123 (/ /local/pjd_test_beefs_version/bin/ /tmp/Queenbee.lg/ 11525 S_IFREG|S_IROTH|S_IRGRP|S_IWUSR|S_IRUSR 156812) 25 5 5
        #ARGS MISSING -> 0 18462 18475 (java) sys_write 1319227079842477-85  25 5 5

        lines = [
                 "0 940 940 (tar) sys_open 1319227082315205-101 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ bin/sync 32961 448 5",
                 "0 940 940 (tar) sys_write 1319227082315340-189 5 5120 5120",
                 "0 940 940 (tar) sys_close 1319227082316153-73 5 0"]

        out, err = Collector([]), Collector([])
        clean(lines, out, err)
        cleaned_lines = out
        self.assertEquals(len(cleaned_lines), 3)
        self.assertEquals(CleanCall.from_str(cleaned_lines[0]).raw_str(),
              "0 940 940 (tar) open 1319227082315205-101 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/bin/sync 32961 448 5")
        self.assertEquals(CleanCall.from_str(cleaned_lines[1]).raw_str(),
              "0 940 940 (tar) write 1319227082315340-189 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/bin/sync 5 5120 5120")
        self.assertEquals(CleanCall.from_str(cleaned_lines[2]).raw_str(), "0 940 940 (tar) close 1319227082316153-73 5 0")

    def test_process_open_read_close(self):
        lines = [
                 "0 1079 921 (automount) sys_open 1319227058853999-612 / /home/1079/mounts 32768 438 5",
                 "0 1079 921 (automount) sys_read 1319227058854877-191 (/ / /home/1079/mounts/ 0 S_IFREG|S_IROTH|S_IRGRP|S_IRUSR 6496077) 5 1024 1024"
                ]

        out, err = Collector([]), Collector([])
        clean(lines, out, err)
        cleaned_lines = out
        self.assertEquals(len(cleaned_lines), 2)
        self.assertEquals(CleanCall.from_str(cleaned_lines[0]).raw_str(),
                 "0 1079 921 (automount) open 1319227058853999-612 /home/1079/mounts 32768 438 5")
        self.assertEquals(CleanCall.from_str(cleaned_lines[1]).raw_str(),
                 "0 1079 921 (automount) read 1319227058854877-191 /home/1079/mounts 5 1024 1024")

    def test_clean_llseek(self):
        lines = [
                 "0 1079 921 (automount) sys_open 1319227058853999-612 / /home/myfile 32768 438 5",
                 "0 1079 921 (automount) sys_llseek 1319203801723656-31 5 4294967295 4294967290 SEEK_CUR 708",
                 "0 1079 921 (automount) sys_llseek 1319229169389520-32 5 0 0 SEEK_END 1279166",
                 "0 1079 921 (automount) sys_llseek 1319203351781638-8 5 0 459120 SEEK_SET 459120"]


        out, err = Collector([]), Collector([])
        clean(lines, out, err)
        cleaned_lines = out

        self.assertEquals(len(cleaned_lines), 4)
        self.assertEquals(CleanCall.from_str(cleaned_lines[0]).raw_str(),
                 "0 1079 921 (automount) open 1319227058853999-612 /home/myfile 32768 438 5")
        self.assertEquals(CleanCall.from_str(cleaned_lines[1]).raw_str(),
                 "0 1079 921 (automount) llseek 1319203801723656-31 /home/myfile 5 4294967295 4294967290 SEEK_CUR 708")
        self.assertEquals(CleanCall.from_str(cleaned_lines[2]).raw_str(),
                 "0 1079 921 (automount) llseek 1319229169389520-32 /home/myfile 5 0 0 SEEK_END 1279166")
        self.assertEquals(CleanCall.from_str(cleaned_lines[3]).raw_str(),
                 "0 1079 921 (automount) llseek 1319203351781638-8 /home/myfile 5 0 459120 SEEK_SET 459120")

    def test_path_with_empty_spaces(self):
        lines = [
                "1159 16303 16325 (chrome) sys_open 1319206526399866-340 /home/thiagoepdc/ /home/thiagoepdc/.config/google-chrome/Safe Browsing Bloom-journal 32834 420 58"]

        out, err = Collector([]), Collector([])
        clean(lines, out, err)
        cleaned_lines = out

        self.assertEquals(len(cleaned_lines), 1)
        self.assertEquals(CleanCall.from_str(cleaned_lines[0]).raw_str(),
                "1159 16303 16325 (chrome) open 1319206526399866-340 /home/thiagoepdc/.config/google-chrome/Safe Browsing Bloom-journal 32834 420 58")

    def test_process_open_fstat(self):

        lines = [
                "0 940 940 (tar) sys_open 1319227152428649-145 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ usr/lib/libg.a 32961 384 5",
                "0 940 940 (tar) sys_fstat64 1319227152430169-186 5 0"
                ]
        out, err = Collector([]), Collector([])
        clean(lines, out, err)
        cleaned_lines = out

        self.assertEquals(len(cleaned_lines), 2)
        self.assertEquals(CleanCall.from_str(cleaned_lines[0]).raw_str(),
                "0 940 940 (tar) open 1319227152428649-145 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/lib/libg.a 32961 384 5")
        self.assertEquals(CleanCall.from_str(cleaned_lines[1]).raw_str(),
                "0 940 940 (tar) fstat 1319227152430169-186 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/lib/libg.a 5 0")

    def test_clean_lines(self):
        lines_tokens =  ["1159 2364 32311 (eclipse) vfs_unlink 1318539134533662-8118  (/ /home/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0", 
                         "1159 2364 32311 (eclipse) vfs_unlink 1318539134533662-8118  (/ /home/ /home/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0",
                         "65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 / /home/lib/ganglia/rrds/__SummaryInfo__ 493 -17",
                         "65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 /home/lib/ ganglia/rrds/__SummaryInfo__ 493 -17",
                         "65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 / /home/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0",
                         "65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 /home/lib/ ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0",
                         "0 940 940 (tar) sys_open 1319227153693893-147 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5",
                         "0 940 940 (tar) sys_open 1319227153693893-147 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ /home/lib/python2.5/encodings/euc_jp.pyc 32961 384 6", 
                         "0 940 940 (udisks-daemon) sys_close 1319227059005785-541 6 0"]

        out, err = Collector([]), Collector([])
        clean(lines_tokens, out, err)
        cleaned_lines = out
        self.assertEquals(len(cleaned_lines), 9)

        self.assertEquals(CleanCall.from_str(cleaned_lines[0]).raw_str(),
                          "1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /home/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp 0")
        self.assertEquals(CleanCall.from_str(cleaned_lines[1]).raw_str(),
                          "1159 2364 32311 (eclipse) unlink 1318539134533662-8118 /home/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp 0")
        self.assertEquals(CleanCall.from_str(cleaned_lines[2]).raw_str(),
                           "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /home/lib/ganglia/rrds/__SummaryInfo__ 493 -17")
        self.assertEquals(CleanCall.from_str(cleaned_lines[3]).raw_str(),
                           "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /home/lib/ganglia/rrds/__SummaryInfo__ 493 -17")
        self.assertEquals(CleanCall.from_str(cleaned_lines[4]).raw_str(),
                           "65534 1856 1867 (gmetad) stat 1319227151896626-113 /home/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0")
        self.assertEquals(CleanCall.from_str(cleaned_lines[5]).raw_str(),
                           "65534 1856 1867 (gmetad) stat 1319227151896626-113 /home/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0")
        self.assertEquals(CleanCall.from_str(cleaned_lines[6]).raw_str(),
                           "0 940 940 (tar) open 1319227153693893-147 /home/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5")
        self.assertEquals(CleanCall.from_str(cleaned_lines[7]).raw_str(),
                           "0 940 940 (tar) open 1319227153693893-147 /home/lib/python2.5/encodings/euc_jp.pyc 32961 384 6")
        self.assertEquals(CleanCall.from_str(cleaned_lines[8]).raw_str(),
                           "0 940 940 (udisks-daemon) close 1319227059005785-541 6 0")

    def test_clean_lines_excluding_non_home(self):
        lines_tokens =  ["1159 2364 32311 (eclipse) vfs_unlink 1318539134533662-8118  (/ /local/ourgrid/worker_N2/ ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0",
                         "1159 2364 32311 (eclipse) vfs_unlink 1318539134533662-8118  (/ /local/ /local/ourgrid/worker_N2/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/usr/include/c++/4.3/ext/pb_ds/detail/gp_hash_table_map_/debug_no_store_hash_fn_imps.hpp -1 null -1) 0",
                         "65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 / /var/lib/ganglia/rrds/__SummaryInfo__ 493 -17",
                         "65534 1856 1856 (gmetad) sys_mkdir 1318615768915818-17 /var/lib/ ganglia/rrds/__SummaryInfo__ 493 -17",
                         "65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 / /var/lib/ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0",
                         "65534 1856 1867 (gmetad) sys_stat64 1319227151896626-113 /var/lib/ ganglia/rrds/BeeFS/__SummaryInfo__/cpu_idle.rrd 0",
                         "0 940 940 (tar) sys_open 1319227153693893-147 /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ usr/lib/python2.5/encodings/euc_jp.pyc 32961 384 5",
                         "0 940 940 (tar) sys_open 1319227153693893-147 /local/ourgrid/vserver_images/worker.lsd.ufcg.edu.br_2/ /use/lib/python2.5/encodings/euc_jp.pyc 32961 384 6",
                         "0 2413 2413 (udisks-daemon) sys_close 1319227059005785-541 7 0"]

        out, err = Collector([]), Collector([])
        clean(lines_tokens, out, err)
        cleaned_lines = out
        self.assertEquals(len(cleaned_lines), 0)

if __name__ == '__main__':
    unittest.main()
