import unittest
import tempfile
import shutil
import os
import json
from beefs_bootstrapper import *

class TestDistribution(unittest.TestCase):

    def setUp(self):
        self._on_teardown = []

    def test_load_from_json(self):
        _json = {"fullpath": "/local/backup_nfs_manel/tmp/thiagoepdc/testacp", 
                 "ftype": "d", 
                 "replicas": []
                }
        entry = Entry.from_json(_json)

        self.assertEquals("/local/backup_nfs_manel/tmp/thiagoepdc/testacp",
                          entry.fullpath)
        self.assertTrue(entry.is_dir())
        self.assertEquals(0, len(entry.replicas))

        _json = {"fullpath": "/local/backup_nfs_manel/tmp/thiagoepdc/file.data",
                 "ftype": "f", 
                 "replicas": []
                }
        entry = Entry.from_json(_json)

        self.assertEquals("/local/backup_nfs_manel/tmp/thiagoepdc/file.data",
                          entry.fullpath)
        self.assertFalse(entry.is_dir())
        self.assertEquals(0, len(entry.replicas))

    def test_load_from_json_with_weird_chars(self):
        json_str = open("beefs_bootstrapper_test.data").readline()
        _json = json.loads(json_str )
        entry = Entry.from_json(_json)
        #self.assertEquals(file_weird_chars, entry.fullpath)
        self.assertFalse(entry.is_dir())
        self.assertEquals(0, len(entry.replicas))
        print "fullpath", entry.fullpath

    def make_temp_dir(self):
        temp_dir = tempfile.mkdtemp(prefix="tmp-%s-" % self.__class__.__name__)
        def tear_down():
            shutil.rmtree(temp_dir)
        self._on_teardown.append(tear_down)
        return temp_dir

    def tearDown(self):
        for func in reversed(self._on_teardown):
            func()

    def entries_by_path(self, entries):
        by_path = {}
        for entry in entries:
            by_path[entry.fullpath] = entry
        return by_path

    def test_distribution_directories_and_files(self):

        #    base_dir
        #    |--- manel
        #    |     |--- empty_dir
        #    |     |--- non_empty
        #    |          |--- file
        #    |--- empty_user

        dirs = []
        temp_dir = self.make_temp_dir()
        manel_dir = os.path.join(temp_dir, "manel")
        dirs.append(manel_dir)
        empty_dir = os.path.join(manel_dir, "empty_dir")
        dirs.append(empty_dir)
        non_empty_dir = os.path.join(manel_dir, "non_empty_dir")
        dirs.append(non_empty_dir)
        empty_user_dir = os.path.join(temp_dir, "empty_user")
        dirs.append(empty_user_dir)
        for _dir in dirs:
            os.mkdir(_dir)

        afile = os.path.join(non_empty_dir, "file")
        open(afile, 'w').close()

        replication_level = 2
        entry_tree = distribution(temp_dir, replication_level)
        self.assertEquals(5, len(entry_tree.keys()))
        for entry in entry_tree.keys():
            print entry

        entries_by_path = self.entries_by_path(entry_tree.keys())
        for _dir in dirs:
            self.assertTrue(_dir in entries_by_path)
            entry = entries_by_path[_dir]
            self.assertTrue(entry.is_dir())
            self.assertFalse(entry.replicas)#empty evaluates to false

        #base_dir/manel subtree
        manel_entry = entries_by_path[manel_dir]
        manel_entry_children = self.entries_by_path(entry_tree[manel_entry])
        self.assertEquals(2, len(manel_entry_children.keys()))
        self.assertTrue(empty_dir in manel_entry_children)
        self.assertTrue(non_empty_dir in manel_entry_children)

        empty_dir_entry = manel_entry_children[empty_dir]
        self.assertTrue(empty_dir_entry.is_dir())
        empty_dir_entry_children = self.entries_by_path(
                                       entry_tree[empty_dir_entry])
        self.assertEquals(0, len(empty_dir_entry_children))

        non_empty_dir_entry = manel_entry_children[non_empty_dir]
        non_empty_dir_entry_children = self.entries_by_path(
                                           entry_tree[non_empty_dir_entry])
        self.assertEquals(1, len(non_empty_dir_entry_children))
        self.assertTrue(afile in non_empty_dir_entry_children)
        afile_entry = non_empty_dir_entry_children[afile]
        self.assertFalse(afile_entry.is_dir())
        self.assertEquals(replication_level, len(afile_entry.replicas))

        # base_dir/empty_user subtree
        empty_user_entry = entries_by_path[empty_user_dir]
        self.assertTrue(empty_user_entry.is_dir())
        empty_user_entry_children = self.entries_by_path(
                                             entry_tree[empty_user_entry])
        self.assertFalse(empty_user_entry_children)#empty evaluates to false

    def test_replica_distribution(self):
        temp_dir = self.make_temp_dir()
        num_dirs = 10
        dirs = [os.path.join(temp_dir, str(_dir)) for _dir in range(num_dirs)]

        files_per_dir = 10
        files = []
        for _dir in dirs:
            files.extend([os.path.join(_dir, str(_file)) 
                             for _file in range(files_per_dir)])
        for _dir in dirs:
            os.mkdir(_dir)
        for _file in files:
            open(_file, 'w').close()

        replication_level = 2
        entry_tree = distribution(temp_dir, replication_level)

        actual_osds = set()
        entries_by_path = self.entries_by_path(entry_tree.keys())

        for _dir in dirs:
            dir_entry = entries_by_path[_dir]
            dir_children_entries = entry_tree[dir_entry]
            self.assertEquals(files_per_dir, len(dir_children_entries))

            #we cannot repeat stos in a group. osd neither
            for entry in dir_children_entries:
                id_stos = [replica.sto_id for replica in entry.replicas]
                self.assertEquals(len(id_stos), len(set(id_stos)))

                id_osds = [replica.osd_id for replica in entry.replicas]
                self.assertEquals(len(id_osds), len(set(id_osds)))

            dir_children_primreplicas = [entry.replicas[0].osd_id
                                            for entry in dir_children_entries]

            for p_replica in dir_children_primreplicas:
                self.assertNotEquals(None, p_replica)

            #all primary replicas under the same user dir 
            #should be stored in the same osd
            self.assertEquals(files_per_dir, len(dir_children_primreplicas))
            self.assertEquals(1, len(set(dir_children_primreplicas)))

            #they are all equals, putting one of them
            actual_osds.add(dir_children_primreplicas[0])

        #we cannot repeat osds to diferent root subdirs
        self.assertEquals(num_dirs, len(actual_osds)) 

if __name__ == '__main__':
    unittest.main()
