import unittest
from order_trace import *
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

    def test_open_locks_the_path_and_write_read_fstat_close_touch_the_fd(self):
        lines = [
                 [1, 0, [], 0, [], "0 940 940 (tar) open 1319227151896624-20 /home/user/bla1.rrd 32961 384 5"],
                 [2, 0, [], 0, [], "0 940 941 (tar) fstat 1319227151896625-20 /home/user/bla1.rrd 5 0"],
                 [3, 0, [], 0, [], "0 940 942 (tar) write 1319227151896626-20 /home/user/bla1.rrd 5 5120 5120"],
                 [4, 0, [], 0, [], "0 940 943 (tar) read 1319227151896627-20 /home/user/bla1.rrd 5 5120 5120"],
                 [5, 0, [], 0, [], "0 940 944 (tar) close 1319227151896628-20 5 0"],

                 [6, 0, [], 0, [], "0 941 945 (tar) open 1319227151896625-20 /home/user/bla1.rrd 32961 384 5"],
                 [7, 0, [], 0, [], "0 941 946 (tar) fstat 1319227151896626-20 /home/user/bla1.rrd 5 0"],
                 [8, 0, [], 0, [], "0 941 947 (tar) write 1319227151896627-20 /home/user/bla1.rrd 5 5120 5120"],
                 [9, 0, [], 0, [], "0 941 948 (tar) read 1319227151896628-20 /home/user/bla1.rrd 5 5120 5120"],
                 [10, 0, [], 0, [], "0 941 949 (tar) close 1319227151896629-20 5 0"],
                ]

        actual = sorted(fs_dependency_order(lines), key=lambda line: line[0])

        self.assertLine(actual[0],
                        [1, 0, [], 3, [2, 3, 6], "0 940 940 (tar) open 1319227151896624-20 /home/user/bla1.rrd 32961 384 5"])
        self.assertLine(actual[1],
                        [2, 1, [1], 0, [], "0 940 941 (tar) fstat 1319227151896625-20 /home/user/bla1.rrd 5 0"])
        self.assertLine(actual[2],
                        [3, 1, [1], 2, [4, 5], "0 940 942 (tar) write 1319227151896626-20 /home/user/bla1.rrd 5 5120 5120"])
        self.assertLine(actual[3],
                        [4, 1, [3], 0, [], "0 940 943 (tar) read 1319227151896627-20 /home/user/bla1.rrd 5 5120 5120"])
        self.assertLine(actual[4],
                        [5, 1, [3], 0, [], "0 940 944 (tar) close 1319227151896628-20 5 0"])


        self.assertLine(actual[5],
                 [6, 1, [1], 2, [7, 8], "0 941 945 (tar) open 1319227151896625-20 /home/user/bla1.rrd 32961 384 5"])
        self.assertLine(actual[6],
                 [7, 1, [6], 0, [], "0 941 946 (tar) fstat 1319227151896626-20 /home/user/bla1.rrd 5 0"])
        self.assertLine(actual[7],
                 [8, 1, [6], 2, [9, 10], "0 941 947 (tar) write 1319227151896627-20 /home/user/bla1.rrd 5 5120 5120"])
        self.assertLine(actual[8],
                 [9, 1, [8], 0, [], "0 941 948 (tar) read 1319227151896628-20 /home/user/bla1.rrd 5 5120 5120"])
        self.assertLine(actual[9],
                 [10, 1, [8], 0, [], "0 941 949 (tar) close 1319227151896629-20 5 0"])

    def test_RRR_open_fstat_stat3x(self):
        lines = [
                 [1, 0, [], 1, [2], "0 940 940 (tar) open 1319227151896624-20 /home/user/bla1.rdd 32961 384 5"],
                 [2, 1, [1], 0, [], "0 940 940 (tar) fstat 1319227151896625-20 /home/user/bla1.rrd 5 0"],#what is has a diff tid from open ?
                 [3, 0, [], 0, [], "65534 1856 1867 (gmetad) stat 1319227151896626-20 /home/user/bla1.rrd 0"],
                 [4, 0, [], 0, [], "65534 1856 1868 (gmetad) stat 1319227151896627-20 /home/user/bla1.rrd 0"],
                 [5, 0, [], 0, [], "65534 1856 1869 (gmetad) stat 1319227151896628-20 /home/user/bla1.rrd 0"],
                 [6, 0, [], 0, [], "65534 1856 1870 (gmetad) stat 1319227151896629-20 /home/user/bla1.rrd 0"],
                ]

        fs_dep_lines = fs_dependency_order(lines)
        fs_dep_lines = sorted(fs_dep_lines, key=lambda line: line[0])#sort by _id
	#all read type operations, all operations remains independent
        for (actual, expected) in zip(fs_dep_lines, lines):
            self.assertLine(actual, expected)

    def test_RWW_stat_llssek_llseek(self):
        lines = [
                 [1, 0, [], 0, [], "65534 1856 1867 (gmetad) stat 1319227151896626-20 /home/user/bla1.rrd 0"],
                 [2, 0, [], 0, [], "0 940 940 (tar) llseek 1319227151896627-20 /home/user/bla1.rrd 0 SEEK_CUR 0"],
                 [3, 0, [], 0, [], "0 950 950 (tar) llseek 1319227151896628-20 /home/user/bla1.rrd 0 SEEK_CUR 0"],
                ]

        actual = sorted(fs_dependency_order(lines), key=lambda line: line[0])#sort by _id

        self.assertLine(actual[0], lines[0])
        self.assertLine(actual[1], 
                        [2, 0, [], 1, [3], "0 940 940 (tar) llseek 1319227151896627-20 /home/user/bla1.rrd 0 SEEK_CUR 0"])
        self.assertLine(actual[2],
                        [3, 1, [2], 0, [], "0 950 950 (tar) llseek 1319227151896628-20 /home/user/bla1.rrd 0 SEEK_CUR 0"])

    def test_WRR_rmdir_stat_stat(self):
        lines = [
                 [1, 0, [], 0, [], "0 960 960 (tar) rmdir 1319227151896627-20 /home/user/bla1.rdd 0"],
                 [2, 0, [], 0, [], "0 970 970 (tar) stat 1319227151896628-20 /home/user/bla1.rdd 0"],
                 [3, 0, [], 0, [], "0 980 980 (tar) stat 1319227151896629-20 /home/user 0"],
                ]

        #rmdir get write lock both to object and its parent
        actual = sorted(fs_dependency_order(lines), key=lambda line: line[0])#sort by _id

        self.assertLine(actual[0],
                        [1, 0, [], 2, [2, 3], "0 960 960 (tar) rmdir 1319227151896627-20 /home/user/bla1.rdd 0"])
        self.assertLine(actual[1],
                        [2, 1, [1], 0, [], "0 970 970 (tar) stat 1319227151896628-20 /home/user/bla1.rdd 0"])
        self.assertLine(actual[2],
                        [3, 1, [1], 0, [], "0 980 980 (tar) stat 1319227151896629-20 /home/user 0"])

    def test_RWR_stat_unlink_stat(self):
        lines = [
                 [1, 0, [], 0, [], "0 950 950 (tar) stat 1319227151896626-20 /home/user/bla1.rdd 0"],
                 [2, 0, [], 0, [], "0 960 960 (tar) unlink 1319227151896627-20 /home/user/bla1.rdd 0"],
                 [3, 0, [], 0, [], "0 970 970 (tar) stat 1319227151896628-20 /home/user/bla1.rdd 0"],
                 [4, 0, [], 0, [], "0 980 980 (tar) stat 1319227151896629-20 /home/user 0"],
                ]

        actual = sorted(fs_dependency_order(lines), key=lambda line: line[0])#sort by _id
        self.assertLine(actual[0],
                        [1, 0, [], 0, [], "0 950 950 (tar) stat 1319227151896626-20 /home/user/bla1.rdd 0"])
        self.assertLine(actual[1],
                        [2, 0, [], 2, [3, 4], "0 960 960 (tar) unlink 1319227151896627-20 /home/user/bla1.rdd 0"])
        self.assertLine(actual[2],
                        [3, 1, [2], 0, [], "0 970 970 (tar) stat 1319227151896628-20 /home/user/bla1.rdd 0"])
        self.assertLine(actual[3],
                        [4, 1, [2], 0, [], "0 980 980 (tar) stat 1319227151896629-20 /home/user 0"])

    def test_fs_order_stat(self):
        #stat is a read type operation, so no changes
        lines = [
                 [1, 0, [], 1, [3], "65534 1856 1867 (gmetad) stat 1319227151896626-113 /home/user/bla1.rrd 0"],
                 [2, 0, [], 1, [4], "65534 1856 1868 (gmetad) stat 1319227151896626-114 /home/user/bla1.rrd 0"],
                 [3, 1, [1], 0, [], "65534 1856 1867 (gmetad) stat 1319227151896626-115 /home/user/bla1.rrd 0"],
                 [4, 1, [2], 0, [], "65534 1856 1868 (gmetad) stat 1319227151896626-116 /home/user/bla1.rrd 0"],
                ]

        fs_dep_lines = fs_dependency_order(lines)
        fs_dep_lines = sorted(fs_dep_lines, key=lambda line: line[0])#sort by _id

        self.assertEquals(fs_dep_lines[0], lines[0])
        self.assertEquals(fs_dep_lines[1], lines[1])
        self.assertEquals(fs_dep_lines[2], lines[2])
        self.assertEquals(fs_dep_lines[3], lines[3])

    def test_fs_order_mkdir_and_stat(self):
        #mkdir is a write type operation, it blocks both parent and the new directory but I'll give from blocking parent
        lines = [
                 [1, 0, [], 0, [], "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /home/user/__SummaryInfo__ 493 0"],
                 [2, 0, [], 0, [], "65534 1850 1850 (gmetad) stat 1318615768915818-18 /home/user/ 0"],
                 [3, 0, [], 0, [], "65534 1860 1860 (gmetad) stat 1318615768915818-19 /home/user/__SummaryInfo__ 0"],
                ]

        fs_dep_lines = fs_dependency_order(lines)
        fs_dep_lines = sorted(fs_dep_lines, key=lambda line: line[0])#sort by _id

        self.assertEquals(fs_dep_lines[0],
                          [1, 0, [], 1, [3], "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /home/user/__SummaryInfo__ 493 0"])
        self.assertEquals(fs_dep_lines[1],
                          [2, 0, [], 0, [], "65534 1850 1850 (gmetad) stat 1318615768915818-18 /home/user/ 0"])
        self.assertEquals(fs_dep_lines[2],
                          [3, 1, [1], 0, [], "65534 1860 1860 (gmetad) stat 1318615768915818-19 /home/user/__SummaryInfo__ 0"])

    def assertLine(self, actual, expected):
        self.assertEquals(actual[0], expected[0])#id
        self.assertEquals(actual[1], expected[1])#n_parents
        self.assertEquals(set(actual[2]), set(expected[2]))#parents
        self.assertEquals(actual[3], expected[3])#n_children
        self.assertEquals(set(actual[4]), set(expected[4]))#children
        self.assertEquals(actual[5], expected[5])#sycall
        

    def test_fs_order_mkdir_and_stat_short_circuit(self):
        lines = [
                 [1, 0, [], 0, [], "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /home/user/d1 493 0"],
                 [2, 0, [], 0, [], "65534 1856 1857 (gmetad) mkdir 1318615768915818-18 /home/user/d1/d2 493 0"],
                 [3, 0, [], 0, [], "65534 1856 1858 (gmetad) stat 1318615768915818-19 /home/user/d1/d2 0"],
                 [4, 0, [], 0, [], "65534 1856 1859 (gmetad) mkdir 1318615768915818-20 /home/user/d1/d2/d3 493 0"],
                ]

        fs_dep_lines = fs_dependency_order(lines)
        fs_dep_lines = sorted(fs_dep_lines, key=lambda line: line[0])#sort by _id

        #if 2 and 3 depends on 1, we set 1 -> 2 -> 3
        self.assertLine(fs_dep_lines[0],
                          [1, 0, [], 1, [2], "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /home/user/d1 493 0"])
        self.assertLine(fs_dep_lines[1],
                      [2, 1, [1], 2, [3, 4], "65534 1856 1857 (gmetad) mkdir 1318615768915818-18 /home/user/d1/d2 493 0"])
        self.assertLine(fs_dep_lines[2],
                          [3, 1, [2], 0, [], "65534 1856 1858 (gmetad) stat 1318615768915818-19 /home/user/d1/d2 0"])
        self.assertLine(fs_dep_lines[3],
                          [4, 1, [2], 0, [], "65534 1856 1859 (gmetad) mkdir 1318615768915818-20 /home/user/d1/d2/d3 493 0"])

    def test_order_pid_tid(self):
        lines = [
                 "65534 1856 1867 (gmetad) stat 1319227151896626-113 /home/user/bla1.rrd 0",
                 "65534 1856 1868 (gmetad) stat 1319227151896626-114 /home/user/bla2.rrd 0",
                 "65534 1856 1867 (gmetad) stat 1319227151896626-115 /home/user/bla3.rrd 0",
                 "65534 1856 1868 (gmetad) stat 1319227151896626-116 /home/user/bla4.rrd 0",
                ]

        o_lines = order_by_pidfid(lines)
        self.assertEquals(len(o_lines), 4)

        all_lines = sorted(o_lines, key=lambda line: line[0])#sort by _id

        (_id, n_parents, parents, n_children, children, line) = all_lines[0]
        self.assertEquals(line, lines[0])
        self.assertEquals(_id, 1)
        self.assertEquals(n_parents, 0)
        self.assertEquals(parents, [])
        self.assertEquals(n_children, 1)
        self.assertEquals(children, [3])

        (_id, n_parents, parents, n_children, children, line) = all_lines[1]
        self.assertEquals(line, lines[1])
        self.assertEquals(_id, 2)
        self.assertEquals(n_parents, 0)
        self.assertEquals(parents, [])
        self.assertEquals(n_children, 1)
        self.assertEquals(children, [4])

        (_id, n_parents, parents, n_children, children, line) = all_lines[2]
        self.assertEquals(line, lines[2])
        self.assertEquals(_id, 3)
        self.assertEquals(n_parents, 1)
        self.assertEquals(parents, [1])
        self.assertEquals(n_children, 0)
        self.assertEquals(children, [])

        (_id, n_parents, parents, n_children, children, line) = all_lines[3]
        self.assertEquals(line, lines[3])
        self.assertEquals(_id, 4)
        self.assertEquals(n_parents, 1)
        self.assertEquals(parents, [2])
        self.assertEquals(n_children, 0)
        self.assertEquals(children, [])

if __name__ == "__main__":
    unittest.main()
