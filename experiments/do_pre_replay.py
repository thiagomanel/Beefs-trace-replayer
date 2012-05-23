import sys
import os

if __name__ == "__main__":
    """
        Usage: python do_pre_replay.py < pre_replay_data

        pre_replay data format
        /local/thiagoepdc/espadarte_nfs//home/manoelfmn/workspace/dev-0.2/.svn/entries	f	881
        /local/thiagoepdc/espadarte_nfs//home/manoelfmn/.java	d
    """

    def mkdir_p(path):
        os.makedirs(path)

    def create_file(path, size):
        with open(path, 'w') as _file:
            #input gives -1 when size is not available
            _file.truncate(max([size, 0]))

    def parse(line):
        def parse_path(line):#FIXME this code is duplicated in a number of files
            return line.split("<path=")[1].split("/>")[0]
        def parse_ftype(line):
            return line.split("<ftype=")[1].split("/>")[0]
        def parse_fsize(line):
            if "<fsize=" in line:
                return long(line.split("<fsize=")[1].split("/>")[0])
            else:
                return -1

        return parse_path(line), parse_ftype(line), parse_fsize(line)

    for line in sys.stdin:
        path, ftype, fsize = parse(line)
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
            if not os.path.exists(path):
                parent_dir = os.path.dirname(path)
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)
                create_file(path, fsize)
                sys.stdout.write("file created: " + path + "\n")

        os.chmod(path, 0777)
