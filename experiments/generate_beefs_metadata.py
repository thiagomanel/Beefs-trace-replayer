import os
import json
from itertools import groupby
from beefs_bootstrapper import *

if __name__ == "__main__":

    """ It creates beefs metadata based on generate_boot_data.py output
        
        Args:
            boot_data_path (str): path to generate_boot_data.py output.
            output_dir (str): path to a directory to store generated beefs
                                  metadata.
    """

    boot_data_path = sys.argv[1]
    output_dir = sys.argv[2]
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

    generate_queenbee_metadata(boot_data_path, queenbee_out_dir)
