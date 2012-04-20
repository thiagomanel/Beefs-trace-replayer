import sys
import os
from datetime import datetime
import subprocess

def stamp(filename):
    return datetime.strptime(filename.split("-")[0], "%Y%m%d%H%M%S")

def machine(filename):
    """from "20111021000002-gupi.log.26.filtered.sort" returns gupi"""
    return filename.split("-")[1].split(".")[0]

def stamp_and_seq_cmp(stamp_name1, stamp_name2):
    """compare tuples (stamp, filename)"""
    def seq(filename):
        """from "20111021000002-gupi.log.26.filtered.sort" returns 26"""
        return int(filename.split(".log.")[1].split(".filtered")[0])

    if stamp_name1[0] == stamp_name2[0]:
        return  seq(stamp_name1[1]) - seq(stamp_name2[1])
    elif (stamp_name1[0] < stamp_name2[0]):
        #time_delta operations before python 2.7 are not that easy, so
        #that is the reason we are if and elif'ing and returning -1 and 1
        return -1
    else:
        return 1

def group_by_date(filenames):
    files_by_date = {}
    for _file in filenames:
        _stamp = stamp(_file)
        date = (_stamp.year, _stamp.month, _stamp.day)
        if not date in files_by_date:
            files_by_date[date] = []
        files_by_date[date].append((_stamp, _file))
    return files_by_date

def cat(filenames, output):
    subprocess.call(["cat"] + filenames, stdout=output)

if __name__ == "__main__":
    """ It concats .sort files based on creation date and sequence number.
        It outputs a *.join file """
    data_dir = sys.argv[1]
    files_by_date = group_by_date(os.listdir(data_dir))

    for date in sorted(files_by_date.keys()):
        stamp_filenames = files_by_date[date]
        sorted_by_seq = sorted(stamp_filenames, cmp=stamp_and_seq_cmp)

        machine_name = machine(sorted_by_seq[0][1])
        date_str = "_".join([str(date[0]), str(date[1]), str(date[2])])

        with open(data_dir + "/" + date_str + "-" + machine_name + ".join", 'w') as cat_file:
            filenames = [data_dir + "/" + filename for (stamp, filename) in stamp_filenames]
            cat(filenames, cat_file)
