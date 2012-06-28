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

def remove_local_path(local_path_head, line):
    """ It removes the local path head. For example, with 
        local_path_head="/local/nfs_manel" and 
        line="{"path": "/local/nfs_manel/patrickjem/coreutils-5.0/m4", 
        "type": "d", 
        "inodeId": "29c26445-fbe4-414c-8184-031763d9a410", 
        "group": {}, "parentId": "b890b2d0-13ba-4ebf-8e08-619b3813752c"
       }"

       we get

       {"path": "/patrickjem/coreutils-5.0/m4", 
        "type": "d", 
        "inodeId": "29c26445-fbe4-414c-8184-031763d9a410", 
        "group": {}, "parentId": "b890b2d0-13ba-4ebf-8e08-619b3813752c"
       }
    """
    return line.replace(local_path_head, "")

def main(server_export_dir, boot_data_path, output_dir, network_id_path):
    """ It creates beefs metadata based on generate_boot_data.py output
        
        Args:
            server_export_dir (str): Namespace is stored under this dir at 
                                     server side.
            boot_data_path (str): path to generate_boot_data.py output.
            output_dir (str): path to a directory to store generated beefs
                              metadata.
            network_id_path (str): path to a file describing the mapping between
                                   uuid based osdIds used on boot_data_path and 
                                   real network ids used  on queenbee metadata.
    """
    def create_replacement(network_id_path):
        def parse(line):
            #when
            #/path 3ad4fafb-0be0-49b3-ad0a-cda1c85fb6fd {"hostname": "host1", "port": 1, "dataPort": 2}
            #then
            #("3ad4fafb-0be0-49b3-ad0a-cda1c85fb6fd", "{"hostname": "host1", "port": 1, "dataPort": 2}")
            tokens = line.split()
            uuid = tokens[1]
            network_id = " ".join(tokens[2:])
            return {uuid:network_id}
        
        replacement = {}
        with open(network_id_path) as network_id_data:
            for line in network_id_data:
                replacement.update(parse(line))
        return replacement

    def format_queenbee_input(replacement, exp_dir, unform_path, form_path):

        """ It formats boot data. New format has network ids instead uuid,
            paths had their leading path removed of "exp_dir". Root's inode_id
            is replace by "0" to follow beefs internals.
            Args:
                replacement (dict): a {uuid:network_id} dict
                exp_dir (src): leading path to be remove on formated file
                unform_path (str): path to unformatted input file
                form_path (str): formatted data will be store here
        """
        def inode_id(line):
            return line.split("inodeId\": ")[1].split("\"")[1]

        def path(line):
            return line.split("path\": ")[1].split("\"")[1]

        def replace_inode_id(line, old_id, new_id):
            return line.replace(old_id, new_id)

        with open(unform_path) as base_boot_data:
            root_inode_id = None
            formatted_lines = []

            for old_line in base_boot_data:
                new_line = replace_osdid(old_line, replacement)
                new_line = remove_local_path(server_export_dir, new_line)
                formatted_lines.append(new_line)
                if path(new_line) == "/":
                    root_inode_id = inode_id(new_line)

            with open(form_path, 'w') as form_data:
                for line in formatted_lines:
                    final_line = replace_inode_id(line, root_inode_id, "0")
                    form_data.write(final_line)
                
    iso = "ISO-8859-1"
    with open(boot_data_path) as boot_data:
        entries = [Entry.from_json(json.loads(entry, encoding=iso)) 
                       for entry in boot_data]

        generate_data_servers_metadata(entries, output_dir)

    queenbee_out_dir = os.path.join(output_dir, "queenbee_metadata")
    if not os.path.exists(queenbee_out_dir):
        os.mkdir(queenbee_out_dir)
    formatted_boot_path = os.path.join(queenbee_out_dir, "queenbee.boot")

    replacement = create_replacement(network_id_path)
    format_queenbee_input(replacement, server_export_dir, boot_data_path,
                          formatted_boot_path)
    generate_queenbee_metadata(formatted_boot_path, queenbee_out_dir)

if __name__ == "__main__":

    export_dir = sys.argv[1]
    boot_data_path = sys.argv[2]
    output_dir = sys.argv[3]
    network_id_path = sys.argv[4]

    main(export_dir, boot_data_path, output_dir, network_id_path)
