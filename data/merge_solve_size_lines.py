import sys

if __name__ == "__main__":

    def read_data(source):
        line_by_path = {}
        for line in source:
            tokens = line.split()
            line_by_path[tokens[0]] = line
        return line_by_path
   
    solved_output = sys.argv[1]#the partial output from solve_pre_replay_fsize_all.sh
    pre_replay_data = sys.argv[2]#the pre-replay data before find size
   
    solved_by_path = {}
    with open(solved_output) as solved_lines:
        solved_by_path = read_data(solved_lines)
   
    original_data = {}
    with open(pre_replay_data) as pre_replay_lines:
        original_data = read_data(pre_replay_lines)

    for line, data in original_data.iteritems():
        if not line in solved_by_path:
            sys.stdout.write("\t".join(data.split()) + "\n")
        else:
            sys.stdout.write("\t".join(solved_by_path[line].split()) + "\n")
