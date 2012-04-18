import sys

def is_write(line):
    return not line.find("write") == -1

def is_read(line):
    return not line.find("read") == -1

def expected(out_line):
    return out_line.split()[-2]

def actual(out_line):
    return out_line.split()[-1]

if __name__ == "__main__":
    """
    It checks replay actual responses against the expected ones for write
    and read operations
    """
    r_input_path = sys.argv[1]
    r_output_path = sys.argv[2]

    with open(r_input_path) as r_input:
        with open(r_output_path) as r_output:
            r_input.readline()#it skips total lines descriptor
            r_output.readline()#it skips fake root line
            for in_line in r_input:
                if is_write(in_line) or is_read(in_line):
                    out_line = r_output.readline()
                    r_expected = expected(out_line)
                    r_actual = actual(out_line)
                    line_id = in_line.split()[0]
                    sys.stdout.write(" ".join([str(r_expected == r_actual),
                                        line_id,
                                        r_expected,
                                        r_actual]) + "\n")
