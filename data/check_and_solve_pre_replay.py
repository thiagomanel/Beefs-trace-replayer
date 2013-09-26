import sys

if __name__ == "__main__":
    """
    It seems that pre_replay is not bullet-proven, for example, I saw the same
    path being includude both as directory and file to be created. This code tries
    to solve these inconsistences.
    Usage: python check_and_solve_pre_replay.py < pre_replay_data > checked_pre_replay 2> checking_log
    """
    def is_file(path_info):
        return path_info[0] == "f"

    def is_dir(path_info):
        return path_info[0] == "d"

    path_2_lines = {}
    for replay_line in sys.stdin:
        tokens = replay_line.split()
        path = tokens[0]
        ftype = tokens[1]
        if not path in path_2_lines:
            path_2_lines[path] = []
        path_2_lines[path].append((ftype, replay_line))

    for path, path_infos in path_2_lines.iteritems():
        if len(path_infos) == 1:#there is no collision on path
            info = path_infos[0]
            original_line = info[-1]
            sys.stdout.write(original_line)
        else:
            choosen_line = None
            for info in path_infos:
                if is_dir(info):
                    choosen_line = info[-1]
                    break
            if choosen_line:
                sys.stdout.write(choosen_line)
                sys.stderr.write(" ".join(["we choose ",
	                                   choosen_line,
                                           "from",
                                           str(path_infos)]))
            else:
                sys.stderr.write("we were no able to fix this path " +
                                  path +
                                  " original_lines " +
                                  str(path_infos) + "\n")
