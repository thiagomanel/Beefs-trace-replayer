import sys
import json
from beefs_bootstrapper import *

if __name__ == "__main__":

    """ It checks if all directories and files under and subtree were considered
        by bootstrapper"

        Args:
             local_path (str): path used to generate the distribution
             bootstrapper_output (str): path to boostrapper output
             *ignore_dirs (str): an arbitrary lenght, empty space sep, str args.
                                These directories will be ignored.

        Raises:
            ValuerError: if local_path or bootstrapper_output are not valid,
                         accesible paths
    """
    def error_msg(path):
        return "we missed %s generation" % path

    def generated_namespace(output_path):
        dirs = set()
        files = set()
        with open(output_path) as boot_data:
            for line in boot_data:
                entry = Entry.from_json(json.loads(line))
                if entry.is_dir():
                    dirs.add(entry.fullpath)
                else:
                    files.add(entry.fullpath)
        return dirs, files

    local_path = sys.argv[1]
    output_to_check = sys.argv[2]
    ignored = sys.argv[3:]#NOTE: a ignored path cannot have am empty space.

    gen_dirs, gen_files = generated_namespace(output_to_check)

    for root, dirs, files in walk(local_path, ignored):
        if not root in gen_dirs:
            sys.stdout.write(error_msg(root) + " directory\n")
        for _dir in dirs:
            fullpath_dir = os.path.join(root, _dir)
            if not fullpath_dir in gen_dirs:
                sys.stdout.write(error_msg(fullpath_dir) + " directory\n")
        for _file in files:
            fullpath_file = os.path.join(root, _file)
            if not fullpath_file in gen_files:
                sys.stdout.write(error_msg(fullpath_file) + " file\n")
