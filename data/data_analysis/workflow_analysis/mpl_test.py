import unittest
from mpl import *

class TestMPL(unittest.TestCase):

    def testMPL(self):
        begin = True
        r_tuples = [
                    (0, begin, 0),
                    (1, begin, 1),
                    (2, begin, 2),
                    (2, not begin, 3),
                    (0, not begin, 4),
                    (1, not begin, 5)
                    ]

        self.assertEquals(mpl(r_tuples), 3)

    def parse_replay_output(self):
        r_begin, r_end = requests_from_trace_output(1, "1364504782 931917\
                                                    1364504782 931918 0.000000\
                                                    -666 -666")

        self.assertEquals(r_begin, (1, mpl.__BEGIN__,       1364504782931917))
        self.assertEquals(r_begin, (1, not mpl.__BEGIN__,   1364504782931918))

#1364504782 932503 1364504782 932508 0.000000 18 16
#1364504782 932726 1364504782 932728 0.000000 0 0
#1364504782 932471 1364504782 932479 0.000000 23 -1
#1364504782 932645 1364504782 932646 0.000000 0 -1
#1364504782 932735 1364504782 932740 0.000000 18 4
#1364504782 932915 1364504782 932917 0.000000 0 0
#1364504782 932454 1364504782 932461 0.000000 43 15
#1364504782 932699 1364504782 932701 0.000000 0 0
#1364504782 932706 1364504782 932708 0.000000 0 0
if __name__ == '__main__':
    unittest.main()
