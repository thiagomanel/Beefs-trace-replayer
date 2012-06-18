import unittest
from beefs_bootstrapper import *

class TestDistribution(unittest.TestCase):

    def setUp(self):
        self._on_teardown = []

    def make_temp_dir(self):
        temp_dir = tempfile.mkdtemp(prefix="tmp-%s-" % self.__class__.__name__)
        def tear_down():
            shutil.rmtree(temp_dir)
        self._on_teardown.append(tear_down)
        return temp_dir

    def tearDown(self):
        for func in reversed(self._on_teardown):
            func()

    def test_distribution_directories_and_files(self):

        #    base_dir
        #    |---home
        #        |--- manel
        #             |--- empty_dir
        #             |--- non_empty
        #                  |--- file
        #        |--- empty_user

        dirs = []
        temp_dir = make_temp_dir()
	home_dir = os.path.join(temp_dir, "home")
        dirs.append(home_dir)
        manel_dir = os.path.join(home_dir, "manel")
        dirs.append(manel_dir)
        empty_dir = os.path.join(manel_dir, "empty_dir")
        dirs.append(empty_dir)
        non_empty_dir = os.path.join(manel_dir, "non_empty_dir")
        dirs.append(non_empty_dir)
        afile = os.path.join(non_empty_dir, "file")
        open(afile, 'w').close()
        empty_user_dir = os.path.join(home_dir, "empty_user")
        dirs.append(empty_user_dir)

        for _dir in dirs:
            os.mkdir(_dir):

        dist_tree = distribution(temp_dir, 2)
        for _dir in dirs:
            self.assertTrue(_dir in dist_tree))


if __name__ == '__main__':
    unittest.main()
