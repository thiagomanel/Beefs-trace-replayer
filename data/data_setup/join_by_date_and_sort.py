import sys
import os
from datetime import datetime

def sorted_by_seq(filenames):
    "20111021000002-gupi.log.26.filtered.sort"

if __name__ == "__main__":
    """It concats .sort files based on creation date and sequence number.
       It sorts this concatened file"""
    data_dir = sys.argv[1]
    files_by_date = {}
    for _file in os.listdir(data_dir):
        stamp = datetime.strptime(_file, "%Y%m%d%H%M%S")
        date = (stamp.year, stamp.month, stamp.day)
        if not date in files_by_data:
            files_by_date[date] = []
        files_by_date[date].append(_file)

        
    for date in sorted(files_by_date.keys()):
        file_names = files_by_date[date]
        sorted_by_seq = sorted(filenames, key=lambda 
                               name: name.split(".log.")[1].split(".filtered")[0])
        for name in sorted_by_seq:
            print name

