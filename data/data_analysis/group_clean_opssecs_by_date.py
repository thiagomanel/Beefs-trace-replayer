import sys
import time

if __name__ == "__main__":
    """
        Usage: python group_clean_opssecs_by_date.py
        It receives a ops_secs.py output (possibly a collection of cat'ed outputs)
        then, it filters the input out by grouping lines at the same day
    """
    def date(stamp_secs):
        tm = time.gmtime(stamp_secs)
        return tm.tm_year, tm.tm_mon, tm.tm_mday 

    files_by_date = {}

    for line in sys.stdin:
        #e.g 1318613152181007 655 abelhinha
        stamp_str = line.split()[0]
        _date = date(long(stamp_str)/1000000)
        (year, month, day) = _date
        if not _date in files_by_date:
            new_file_name = "_".join([str(year), str(month), str(day)])
            files_by_date[_date] = open(new_file_name, 'w')
        _file = files_by_date[_date]
        _file.write(line)

    for _file in files_by_date.values():
        _file.close()
