import os
import sys
import json
import uuid
import random
import subprocess
from itertools import groupby

def walk(top_dir, ignore):
    for dirpath, dirnames, filenames in os.walk(top_dir):
        dirnames[:] = [
            dn for dn in dirnames if os.path.join(dirpath, dn) not in ignore]
        yield dirpath, dirnames, filenames

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
        return self.ftype == "d"

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

def generate_beefs_metadata(entries, outdir_path):
    """
        It generates beefs metadata based on distribution function of this
        module.

        Args:
           entries (list) - A list of Entry objects.
           outdir_path (str) - path to a directory to store output data

        FIXME: explain how raw_dir is defined
        Returns: TODO
        Raises:  TODO
    """

    def generate_data_servers_metadata(raw_dir, osd_id, stos_id, meta_outdir):
        """
           Args:
              raw_dir (str) - 
              osd_id (str) -
              stos_id (str) -
              meta_outdir (str) - 
        """

        def create_osd_boot_data(raw_dir, osd_id, stos_id, filepath_to_write):
            #osd boot_data format
            #stoId	osdId	stoDataPath
            with open(filepath_to_write, 'w') as boot_data:
                for sto in stos_id:
                    boot_data.write("\t".join([sto, osd_id, raw_dir]) + "\n")

        def call_osd_bootstrapper(input_path, output_dir_path):
            print "to_call", input_path, output_dir_path
            boot_script = "/local/thiagoepdc/workspace_beefs/beefs-middleware-project/target/beefs/bin/bootstrap.sh"

            subprocess.call(["bash", boot_script,
                             "honeycomb",
                             input_path,
                             output_dir_path])

        in_path = ".".join([osd_id,"osd.boot"])
        create_osd_boot_data(raw_dir, osd_id, stos_id, in_path)
        call_osd_bootstrapper(in_path, meta_outdir)

    def groupby_osd(entries):
        group = {}
        for entry in entries:
            for replica in entry.replicas:
                osd_id = replica.osd_id
                sto_id = replica.sto_id
                if not osd_id in group:
                    group[osd_id] = []
                group[osd_id].append(sto_id)
        return group

    files = [entry for entry in entries if not entry.is_dir()]

    ds_metadata_root = "dataserver_metadata"
    if not os.path.exists(ds_metadata_root):
        os.mkdir(ds_metadata_root)

    for osd_id, stos_id in groupby_osd(files).iteritems():
        osd_rawdir = os.path.join(outdir_path, osd_id)
        meta_outdir = os.path.join(ds_metadata_root, osd_id)
        if not os.path.exists(meta_outdir):
            os.mkdir(meta_outdir)
        generate_data_servers_metadata(osd_rawdir, osd_id, stos_id, meta_outdir)

def distribution(namespace_path, rlevel, ignore):
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
           ignore (list): a list of subdirs to ignore

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
        def __init__(self, base_dir, ignore):
            self.base_dir = base_dir
            self.ids = {}
            root, dirs, files = walk(base_dir, ignore).next()
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

    prim_osd_gen = OsdGen(namespace_path, ignore)

    graph = {}
    entry_by_path = {}
    for root, dirs, files in walk(namespace_path, ignore):
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
