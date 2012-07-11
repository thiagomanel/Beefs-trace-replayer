import sys
import os

if __name__ == "__main__":
    """ It creates hidden files and directories on server side backup

        Args:
            old_head_dir (str) - head dir that was used to generate pre_replay
                                 input. It should be discarded 
            new_head_dir (str) - head dir to replace old_head_dir
            pre_replay_input (str) - path to replay input data
            

        pre_replay data format
        <path=/local/nfs_manel//nathaniel/.config/foo/> <ftype=d/>    
        <path=/local/nfs_manel//patrickjem/.config/journal/> <ftype=f/> <fsize=525824/>

        On above example, /local/nfs_manel is the old_head_dir
    """

    def mkdir_p(path):
        os.makedirs(path)

    def create_file(path, size):
        with open(path, 'w') as _file:
            #input gives -1 when size is not available
            _file.truncate(max([size, 0]))

    def parse(line, old_head_dir, new_head_dir):
        def parse_path(line):#FIXME this code is duplicated in a number of files
            return line.split("<path=")[1].split("/>")[0]
        def parse_ftype(line):
            return line.split("<ftype=")[1].split("/>")[0]
        def parse_fsize(line):
            if "<fsize=" in line:
                return long(line.split("<fsize=")[1].split("/>")[0])
            else:
                return -1

        old_path = parse_path(line)
        if not old_head_dir in old_path:
            raise Exception("path does not start with heading line:%s head:%s"
                            % (line, old_head_dir))

        new_path = old_path.replace(old_head_dir, new_head_dir)
        return new_path, parse_ftype(line), parse_fsize(line)

    old_head_dir = sys.argv[1]
    new_head_dir = sys.argv[2]
    pre_replay_input_path = sys.argv[3]

    with open(pre_replay_input_path) as pre_replay_input:
        for line in pre_replay_input:
            path, ftype, fsize = parse(line, old_head_dir, new_head_dir)
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
