import sys

if __name__ == "__main__":
    """ It seems we have problems on sorting (I've detected this on replaying
        a trace, a child's stamps was earlier than its parent. Not sure if this problem
        can affect ordering for example, it is possible.
        Usage: python check_timestamp_sort.py < data
        It works for any data that uses timestamp as 6th token (does not work for workflow data)
    """
    last_stamp = -1
    for line in sys.stdin:
        #e.g line 1007 23211 23221 (chromium-browse) read 1319217570137312-86 /home/tiagohsl/.config/chromium/Default/Cookies-journal 79 8 0
        #from 1319217570137312-86 returns 1319217570137312
        timestamp = long(line.split()[5].split("-")[0])
        if last_stamp == -1:
            last_stamp = timestamp
        if timestamp < last_stamp:
            sys.stderr.write(" ".join([line, "timestamp decreased\n"]))
            sys.exit(-1)
