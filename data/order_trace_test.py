import unittest
from order_trace import *

class TestOrderTrace(unittest.TestCase):

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

        (_id, n_parents, parents, n_children, children, line) = first_tid[0]
        self.assertEquals(line, lines[0])
        self.assertEquals(_id, 1)
        self.assertEquals(n_parents, 0)
        self.assertEquals(parents, [])
        self.assertEquals(n_children, 1)
        self.assertEquals(children, [3])

        (_id, n_parents, parents, n_children, children, line) = second_tid[0]
        self.assertEquals(line, lines[1])
        self.assertEquals(_id, 2)
        self.assertEquals(n_parents, 0)
        self.assertEquals(parents, [])
        self.assertEquals(n_children, 1)
        self.assertEquals(children, [4])

        (_id, n_parents, parents, n_children, children, line) = first_tid[1]
        self.assertEquals(line, lines[2])
        self.assertEquals(_id, 3)
        self.assertEquals(n_parents, 1)
        self.assertEquals(parents, [1])
        self.assertEquals(n_children, 0)
        self.assertEquals(children, [])

        (_id, n_parents, parents, n_children, children, line) = second_tid[3]
        self.assertEquals(line, lines[3])
        self.assertEquals(_id, 4)
        self.assertEquals(n_parents, 1)
        self.assertEquals(parents, [2])
        self.assertEquals(n_children, 0)
        self.assertEquals(children, [])

if __name__ == "__main__":
    unittest.main()
