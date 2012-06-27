import os
import json
from itertools import groupby
from beefs_bootstrapper import *

def replace_osdid(line, id_to_replacement):
     """
        It replaces the osdId uuid by a real network id.
        For example, where we have "osdId": "bc272f39-96b1-47c2-92e7-87c0f62b1be1"
        we replace by "osdId": {"hostname": name, "port": 1111, "dataPort": 2222}

        Args:
            line (str) - line on the old format
            id_to_replacement (dict) - a dict from uuid to real network ids
        Returns:
            A new line with the replacement
     """
     new_string = str(line)
     for old_id, replacement in id_to_replacement.iteritems():
         old_str = "\"" + old_id + "\""
         new_string = new_string.replace(old_str, replacement)        
     return new_string

def main(boot_data_path, output_dir, network_id_path):
    """ It creates beefs metadata based on generate_boot_data.py output
        
        Args:
            boot_data_path (str): path to generate_boot_data.py output.
            output_dir (str): path to a directory to store generated beefs
                              metadata.
            network_id_path (str): path to a file describing the mapping between
                                   uuid based osdIds used on boot_data_path and 
                                   real network ids used  on queenbee metadata.
    """
    def create_replacement(network_id_path):
        def parse(line):
            #from /local/nfs_manel/igorvcs	3ad4fafb-0be0-49b3-ad0a-cda1c85fb6fd {"hostname": "host1", "port": 1111, "dataPort": 2222
            #it returns ("3ad4fafb-0be0-49b3-ad0a-cda1c85fb6fd", "{"hostname": "host1",     "port": 1111, "dataPort": 2222}")a
            tokens = line.split()
            uuid = tokens[1]
            network_id = " ".join(tokens[2:])
            return {uuid:network_id}
        
        replacement = {}
        with open(network_id_path) as network_id_data:
            for line in network_id_data:
                replacement.update(parse(line))
        return replacement
                
    iso = "ISO-8859-1"
#    with open(boot_data_path) as boot_data:
#        entries = [Entry.from_json(json.loads(entry, encoding=iso)) 
#                       for entry in boot_data]
#
#        generate_data_servers_metadata(entries, output_dir)
#
    queenbee_out_dir = os.path.join(output_dir, "queenbee_metadata")
    if not os.path.exists(queenbee_out_dir):
        os.mkdir(queenbee_out_dir)
    queenbee_boot_data_path = os.path.join(queenbee_out_dir, "queenbee.boot")

    replacement = create_replacement(network_id_path)

    with open(queenbee_boot_data_path, 'w') as queenbee_boot_data:
        with open(boot_data_path) as base_boot_data:
            for old_line in base_boot_data:
                new_line = replace_osdid(old_line, replacement)
                queenbee_boot_data.write(new_line)

    generate_queenbee_metadata(queenbee_boot_data_path, queenbee_out_dir)

if __name__ == "__main__":

    boot_data_path = sys.argv[1]
    output_dir = sys.argv[2]
    network_id_path = sys.argv[3]

    main(boot_data_path, output_dir, network_id_path)
