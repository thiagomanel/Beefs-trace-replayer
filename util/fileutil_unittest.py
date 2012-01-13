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
        self.assertEqual(mode, access_modes.O_RDONLY)

    def test_acceptance_mode_33281(self):
        #O_WRONLY|O_TRUNC|O_LARGEFILE=33281
        mode = access_mode(33281)
        self.assertEqual(mode, access_modes.O_WRONLY)

# Linux reserves the special, nonstandard access mode 3 (binary 11) in flags to
# mean: check for read and write permission on the file and return a descriptor
# that can't be used for reading or writing. This nonstandard access mode is
# used by some Linux drivers to return a descriptor that is only to be used for
# device-specific ioctl(2) operations.
    def test_acceptance_mode_33283_is_None(self):
        mode = access_mode(33283)
        self.assertEqual(mode, None)

    def assertSequenceEqual(self, it1, it2):
        #python 2.7 has new def assertSequenceEqual(self, it1, it2) but i'm with 2.6
        self.assertEqual(tuple(it1), tuple(it2))

if __name__ == '__main__':
    unittest.main()
