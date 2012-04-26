import unittest
import os
from pre_replay import *

class TestTraceWalk(unittest.TestCase):

    def fs_object(to_create):
        return to_create[0]

    def fs_type(to_create):
        return to_create[1]

    def test_fsobjects_to_be_created(self):
        lines = [
                 WorkflowLine(1, [], [2], CleanCall("0", "916", "916", "(rm)", "rmdir", "1319227056527181-26", ["/ok_rmdir/lib/gp_hash_table_map_"], "0")),
                 WorkflowLine(2, [1], [3], CleanCall("0", "916", "916", "(rm)", "rmdir", "1319227056527181-26", ["/error_rmdir/lib/gp_hash_table_map_2"], "-1")),
                 WorkflowLine(3, [2], [4], CleanCall("1159", "2364", "32311", "(eclipse)", "unlink", "1318539134533662-8118", ["/ok_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp"], "0")),
                 WorkflowLine(4, [3], [5], CleanCall("1159", "2364", "32311", "(eclipse)", "unlink", "1318539134533662-8118", ["/error_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp1"], "-1")),
                 WorkflowLine(5, [4], [6], CleanCall("65534", "1856", "1867", "(gmetad)", "stat", "1319227151896626-113", ["/ok_stat/__SummaryInfo__/cpu_idle.rrd"], "0")),
                 WorkflowLine(6, [5], [7], CleanCall("65534", "1856", "1867", "(gmetad)", "stat", "1319227151896626-113", ["/error_stat/__SummaryInfo__/cpu_idle.rrd"], "-1")),
                 WorkflowLine(7, [6], [8], CleanCall("0", "1079", "921", "(automount)", "read", "1319227058854877-191", ["/ok_read/1079/mounts", "5", "1024"], "1024")),
                 WorkflowLine(8, [7], [9], CleanCall("0", "1079", "921", "(automount)", "read", "1319227058854877-191", ["/error_read/1079/mounts", "5", "1024"], "-3")),
                 WorkflowLine(9, [8], [10], CleanCall("0", "1079", "921", "(automount)", "write", "1319227058854877-191", ["/ok_write/1079/mounts", "5", "1024"], "1024")),
                 WorkflowLine(10, [9], [11], CleanCall("0", "1079", "921", "(automount)", "write", "1319227058854877-191", ["/error_write/1079/mounts", "5", "1024"], "-3")),
                 WorkflowLine(11, [10], [12], CleanCall("0", "916", "916", "(rm)", "llseek", "1319227065620757-4", ["/ok_llseek/R-ex/file", "0", "4294967295", "4294967295", "SEEK_CUR"], "20")),
                 WorkflowLine(12, [11], [13], CleanCall("0", "916", "916", "(rm)", "llseek", "1319227065620757-4", ["/error_llseek/R-ex/file", "0", "4294967295", "4294967295", "SEEK_SET"], "-1")),
                 WorkflowLine(13, [12], [14], CleanCall("65534", "1856", "1856", "(gmetad)", "mkdir", "1318615768915818-17", ["/ok_mkdir/rrds/__SummaryInfo__", "493"], "0")),
                 WorkflowLine(14, [13], [15], CleanCall("65534", "1856", "1856", "(gmetad)", "mkdir", "1318615768915818-17", ["/error_mkdir/rrds/__SummaryInfo__", "493"], "-17")),
                 WorkflowLine(15, [14], [16], CleanCall("0", "940", "940", "(tar)", "open", "1319227153693893-147", ["/ok_open/lib/euc_jp.pyc", "2", "384"], "5")),
                 WorkflowLine(16, [15], [17], CleanCall("0", "940", "940", "(tar)", "open", "1319227153693893-147", ["/create/lib/euc_jp.pyc", "66", "384"], "5")),#open to create
                 WorkflowLine(17, [16], [], CleanCall("0", "940", "940", "(tar)", "open", "1319227153693893-147", ["/error_open/lib/euc_jp.pyc", "32961", "384"], "-3"))
                ]
        #test if a path cannot be shown twice
        replay_dir = "/tmp/replay"
        to_create_dirs, to_create_files = build_namespace(replay_dir, lines)
        #print to_create_dirs, to_create_files

        self.assertTrue(replay_dir + "/ok_rmdir/lib/gp_hash_table_map_" in to_create_dirs)
        self.assertTrue(replay_dir + "/ok_rmdir/lib" in to_create_dirs)
        self.assertTrue(replay_dir + "/ok_rmdir" in to_create_dirs)
        self.assertFalse(replay_dir + "/error_rmdir/lib/gp_hash_table_map_2" in to_create_dirs)
        self.assertFalse(replay_dir + "/error_rmdir/lib" in to_create_dirs)
        self.assertFalse(replay_dir + "/error_rmdir" in to_create_dirs)

        self.assertTrue(replay_dir + "/ok_unlink/ourgrid" in to_create_dirs)
        self.assertTrue(replay_dir + "/ok_unlink" in to_create_dirs)
        self.assertTrue(replay_dir + "/ok_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp" in to_create_files)
        self.assertFalse(replay_dir + "/error_unlink/ourgrid/debug_no_store_hash_fn_imps.hpp1" in to_create_files)
        self.assertFalse(replay_dir + "/error_unlink/ourgrid" in to_create_dirs)
        self.assertFalse(replay_dir + "/error_unlink" in to_create_dirs)
        #FIXME add assert for all of lines list


    def test_create_dir_on_open(self):
        # it was due a bug on replay
        if os.path.exists("/tmp/test/home/tiagohsl/.java/"):
            os.removedirs("/tmp/test/home/tiagohsl/.java/")
        os.makedirs("/tmp/test/home/tiagohsl/.java/")

        lines = [
                 WorkflowLine(1, [], [], CleanCall("1007", "19656", "19834", "(eclipse)", "open", "1319217018156867-563",["/home/tiagohsl/.java/.userPrefs/.user.lock.tiagohsl", "65", "384"], "108")),
                 WorkflowLine(2, [], [], CleanCall("1007", "23211", "23221", "(chromium-browse)", "open", "1319217020939991-757", ["/home/tiagohsl/.config/chromium/Default/Cookies-journal", "32834", "420"], "79"))]

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
