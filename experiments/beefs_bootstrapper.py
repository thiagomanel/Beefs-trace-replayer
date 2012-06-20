import os
import sys
import json
import uuid
import random

class Entry():
    class Replica():
        def __init__(self, version, osd_id, sto_id):
           self.version = version
           self.osd_id = osd_id
           self.sto_id = sto_id

        def __str__(self):
            return json.dumps(self.json())

        def json(self):
            return {
                    "version": self.version,
                    "osd_id": self.osd_id,
                    "sto_id": self.sto_id
                   }

        @classmethod
        def from_json(cls, _json):
            return Entry.Replica(_json["version"], _json["osd_id"], _json["sto_id"])

    def __init__(self, fullpath, ftype, replicas):
        if not ftype in ("f", "d"):
            raise ValueError("We allow f or d arg: %s", ftype)
        self.fullpath = fullpath
        self.ftype = ftype
        self.replicas = replicas

    def __str__(self):
        return json.dumps(self.json())

    def is_dir(self):
        return self.ftype is "d"

    def json(self):
        replicas_json = [rep.json() for rep in self.replicas]
        return {
                "fullpath": self.fullpath,
                "ftype": self.ftype,
                "replicas": replicas_json
               }

    @classmethod
    def from_json(cls, _json):
        replicas = [Entry.Replica.from_json(replica_json) 
                       for replica_json in _json["replicas"]]
        return Entry(_json["fullpath"], _json["ftype"], replicas)

def distribution(namespace_path, rlevel):
    """ It creates a beefs data distribution, sto location and replication info,
        given a path.
        We assume the following layout under namespace_path arg:
            namespace_path
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

    def dentry(fullpath):
        return Entry(fullpath, "d", [])

    def fentry(fullpath, gen, rlevel):
        if rlevel < 0:
            raise ValueError("rlevel should not be negative %d", rlevel)

        replicas = [Entry.Replica(1, osd_id, str(uuid.uuid4())) \
                        for osd_id in
                         gen.generate(fullpath, rlevel)]

        return Entry(fullpath, "f", replicas)

    class OsdGen():
        def __init__(self, base_dir):
            self.base_dir = base_dir
            self.ids = {}
            root, dirs, files = os.walk(base_dir).next()
            for _dir in dirs:
                self.ids[os.path.join(base_dir,_dir)] = str(uuid.uuid4())

        def generate(self, fullpath, rlevel):
            """ It creates rlevel osd_ids. First id stands for the primary
                replica, followed by secondary ids. Primary replicas under
                the same user directory share the same osd id. For example,
                any file with prefix /base_dir/user_dir will have primary 
                replicas on the same osd_id. Also, files under different 
                user directories must have primary replicas with different
                osd_ids.
                Generated osd_ids cannot contais duplicates.
            """
            def match_primary_osd(fullpath):
                for user_dir in self.ids.keys():
                    if fullpath.startswith(user_dir):
                        return self.ids[user_dir]
                return None

            if rlevel > len(self.ids.keys()):
                raise ValueError("rlevel is greater than amount \
                                      of available osds")
            gen_ids = []
            prim_id = match_primary_osd(fullpath)
            if prim_id:
                gen_ids.append(prim_id)
            else:
                raise ValueError("match not found for %s" % fullpath)

            possible_secs = list(self.ids.values())
            possible_secs.remove(prim_id)
            gen_ids.extend(random.sample(possible_secs, rlevel - 1))
            return gen_ids

    prim_osd_gen = OsdGen(namespace_path)

    graph = {}
    entry_by_path = {}
    for root, dirs, files in os.walk(namespace_path):
        if not root in entry_by_path:
            entry_by_path[root] = dentry(root)

        root_entry = entry_by_path[root]
        graph[root_entry] = []

        #FIXME remove this duplication
        for _dir in dirs:
            if _dir:
                fullpath = os.path.join(root, _dir)
                if not _dir in entry_by_path:
                    entry = dentry(fullpath)
                    entry_by_path[fullpath] = entry
                graph[root_entry].append(entry_by_path[fullpath])

        for _file in files:
            if _file:
                fullpath = os.path.join(root, _file)
                if not _file in entry_by_path:
                    entry = fentry(fullpath, prim_osd_gen, rlevel)
                    entry_by_path[fullpath] = entry
                graph[root_entry].append(entry_by_path[fullpath])
		
    return graph

if __name__ == "__main__":

    """ It creates a distribution based on a local path.
        
        Args:
            local_path (str): path to a directory to generate the distribution
            replication_level (str): rlevel used on distribution

        Returns:
            a json-like string representation of beefs distribution.
            {"fullpath": value, "ftype":value, 
                replicas: [{"version": value, "osd_id": value, "sto_id":value}]}
            Each distribution entry as above is a single-line string. 
            Entries are separated by \n

        Raises:
            ValueError, If there is not an acessible directory on local_path arg
                or replication_level is not a integer value.
    """

    local_path = sys.argv[1]
    rlevel = int(sys.argv[2])
    iso = "ISO-8859-1"

    for parent, children in distribution(local_path, rlevel).iteritems():
        #we take files from values and dirs from keys, to avoid duplicates
        if not parent.is_dir():
            raise Exception("Hey, keys should store directories")
        sys.stdout.write(json.dumps(parent.json(), encoding=iso) + "\n")

        for child in children:
            if not child.is_dir():
                sys.stdout.write(json.dumps(child.json(), encoding=iso) + "\n")
