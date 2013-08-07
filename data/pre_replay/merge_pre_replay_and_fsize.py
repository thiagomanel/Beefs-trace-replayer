import sys

if __name__ == "__main__":
    """
       It merges the output from pre_replay.py and pre_replay_fsize.py
       pre_replay_fsize.py script modifies some line from pre_replay.py when
       it finds right sizes for them. This script merge these modification back
       to original input
    """ 
    def read_data(source):
        def parse_pre_replay(line):#FIXME duplicated code
            def parse_path(line):
                return line.split("<path=")[1].split("/>")[0]
            def parse_ftype(line):
                return line.split("<ftype=")[1].split("/>")[0]
            return parse_path(line), parse_ftype(line)

        line_by_path = {}
        for line in source:
            path = parse_pre_replay(line)[0]
            line_by_path[path] = line.strip()
        return line_by_path
   
    #the partial output from solve_pre_replay_fsize_all.sh
    solved_output = sys.argv[1]
    #the pre-replay data before find size, cat'ed as a single file
    pre_replay_data = sys.argv[2]
   
    solved_by_path = {}
    with open(solved_output) as solved_lines:
        solved_by_path = read_data(solved_lines)
   
    original_data = {}
    with open(pre_replay_data) as pre_replay_lines:
        original_data = read_data(pre_replay_lines)

    for path, data in original_data.iteritems():
        if not path in solved_by_path:
            sys.stdout.write(data + "\n")
        else:
            sys.stdout.write(solved_by_path[path] + "\n")
