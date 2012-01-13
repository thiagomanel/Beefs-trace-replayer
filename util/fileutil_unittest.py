import unittest
from enum import Enum
from fileutil import access_mode
from fileutil import creation_flags
from fileutil import ACCESS_MODES
from fileutil import CREATION_FLAGS

class TestFileUtil(unittest.TestCase):

    """ an acceptance test """
    def test_access_mode_34816(self):
	#(O_RDONLY|O_NONBLOCK|O_LARGEFILE)=34816
        mode = access_mode(34816)
        self.assertEqual(mode, ACCESS_MODES.O_RDONLY)

    def test_creation_flags_34816(self):
	#(O_RDONLY|O_NONBLOCK|O_LARGEFILE)=34816
        c_flags = creation_flags(33816)
	#order is not important
        self.assertSequenceEqual(c_flags, [CREATION_FLAGS.O_TRUNC])

    def test_access_mode_33281(self):
        #O_WRONLY|O_TRUNC|O_LARGEFILE=33281
        mode = access_mode(33281)
        self.assertEqual(mode, ACCESS_MODES.O_WRONLY)

    def test_creation_flags_CREAT_and_TRUNC(self):
        #O_RDONLY|O_CREAT|O_TRUNC=576=0x240
        c_flags = creation_flags(576)
        self.assertSequenceEqual(c_flags, [CREATION_FLAGS.O_TRUNC,
                                              CREATION_FLAGS.O_CREAT])
        self.assertSequenceEqual(c_flags, [CREATION_FLAGS.O_CREAT, 
                                              CREATION_FLAGS.O_TRUNC])
        

    def test_creation_flags_33281(self):
        c_flags = creation_flags(33281)
        self.assertSequenceEqual(c_flags, [CREATION_FLAGS.O_TRUNC])

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
