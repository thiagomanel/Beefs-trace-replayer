import sys

if __name__ == "__main__":
    graph = open(sys.argv[1], 'r').readlines()
    consumed_lines = open(sys.argv[2], 'r').readlines()

    consumed = set()
    for c_line in consumed_lines:
           consumed.add(int(c_line))

    for line in graph:
       if int(line.split()[0]) in consumed:
           print line.strip(), "consumed"
       else:
           print line.strip()

