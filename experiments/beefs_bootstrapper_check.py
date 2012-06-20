import sys
import json
from beefs_bootstrapper import *

if __name__ == "__main__":

    """ It checks if all directories and files under and subtree were considered
        by bootstrapper"

        Args:
             local_path (str): path used to generate the distribution
             bootstrapper_output (str): path to boostrapper output

        Raises:
            ValuerError: if local_path or bootstrapper_output are not valid,
                         accesible paths
    """
    def erro_msg(path):
        return "we missed %s generation" % path

    def generated_namespace(output_path):
        dirs = []
        files = []
        with open(output_path) as boot_data:
            entries = [Entry.from_json(json.loads(line)) for line in boot_data]
            for entry in entries:
                if entry.is_dir():
                    dirs.append(entry.fullpath)
                else:
                    files.append(entry.fullpath)
        return dirs, files

    local_path = sys.argv[1]
    output_to_check = sys.argv[2]

    gen_dirs, gen_files = generated_namespace(output_to_check)

    for root, dirs, files in os.walk(local_path):
        if not root in gen_dirs:
            sys.std.out(error_msg(root) + "\n")
        for _dir in dirs:
            if not _dir in gen_dirs:
                sys.std.out(error_msg(_dir) + "\n")
        for _file in files:
            if not _dir in gen_dirs:
                sys.std.out(error_msg(_file) + "\n")
