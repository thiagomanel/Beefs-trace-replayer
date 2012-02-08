import unittest
from order_trace import *
from itertools import chain

class TestOrderTrace(unittest.TestCase):

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

    def test_fs_order_mkdir_and_stat_short_circuit(self):
        lines = [
                 [1, 0, [], 0, [], "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /home/user/d1 493 0"],
                 [2, 0, [], 0, [], "65534 1856 1857 (gmetad) mkdir 1318615768915818-18 /home/user/d1/d2 493 0"],
                 [3, 0, [], 0, [], "65534 1856 1858 (gmetad) mkdir 1318615768915818-19 /home/user/d1/d2/d3 493 0"],
                 [4, 0, [], 0, [], "65534 1856 1859 (gmetad) mkdir 1318615768915818-20 /home/user/d1/d2/d3/d4 493 0"],
                ]

        fs_dep_lines = fs_dependency_order(lines)
        fs_dep_lines = sorted(fs_dep_lines, key=lambda line: line[0])#sort by _id

        #if 2 and 3 depends on 1, we set 1 -> 2 -> 3
        self.assertEquals(fs_dep_lines[0],
                          [1, 0, [], 1, [2], "65534 1856 1856 (gmetad) mkdir 1318615768915818-17 /home/user/d1 493 0"])
        self.assertEquals(fs_dep_lines[1],
                          [2, 1, [1], 1, [3], "65534 1856 1857 (gmetad) mkdir 1318615768915818-18 /home/user/d1/d2 493 0"])
        self.assertEquals(fs_dep_lines[2],
                          [3, 1, [2], 1, [4], "65534 1860 1858 (gmetad) stat 1318615768915818-19 /home/user/d1/d2 0"])
        self.assertEquals(fs_dep_lines[2],
                          [4, 1, [3], 0, [], "65534 1860 1859 (gmetad) mkdir 1318615768915818-20 /home/user/d1/d2/d3 493 0"])

    def test_order_pid_tid(self):
        lines = [
                 "65534 1856 1867 (gmetad) stat 1319227151896626-113 /home/user/bla1.rrd 0",
                 "65534 1856 1868 (gmetad) stat 1319227151896626-114 /home/user/bla2.rrd 0",
                 "65534 1856 1867 (gmetad) stat 1319227151896626-115 /home/user/bla3.rrd 0",
                 "65534 1856 1868 (gmetad) stat 1319227151896626-116 /home/user/bla4.rrd 0",
                ]

        o_lines = order_by_pidfid(lines)
	first_tid = o_lines.next()
	second_tid = o_lines.next()

        self.assertEquals(len(first_tid), 2)
        self.assertEquals(len(second_tid), 2)

        all_lines = list(chain(first_tid, second_tid))
        all_lines = sorted(all_lines, key=lambda line: line[0])#sort by _id

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
