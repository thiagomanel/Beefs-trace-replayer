import unittest
from workflow import *
from itertools import chain

class TestOrderTrace(unittest.TestCase):

#Test cases
#1. r(A) done
#2. w(A)
#3. w(A)

#1. r(A) done
#2. w(A)
#3. r(A)

#1. r(A) done
#2. r(A)
#3. r(A)

#1. w(A) done
#2. r(A)
#3. r(A)

#stat ok
#fstat ok
#rmdir ok
#mkdir ok
#unlink ok
#open
#close
#write
#read
#llseek ok
#open/create

#Open is a write operation within a process, we cannot perform write and read before open finish FIXME

#FIXME take care to not add the same dependency twice, for example, due to both pid and tid ordering
#FIXME fs_object creation sometimes do not handle directories properly, i saw both '/home/user/' '/home/user' in order_trace_test:TestOrderTrace.test_fs_order_mkdir_and_stat

#FIXME test more than one fd being used by tid
#FIXME test fd removal at close syscall

    def test_weak_fs_open_locks_the_path_and_write_read_fstat_close_touch_the_path(self):
        lines = [
                 WorkflowLine(1, [], [],
                  CleanCall("0", "940", "940", "(tar)", "open", "1319227151896624-20", ["/home/user/bla1.rrd", "32961", "384"], "5")),
                 WorkflowLine(2, [], [], 
                  CleanCall("0", "940", "941", "(tar)", "stat", "1319227151896625-20", ["/home/user/bla1.rrd", "5"], "0")),
                 WorkflowLine(3, [], [], 
                  CleanCall("0", "940", "942", "(tar)", "write", "1319227151896626-20", ["/home/user/bla1.rrd", "5", "5120"], "5120")),
                 WorkflowLine(4, [], [], 
                  CleanCall("0", "940", "943", "(tar)", "read", "1319227151896627-20", ["/home/user/bla1.rrd", "5", "5120"], "5120")),
                 WorkflowLine(5, [], [], 
                  CleanCall("0", "940", "944", "(tar)", "close", "1319227151896628-20", ["5"], "0")),

                 WorkflowLine(6, [], [], 
                  CleanCall("0", "941", "945", "(tar)", "open", "1319227151896625-20", ["/home/user/bla1.rrd", "32961", "384"], "5")),
                 WorkflowLine(7, [], [], 
                  CleanCall("0", "941", "946", "(tar)", "stat", "1319227151896626-20", ["/home/user/bla1.rrd", "5"], "0")),
                 WorkflowLine(8, [], [], 
                  CleanCall("0", "941", "947", "(tar)", "write", "1319227151896627-20", ["/home/user/bla1.rrd", "5", "5120"], "5120")),
                 WorkflowLine(9, [], [], 
                  CleanCall("0", "941", "948", "(tar)", "read", "1319227151896628-20", ["/home/user/bla1.rrd", "5", "5120"], "5120")),
                 WorkflowLine(10, [], [], 
                  CleanCall("0", "941", "949", "(tar)", "close", "1319227151896629-20", ["5"], "0"))
                ]

        actual = sorted(weak_fs_dependency_sort(lines), key=lambda line: line._id)

        self.assertWLine(actual[0], 1, [], [2, 3], lines[0].clean_call)
        self.assertWLine(actual[1], 2, [1], [], lines[1].clean_call)
        self.assertWLine(actual[2], 3, [1], [4, 6], lines[2].clean_call)
        self.assertWLine(actual[3], 4, [3], [5], lines[3].clean_call)
        self.assertWLine(actual[4], 5, [4], [], lines[4].clean_call)
        self.assertWLine(actual[5], 6, [3], [7, 8], lines[5].clean_call)
        self.assertWLine(actual[6], 7, [6], [], lines[6].clean_call)
        self.assertWLine(actual[7], 8, [6], [9], lines[7].clean_call)
        self.assertWLine(actual[8], 9, [8], [10], lines[8].clean_call)
        self.assertWLine(actual[9], 10, [9], [], lines[9].clean_call)

    def test_open_locks_the_path_and_write_read_fstat_close_touch_the_fd(self):
        lines = [
                 WorkflowLine(1, [], [],
                  CleanCall("0", "940", "940", "(tar)", "open", "1319227151896624-20", ["/home/user/bla1.rrd", "32961", "384"], "5")),
                 WorkflowLine(2, [], [], 
                  CleanCall("0", "940", "941", "(tar)", "fstat", "1319227151896625-20", ["/home/user/bla1.rrd", "5"], "0")),
                 WorkflowLine(3, [], [], 
                  CleanCall("0", "940", "942", "(tar)", "write", "1319227151896626-20", ["/home/user/bla1.rrd", "5", "5120"], "5120")),
                 WorkflowLine(4, [], [], 
                  CleanCall("0", "940", "943", "(tar)", "read", "1319227151896627-20", ["/home/user/bla1.rrd", "5", "5120"], "5120")),
                 WorkflowLine(5, [], [], 
                  CleanCall("0", "940", "944", "(tar)", "close", "1319227151896628-20", ["5"], "0")),

                 WorkflowLine(6, [], [], 
                  CleanCall("0", "941", "945", "(tar)", "open", "1319227151896625-20", ["/home/user/bla1.rrd", "32961", "384"], "5")),
                 WorkflowLine(7, [], [], 
                  CleanCall("0", "941", "946", "(tar)", "fstat", "1319227151896626-20", ["/home/user/bla1.rrd", "5"], "0")),
                 WorkflowLine(8, [], [], 
                  CleanCall("0", "941", "947", "(tar)", "write", "1319227151896627-20", ["/home/user/bla1.rrd", "5", "5120"], "5120")),
                 WorkflowLine(9, [], [], 
                  CleanCall("0", "941", "948", "(tar)", "read", "1319227151896628-20", ["/home/user/bla1.rrd", "5", "5120"], "5120")),
                 WorkflowLine(10, [], [], 
                  CleanCall("0", "941", "949", "(tar)", "close", "1319227151896629-20", ["5"], "0"))
                ]

        actual = sorted(fs_dependency_order(lines), key=lambda line: line._id)

        self.assertWLine(actual[0], 1, [], [2, 3, 6], lines[0].clean_call)
        self.assertWLine(actual[1], 2, [1], [], lines[1].clean_call)
        self.assertWLine(actual[2], 3, [1], [4, 5], lines[2].clean_call)
        self.assertWLine(actual[3], 4, [3], [], lines[3].clean_call)
        self.assertWLine(actual[4], 5, [3], [], lines[4].clean_call)
        self.assertWLine(actual[5], 6, [1], [7, 8], lines[5].clean_call)
        self.assertWLine(actual[6], 7, [6], [], lines[6].clean_call)
        self.assertWLine(actual[7], 8, [6], [9, 10], lines[7].clean_call)
        self.assertWLine(actual[8], 9, [8], [], lines[8].clean_call)
        self.assertWLine(actual[9], 10, [8], [], lines[9].clean_call)


    def test_RRR_open_fstat_stat3x(self):
        lines = [
                 WorkflowLine(1, [], [2], CleanCall("0", "940", "940", "(tar)", "open", "1319227151896624-20", ["/home/user/bla1.rdd", "32961", "384"], "5")),
                 WorkflowLine(2, [1], [], CleanCall("0", "940", "940", "(tar)", "fstat", "1319227151896625-20", ["/home/user/bla1.rrd", "5"], "0")),#what is has a diff tid from open ?
                 WorkflowLine(3, [], [], CleanCall("65534", "1856", "1867", "(gmetad)", "stat", "1319227151896626-20", ["/home/user/bla1.rrd"], "0")),
                 WorkflowLine(4, [], [], CleanCall("65534", "1856", "1868", "(gmetad)", "stat", "1319227151896627-20", ["/home/user/bla1.rrd"], "0")),
                 WorkflowLine(5, [], [], CleanCall("65534", "1856", "1869", "(gmetad)", "stat", "1319227151896628-20", ["/home/user/bla1.rrd"], "0")),
                 WorkflowLine(6, [], [], CleanCall("65534", "1856", "1870", "(gmetad)", "stat", "1319227151896629-20", ["/home/user/bla1.rrd"], "0"))
                ]

        fs_dep_lines = fs_dependency_order(lines)
        fs_dep_lines = sorted(fs_dep_lines, key=lambda line: line._id)#sort by _id
	#all read type operations, all operations remains independent
        for (actual, expected) in zip(fs_dep_lines, lines):
            self.assertEquals(actual, expected)

    def test_RWW_stat_llssek_llseek(self):
        lines = [
                 WorkflowLine(1, [], [], 
                     CleanCall("65534", "1856", "1867", "(gmetad)", "stat", "1319227151896626-20", ["/home/user/bla1.rrd"], "0")),
                 WorkflowLine(2, [], [], 
                     CleanCall("0", "940", "940", "(tar)", "llseek", "1319227151896627-20", ["/home/user/bla1.rrd", "0", "4294967295", "4294967295", "SEEK_CUR"], "0")),
                 WorkflowLine(3, [], [], 
                     CleanCall("0", "940", "940", "(tar)", "llseek", "1319227151896628-20", ["/home/user/bla1.rrd", "0", "4294967295", "4294967295", "SEEK_CUR"], "0"))
                ]

        actual = sorted(fs_dependency_order(lines), key=lambda line: line._id)#sort by _id

        self.assertWLine(actual[0], 1, [], [], lines[0].clean_call)
        self.assertWLine(actual[1], 2, [], [3], lines[1].clean_call)
        self.assertWLine(actual[2], 3, [2], [], lines[2].clean_call)

    def test_WRR_rmdir_stat_stat(self):
        lines = [
                 WorkflowLine(1, [], [],
                     CleanCall("0", "960", "960", "(tar)", "rmdir", "1319227151896627-20", ["/home/user/bla1.rdd"], "0")),
                 WorkflowLine(2, [], [], 
                     CleanCall("0", "970", "970", "(tar)", "stat", "1319227151896628-20", ["/home/user/bla1.rdd"], "0")),
                 WorkflowLine(3, [], [], 
                     CleanCall("0", "980", "980", "(tar)", "stat", "1319227151896629-20", ["/home/user"], "0"))
                ]

        #rmdir get write lock both to object and its parent
        actual = sorted(fs_dependency_order(lines), key=lambda line: line._id)#sort by _id

        self.assertWLine(actual[0], 1, [], [2, 3], lines[0].clean_call)
        self.assertWLine(actual[1], 2, [1], [], lines[1].clean_call)
        self.assertWLine(actual[2], 3, [1], [], lines[2].clean_call)

    def test_RWR_stat_unlink_stat(self):
        lines = [
                 WorkflowLine(1, [], [], 
                     CleanCall("0", "950", "950", "(tar)", "stat", "1319227151896626-20", ["/home/user/bla1.rdd"], "0")),
                 WorkflowLine(2, [], [], 
                     CleanCall("0", "960", "960", "(tar)", "unlink", "1319227151896627-20", ["/home/user/bla1.rdd"], "0")),
                 WorkflowLine(3, [], [], 
                     CleanCall("0", "970", "970", "(tar)", "stat", "1319227151896628-20", ["/home/user/bla1.rdd"], "0")),
                 WorkflowLine(4, [], [], 
                     CleanCall("0", "980", "980", "(tar)", "stat", "1319227151896629-20", ["/home/user"], "0"))
                ]

        actual = sorted(fs_dependency_order(lines), key=lambda line: line._id)#sort by _id
        self.assertWLine(actual[0], 1, [], [], lines[0].clean_call)
        self.assertWLine(actual[1], 2, [], [3, 4], lines[1].clean_call)
        self.assertWLine(actual[2], 3, [2], [], lines[2].clean_call)
        self.assertWLine(actual[3], 4, [2], [], lines[3].clean_call)

    def test_fs_order_stat(self):
        #stat is a read type operation, so no changes
        lines = [
                 WorkflowLine(1, [], [3],
                     CleanCall("65534", "1856", "1867", "(gmetad)", "stat", "1319227151896626-113", ["/home/user/bla1.rrd"], "0")),
                 WorkflowLine(2, [], [4],
                     CleanCall("65534", "1856", "1868", "(gmetad)", "stat", "1319227151896626-114", ["/home/user/bla1.rrd"], "0")),
                 WorkflowLine(3, [1], [],
                     CleanCall("65534", "1856", "1867", "(gmetad)", "stat", "1319227151896626-115", ["/home/user/bla1.rrd"], "0")),
                 WorkflowLine(4, [2], [], 
                     CleanCall("65534", "1856", "1868", "(gmetad)", "stat", "1319227151896626-116", ["/home/user/bla1.rrd"], "0"))
                ]

        fs_dep_lines = fs_dependency_order(lines)
        fs_dep_lines = sorted(fs_dep_lines, key=lambda line: line._id)#sort by _id

        self.assertEquals(fs_dep_lines[0], lines[0])
        self.assertEquals(fs_dep_lines[1], lines[1])
        self.assertEquals(fs_dep_lines[2], lines[2])
        self.assertEquals(fs_dep_lines[3], lines[3])

    def test_fs_order_mkdir_and_stat(self):
        #mkdir is a write type operation, it blocks both parent and the new directory but I'll give from blocking parent
        lines = [
                 WorkflowLine(1, [], [],
                     CleanCall("65534", "1856", "1856", "(gmetad)", "mkdir", "1318615768915818-17", ["/home/user/__SummaryInfo__", "493"], "0")),
                 WorkflowLine(2, [], [],
                     CleanCall("65534", "1850", "1850", "(gmetad)", "stat", "1318615768915818-18", ["/home/user/"], "0")),
                 WorkflowLine(3, [], [],
                     CleanCall("65534", "1860", "1860", "(gmetad)", "stat", "1318615768915818-19", ["/home/user/__SummaryInfo__"], "0"))
                ]

        fs_dep_lines = fs_dependency_order(lines)
        fs_dep_lines = sorted(fs_dep_lines, key=lambda line: line._id)#sort by _id

        self.assertWLine(fs_dep_lines[0], 1, [], [3], lines[0].clean_call)
        self.assertWLine(fs_dep_lines[1], 2, [], [], lines[1].clean_call)
        self.assertWLine(fs_dep_lines[2], 3, [1], [], lines[2].clean_call)

    def assertLine(self, actual, expected):
        self.assertEquals(actual[0], expected[0])#id
        self.assertEquals(actual[1], expected[1])#n_parents
        self.assertEquals(set(actual[2]), set(expected[2]))#parents
        self.assertEquals(actual[3], expected[3])#n_children
        self.assertEquals(set(actual[4]), set(expected[4]))#children
        self.assertEquals(actual[5], expected[5])#CleanCall
        

    def test_fs_order_mkdir_and_stat_short_circuit(self):
        lines = [
                 WorkflowLine(1, [], [], 
                   CleanCall("65534", "1856", "1856", "(gmetad)", "mkdir", "1318615768915818-17", ["/home/user/d1", "493"], "0")),
                 WorkflowLine(2, [], [],
                   CleanCall("65534", "1856", "1857", "(gmetad)", "mkdir", "1318615768915818-18", ["/home/user/d1/d2", "493"], "0")),
                 WorkflowLine(3, [], [],
                   CleanCall("65534", "1856", "1858", "(gmetad)", "stat", "1318615768915818-19", ["/home/user/d1/d2"], "0")),
                 WorkflowLine(4, [], [], 
                   CleanCall("65534", "1856", "1859", "(gmetad)", "mkdir", "1318615768915818-20", ["/home/user/d1/d2/d3", "493"], "0"))
                ]

        fs_dep_lines = fs_dependency_order(lines)
        fs_dep_lines = sorted(fs_dep_lines, key=lambda line: line._id)#sort by _id

        #if 2 and 3 depends on 1, we set 1 -> 2 -> 3
        self.assertWLine(fs_dep_lines[0], 1, [], [2], lines[0].clean_call)
        self.assertWLine(fs_dep_lines[1], 2, [1], [3, 4], lines[1].clean_call)
        self.assertWLine(fs_dep_lines[2], 3, [2], [], lines[2].clean_call)
        self.assertWLine(fs_dep_lines[3], 4, [2], [], lines[3].clean_call)

    def test_order_open_read_close_short_circuit(self):
    #based on a replay bug (in fact, replay was expecting always single parents
        lines = [
                 CleanCall("1159", "2205", "9951", "(firefox-bin)", 
                           "open",
                           "1319204801598460-61446",
                           ["/home/thiagoepdc/.mozilla/firefox/tqcuxi3p.default/Cache/9/8E/3AE45d01", "32768", "0"], 
                           "69"),
                 CleanCall("1159", "2205", "2306", "(firefox-bin)",
                           "read",
                           "1319204805518105-21952",
                           ["/home/thiagoepdc/.mozilla/firefox/tqcuxi3p.default/Cache/9/8E/3AE45d01", "69", "4477"],
                           "4477"),
                 CleanCall("1159", "2205", "2306", "(firefox-bin)",
                           "close",
                           "1319204805540068-28",
                           ["69"],
                           "0")
              ]

        pidfid_order = sorted(order_by_pidfid(lines), key=lambda line: line._id)
        w_lines = sorted(fs_dependency_order(pidfid_order), key=lambda line: line._id)

        self.assertWLine(w_lines[0], 1, [], [2], lines[0])
        self.assertWLine(w_lines[1], 2, [1], [3], lines[1])
        self.assertWLine(w_lines[2], 3, [2], [], lines[2])

    def test_order_pid_tid(self):
        lines = [
                 CleanCall("65534", "1856", "1867", "(gmetad)", "stat", 
                           "1319227151896626-113",
                           ["/home/user/bla1.rrd"], 
                           "0"),
                 CleanCall("65534", "1856", "1868", "(gmetad)", "stat",
                           "1319227151896626-114",
                           ["/home/user/bla2.rrd"],
                           "0"),
                 CleanCall("65534", "1856", "1867", "(gmetad)", "stat",
                           "1319227151896626-115",
                           ["/home/user/bla3.rrd"],
                           "0"),
                 CleanCall("65534", "1856", "1868", "(gmetad)", "stat",
                           "1319227151896626-116",
                           ["/home/user/bla4.rrd"], 
                           "0")
                ]

        o_lines = order_by_pidfid(lines)
        self.assertEquals(len(o_lines), 4)

        w_lines = sorted(o_lines, key=lambda line: line._id)#sort by _id

        self.assertWLine(w_lines[0], 1, [], [3], lines[0])
        self.assertWLine(w_lines[1], 2, [], [4], lines[1])
        self.assertWLine(w_lines[2], 3, [1], [], lines[2])
        self.assertWLine(w_lines[3], 4, [2], [], lines[3])

    def test_creation_from_json(self):
        exp_id = 1
        exp_parents = []
        exp_children = [2, 50, 44]
        _json = {
                       "args": [
                                "/home/nathaniel/.config/google-chrome/Default", 
                                "32768", 
                                "0"
                               ], 
                       "call": "open", 
                       "caller": {
                                  "exec": "(chrome)", 
                                  "pid": "9822", 
                                  "tid": "9887", 
                                  "uid": "1057"
                                 }, 
                       "children": exp_children,
                       "id": exp_id, 
                       "parents": exp_parents, 
                       "rvalue": 146, 
                       "stamp": {
                                 "begin": 1319217009707385.0, 
                                 "elapsed": 277
                                 }
                }

        workflow = WorkflowLine.from_json(_json)
        self.assertWLine(workflow, exp_id, exp_parents, exp_children, 
                                  CleanCall("1057", "9822", "9887", "(chrome)",
                                            "open", "1319217009707385-277",
                                            ["/home/nathaniel/.config/google-chrome/Default", 
                                             "32768", "0"],
                                            "146"))

    def assertWLine(self, actual_wline, exp_id, exp_parents, exp_children, exp_clean_call):
        self.assertEquals(actual_wline.clean_call, exp_clean_call)
        self.assertEquals(actual_wline._id, exp_id)
        self.assertEquals(set(actual_wline.parents), set(exp_parents))
        self.assertEquals(set(actual_wline.children), set(exp_children))

if __name__ == "__main__":
    unittest.main()
