import unittest
from enum import Enum
from fileutil import access_mode
from fileutil import access_modes

class TestFileUtil(unittest.TestCase):

    """ an acceptance test """
    def test_acceptance_access_mode_34816(self):
	#we need an explanation about 34816 meaning
        mode = access_mode(34816)
	
	#order is not important
        self.assertSequenceEqual(mode, [access_modes.O_RDONLY])

#    def test_acceptance_mode_438(self):
#        modes = from_penmode(438)
#        self.assertSequenceEqual(modes, [open_modes.O_RDONLY])

    def assertSequenceEqual(self, it1, it2):
        #python 2.7 has new def assertSequenceEqual(self, it1, it2) but i'm with 2.6
        self.assertEqual(tuple(it1), tuple(it2))

if __name__ == '__main__':
    unittest.main()
