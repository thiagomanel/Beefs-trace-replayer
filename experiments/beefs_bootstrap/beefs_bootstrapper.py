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
    # This classes create json-like string to be consumed by java code.
    # It its turn, java side has also code to reflect these data structures.
    # It'd be nice to keep them close
    class Group():
        def __init__(self, _id, rlevel, primary, replicas):
            self._id = _id
            self.rlevel = rlevel
            self.primary = primary
            self.replicas = replicas

        def __str__(self):
            return json.dumps(self.json())

        def json(self):
            return {
                    "id": self._id,
                    "replicationLevel": self.rlevel,
                    "primary": self.primary.json(),
                    "replicas": [rep.json() for rep in self.replicas]
                   }

        def allreplicas(self):
            _all = list(self.replicas)
            _all.append(self.primary)
            return _all

        def replicas_by_osdid(self):
            by_osdid = {}
            for rep in self.allreplicas():
                if not rep.osd_id in by_osdid:
                    by_osdid[rep.osd_id] = []
                by_osdid[rep.osd_id].append(rep)
            return by_osdid

        @classmethod
        def from_json(cls, _json):
            if _json:
                _primary = Entry.Replica.from_json(_json["primary"])
                _replicas = [Entry.Replica.from_json(rep)
                             for rep in _json["replicas"]]
                return Entry.Group(_json["id"], _json["replicationLevel"], _primary,
                                   _replicas)
            else:
                return None

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
                    "osdId": self.osd_id.json(),
                    "id": self.sto_id
                   }

        @classmethod
        def from_json(cls, _json):
            _osdId = Entry.OsdId.from_json(_json["osdId"])
            return Entry.Replica(_json["version"], _osdId, _json["id"])

    class OsdId():
        def __init__(self, hostname, port, data_port):
            self.hostname = hostname
            self.port = port
            self.data_port = data_port

        def __str__(self):
            return json.dumps(self.json())

        def json(self):
            return {
                    "hostname": self.hostname,
                    "port": self.port,
                    "dataPort": self.data_port
                   }

        def __eq__(self, other):
            return (isinstance(other, self.__class__) 
                        and self.__dict__ == other.__dict__)

        def __ne__(self, other):
            return not self.__eq__(other)

        def __hash__(self):
            return hash(self.hostname) ^ hash(self.port) ^ hash(self.data_port)

        #FIXME i guess if we use self.dict it will be much more simple, this from_json and json methods
        @classmethod
        def from_json(cls, _json):
            return Entry.OsdId(_json["hostname"], _json["port"], _json["dataPort"])

    def __init__(self, inode_id, parent_id, fullpath, ftype, size, group):

        if not ftype in ("f", "d"):
            raise ValueError("We allow f or d arg: %s", ftype)

        self.fullpath = fullpath
        self.ftype = ftype
        self.fileSize = size
        self.group = group
        self.inode_id = inode_id
        self.parent_id = parent_id

    def __str__(self):
        return json.dumps(self.json())

    def is_dir(self):
        return self.ftype == "d"

    def json(self):
        group_json = {}
        if self.group:
            group_json = self.group.json()
        return {
                "inodeId": self.inode_id,
                "parentId": self.parent_id,
                "path": self.fullpath,
                "type": self.ftype,
                "fileSize": self.fileSize,
                "group": group_json
               }

    @classmethod
    def from_json(cls, _json):
        if not "fileSize" in _json:
            size = 0
        else:
            size = _json["fileSize"]

        return Entry(_json["inodeId"], _json["parentId"], _json["path"],
                     _json["type"], size, 
                     Entry.Group.from_json(_json["group"]))

def generate_queenbee_metadata(boot_data_path, output_dir_path):
    """
       It generates queenbee metadata based on file representation of
       distribution function of this module. It creates queenbee database
       files under output_dir_path directory

       Args:
            boot_data_path (str) - Path to a text file. Each line of this file
                is a json-like representation to an Entry object
            output_dir_path (str) - path to a directory to store output data

       Raises: TODO
    """
    #boot_script = "/local/thiagoepdc/workspace_beefs/beefs-middleware-project/target/beefs/bin/bootstrap.sh"
    boot_script = "/media/sda4/manel/workspace_boot/beefs-middleware-project/target/beefs/bin/bootstrap.sh"
    print "queen to call", boot_data_path, output_dir_path
    print subprocess.check_call(["bash", boot_script,
                     "queenbee",
                     os.path.abspath(boot_data_path),
                     os.path.abspath(output_dir_path)])

def generate_data_servers_metadata(entries, outdir_path):
    """
        It generates data_servers metadata based on distribution function of 
        this module.

        Args:
           entries (list) - A list of Entry objects.
           outdir_path (str) - path to a directory to store output data

        FIXME: explain how raw_dir is defined
        Returns: TODO
        Raises:  TODO
    """
    def data_server_metadata(osd_id, stos_id, meta_outdir):

        def create_osd_boot_data(stos_id, filepath_to_write):
            with open(filepath_to_write, 'w') as boot_data:
                for sto in stos_id:
		    boot_data.write(sto + "\n")

        def call_osd_bootstrapper(input_path, output_dir_path):
            print "to_call", input_path, output_dir_path
            #boot_script = "/local/thiagoepdc/workspace_beefs/beefs-middleware-project/target/beefs/bin/bootstrap.sh"
            boot_script = "/media/sda4/manel/workspace_boot/beefs-middleware-project/target/beefs/bin/bootstrap.sh"

            print subprocess.check_call(["bash", boot_script,
                             "honeycomb",
                             os.path.abspath(input_path),
                             os.path.abspath(output_dir_path)])

        in_path = ".".join([osd_id.hostname, "osd.boot"])
        create_osd_boot_data(stos_id, in_path)
        call_osd_bootstrapper(in_path, meta_outdir)

    def groupby_osd(entries):
        group_by = {}
        for entry in entries:
            group = entry.group
            for osd_id, replicas in group.replicas_by_osdid().iteritems():
                if not osd_id in group_by:
                    group_by[osd_id] = []
                for replica in replicas:
                    group_by[osd_id].append(replica.sto_id)
        return group_by

    files = [entry for entry in entries if not entry.is_dir()]

    ds_metadata_root = "dataserver_metadata"
    if not os.path.exists(ds_metadata_root):
        os.mkdir(ds_metadata_root)

    for osd_id, stos_id in groupby_osd(files).iteritems():
        meta_outdir = os.path.join(ds_metadata_root, osd_id.hostname)
        if not os.path.exists(meta_outdir):
            os.mkdir(meta_outdir)
        data_server_metadata(osd_id, stos_id, meta_outdir)

class OsdGen():
    def __init__(self, base_dir, ignore):
        self.base_dir = base_dir
        self.ids = {}
        root, dirs, files = walk(base_dir, ignore).next()
        for _dir in dirs:
            self.ids[os.path.join(base_dir,_dir)] = str(uuid.uuid4())

    def osdId_by_user_path(self):
        return dict(self.ids)

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

def distribution(namespace_path, rlevel, osd_generator, ignore):
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
           osd_generator: It gives osdIds to replicas
           ignore (list): a list of subdirs to ignore

        Returns:
            dict. A graph representation coded as a dict of Entry objects. For
                  each file under namespace_path we an Entry object. If a file
                  is a dir, replicas is a empty collection on Entry object
    """

    def dentry(fullpath, parent_id):
        inode_id = str(uuid.uuid4())
        return Entry(inode_id, parent_id, fullpath, "d", None)

    def fentry(fullpath, gen, rlevel, parent_id):

        def new_replicas(rlevel, osd_id_gen):
            version = 1
            fake_port = 1111
            fake_data_port = 2222
            osdIds = [Entry.OsdId(hostname_uuid, fake_port, fake_data_port)
                      for hostname_uuid in gen.generate(fullpath, rlevel)]
            return [Entry.Replica(version, osd_id, str(uuid.uuid4())) \
                        for osd_id in osdIds]
         
        def new_group(rlevel, osd_id_gen):
            replicas = new_replicas(rlevel, osd_id_gen)
            group_id = str(uuid.uuid4())
            return Entry.Group(group_id, rlevel, replicas[0], replicas[1:])

        if rlevel < 0:
            raise ValueError("rlevel should not be negative %d", rlevel)

        inode_id = str(uuid.uuid4())
        return Entry(inode_id, parent_id, fullpath, "f", new_group(rlevel, gen))


    graph = {}
    entry_by_path = {}
    for root, dirs, files in walk(namespace_path, ignore):
        if not root in entry_by_path:
            entry_by_path[root] = dentry(root, None)

        root_entry = entry_by_path[root]
        parent_id = root_entry.inode_id
        graph[root_entry] = []

        #FIXME remove this duplication
        for _dir in dirs:
            if _dir:
                fullpath = os.path.join(root, _dir)
                if not _dir in entry_by_path:
                    entry = dentry(fullpath, parent_id)
                    entry_by_path[fullpath] = entry
                graph[root_entry].append(entry_by_path[fullpath])

        for _file in files:
            if _file:
                fullpath = os.path.join(root, _file)
                if not _file in entry_by_path:
                    entry = fentry(fullpath, osd_generator, rlevel, parent_id)
                    entry_by_path[fullpath] = entry
                graph[root_entry].append(entry_by_path[fullpath])
		
    return graph
