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

    with open(boot_data_path) as boot_data:
        entries = [Entry.from_json(json.loads(entry, encoding=iso)) 
                       for entry in boot_data]
        generate_beefs_metadata(entries, output_dir)
