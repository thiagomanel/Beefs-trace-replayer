import sys
import os

if __name__ == "__main__":
    """
        Usage: python do_pre_replay.py < pre_replay_data

        pre_replay data format
        /local/thiagoepdc/espadarte_nfs//home/manoelfmn/workspace/dev-0.2/.svn/entries	f	881	1319217032469221-174
        /local/thiagoepdc/espadarte_nfs//home/manoelfmn/.java	d
    """

    def mkdir_p(path):
        os.makedirs(path)

    def create_file(path, size):
        with open(path, 'w') as _file:
            #input gives -1 when size is not available
            _file.truncate(max([size, 0]))

    for line in sys.stdin:
        tokens = line.split()
        path, ftype = tokens[0], tokens[1]
        if os.path.exists(path):
            sys.stderr.write("path " + path + " already exists\n")
        elif ftype == "d":
            if not os.path.exists(path):
                try:
                    mkdir_p(path)
                    sys.stdout.write("directory created: " + path + "\n")
                except OSError as exc: # Python >2.5
                    sys.stderr.write("Error creating dir: " + path + "\n")
        elif ftype == "f":
            try:
                f_size = int(tokens[2])
            #pre_replay.py it is still not filtering all None Value
            except ValueError:
                f_size = -1

            if not os.path.exists(path):
                parent_dir = os.path.dirname(path)
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)
                create_file(path, f_size)
                sys.stdout.write("file created: " + path + "\n")

        os.chmod(path, 0777)
