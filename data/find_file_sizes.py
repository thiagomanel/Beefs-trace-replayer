def find_file_size(join_data_lines, path_and_timestamps):
    """ 
        join_data_lines is the input data to clean_trace.py
        path_and_timestamps is a list of tuple as
        [(path1, timestamp2) ... (pathn, timestampn)] where timestamp
        comes from the first occurrence of a llseek, write or read operation
        over the filepath to find. This list is timestamp ordered
    """
    def timestamp(path_and_timestamp):
        return path_and_timestamp[1]

    def join_line_timestamp(line):
        pass

    first_stamp = timestamp(path_and_timestamps[0])
    last_stamp = timestamp(path_and_timestamps[0])
    to_find = {}
    for path_and_stamp in path_and_timestamps:
        stamp = timestamp(path_and_stamp)
        if not stamp in to_find:
            to_find[stamp] = set()
        to_find[stamp].add(path_and_stamp)

    for line in join_data_lines:
        line_timestamp = join_line_timestamp(line)
        if first_stamp <= line_timestamp <= last_stamp:
            if 

