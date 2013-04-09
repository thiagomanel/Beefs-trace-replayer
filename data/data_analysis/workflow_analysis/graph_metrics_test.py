import unittest
from graph_metrics import *

class TestLongestPath(unittest.TestCase):

    def testLongestPath(self):
        graph = {
                    0: [1,2],
                    1: [],
                    2: []
        }
        self.assertEquals(longest_path_size(graph, 0), 1)
        self.assertEquals(i_longest_path_size(graph, 0), 1)

        graph = {
                    0: [1,2],
                    1: [],
                    2: [3],
                    3: []
        }
        self.assertEquals(longest_path_size(graph, 0), 2)
        self.assertEquals(i_longest_path_size(graph, 0), 2)

    def test_longest_path_size_is_zero_in_a_root_only_graph(self):
        graph = {
                    0: []
        }
        self.assertEquals(longest_path_size(graph, 0), 0)
        self.assertEquals(i_longest_path_size(graph, 0), 0)


if __name__ == '__main__':
    unittest.main()
