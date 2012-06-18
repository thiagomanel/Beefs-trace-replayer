class Entry():
    class Replica():
        def __init__(self, version, osd_id, sto_id):
           self.version = version
           self.osd_id = osd_id
           self.sto_id = sto_id

    def __init__(self, fullpath, ftype, replicas):
        self.fullpath = fullpath
        self.ftype = ftype
        self.replicas = replicas

    def is_dir(self):
        return self.ftype is "f"

def distribution(namespace_path, rlevel):
    """ It creates a beefs data distribution, sto location and replication info,
        given a path.
        We assume the following layout under namespace_path arg:
            namespace_path
            |--- home
                 |--- user1
                 |--- user2
                 |--- ...
                 |--- userN
        Under user directories we assume arbitrary layout.

        Args:
           namespace_path (str): path used to generate the distribution
           rlevel (int): number of replica of each data

        Returns:
            dict. A graph representation coded as a dict of Entry objects. For
                  each file under namespace_path we an Entry object. If a file
                  is a dir, replicas is a empty collection on Entry object
    """
