import sys

if __name__ == "__main__":
    """
        We added some pid/tid marks in our bt monitor, this
        filters worker thread activity in
        Usage: python clean_bt.py < bt.out
    """
    #TODO: filter worker threads.
    for line in sys.stdin:
        if "pid=" in line:
            #format:
            #        78 pid=0 tid=8562
            #        $count pid=$valuepid tid=$valuetid
            tokens = line.split()
            count = tokens[0].strip()
            print " ".join(["\t", count])
        else:
            print line.strip()
