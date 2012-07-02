import os
import json
from itertools import groupby
from beefs_bootstrapper import *

iso = "ISO-8859-1"

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
            #when /path 3ad4fafb-0be0-49b3-ad0a-cda1c85fb6fd hostname
            #then ("3ad4fafb-0be0-49b3-ad0a-cda1c85fb6fd", "hostname")
            tokens = line.split()
            uuid = tokens[-2]
            hostname = tokens[-1]
            return {uuid:hostname}
        
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
        def replace_inode_id(line, old_id, new_id):
            return line.replace(old_id, new_id)

        def replace_osdid(entry, id_to_replacement):
            group = entry.group
            for osd_id, replicas in group.replicas_by_osdid().iteritems():
                if osd_id in id_to_replacement:
                    for replica in replicas:
                        replica.osd_id = id_to_replacement[osd_id]

        def remove_local_path(local_path_head, old_path):
            """ It removes the local path head. For example, with 
                local_path_head="/local/nfs_manel" and 
                "path": "/local/nfs_manel/manoel" we get "path": "/manoel"
            """
            return old_path.replace(local_path_head, "")

        with open(unform_path) as base_boot_data:
            old_root_inode_id = None
            new_root_inode_id = "0"
            formatted_entries = []

            for old_line in base_boot_data:
                entry = Entry.from_json(json.loads(old_line, encoding=iso))
                if not entry.is_dir():
                    replace_osdid(entry, replacement)
                entry.fullpath = remove_local_path(server_export_dir, 
                                                   entry.fullpath)
                formatted_entries.append(entry)
                if entry.fullpath == "/":#replace root inode id
                    old_root_inode_id, entry.inode_id = \
                        entry.inode_id, new_root_inode_id

            with open(form_path, 'w') as form_data:
                for entry in formatted_entries:
                    #update root's children
                    if entry.parent_id == old_root_inode_id:
                        entry.parent_id = new_root_inode_id
                    form_data.write(json.dumps(entry.json(), encoding=iso) + "\n")
                
    with open(boot_data_path) as boot_data:
        entries = [Entry.from_json(json.loads(entry, encoding=iso)) 
                       for entry in boot_data]
        generate_data_servers_metadata(entries, output_dir)

    queenbee_out_dir = os.path.join(output_dir, "queenbee_metadata")
    if not os.path.exists(queenbee_out_dir):
        os.mkdir(queenbee_out_dir)

    replacement = create_replacement(network_id_path)
    formatted_boot_path = os.path.join(queenbee_out_dir, "queenbee.boot")
    format_queenbee_input(replacement, server_export_dir, boot_data_path,
                          formatted_boot_path)
    generate_queenbee_metadata(formatted_boot_path, queenbee_out_dir)

if __name__ == "__main__":

    export_dir = sys.argv[1]
    boot_data_path = sys.argv[2]
    output_dir = sys.argv[3]
    network_id_path = sys.argv[4]

    main(export_dir, boot_data_path, output_dir, network_id_path)
