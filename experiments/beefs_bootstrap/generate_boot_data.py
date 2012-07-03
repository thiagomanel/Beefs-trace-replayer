import os
from itertools import groupby
from beefs_bootstrapper import *

if __name__ == "__main__":

    """ It creates a distribution based on a local path.
        
        Args:
            local_path (str): path to a directory to generate the distribution.
            replication_level (str): rlevel used on distribution.
            osd_mapping_output (str): local_path/user_dir mapping to primary
                osdId used on this distribution will be written on this path.
            *ignore_dirs (str): an arbitrary lenght, empty space sep, str args. 
                                These directories will be ignored. 

        Returns:
            a json-like string representation of beefs distribution.
            {"fullpath": value, "ftype":value, 
                replicas: [{"version": value, "osd_id": value, "sto_id":value}]}
            Each distribution entry as above is a single-line string. 
            Entries are separated by \n

        Raises:
            ValueError, If there is not an acessible directory on local_path arg
                or replication_level is not a integer value or there is an 
                osd.mapping file
    """
    local_path = sys.argv[1]
    rlevel = int(sys.argv[2])
    osd_mapping_output = sys.argv[3]
    ignored = sys.argv[4:]#NOTE: a ignored path cannot have am empty space.

    osd_gen = OsdGen(local_path, ignored)

    for parent, children in distribution(local_path, rlevel, osd_gen, 
                                             ignored).iteritems():
        #we take files from values and dirs from keys, to avoid duplicates
        if not parent.is_dir():
            raise Exception("Hey, keys should store directories")
        sys.stdout.write(json.dumps(parent.json()) + "\n")

        for child in children:
            if not child.is_dir():
                sys.stdout.write(json.dumps(child.json()) + "\n")

    with open(osd_mapping_output, 'w') as map_file:
        for path, osd_id in osd_gen.osdId_by_user_path().iteritems():
            map_file.write("\t".join([path, osd_id]) + "\n")
