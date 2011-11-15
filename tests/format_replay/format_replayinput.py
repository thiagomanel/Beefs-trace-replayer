import sys

def parse_time(line):
    (start, elapsed) = line.split()[5].split("-")
    return (long(start), long(elapsed))

def with_new_timestamp(line, newtimestamp):
    newline = line.split()[0:5]
    newline.append(str(newtimestamp))
    newline.extend(line.split()[6:])
    return newline

def entry_line(line):
    #1159 2364 32311 (eclipse) mkdir 2649-480 /tmp/jdt-images 511 0
    #1159 2364 32311 (eclipse) mkdir 2649 /tmp/jdt-images 511 0
    (start, elapsed) = parse_time(line)
    return with_new_timestamp(line, start)

def return_line(line):
    #1159 2364 32311 (eclipse) mkdir 2649-480 /tmp/jdt-images 511 0
    #1159 2364 32311 (eclipse) return mkdir 3129 /tmp/jdt-images 511 0
    (start, elapsed) = parse_time(line)
    w_timestamp =  with_new_timestamp(line, start + elapsed)
    w_timestamp.insert(4, "return") #adding "return" token before proper call name
    return w_timestamp

def line_with_id(line, id):
    line.append(str(id))
    return line

def timestamp(formatted_line):
    if formatted_line[4] == "return":
    	return long(formatted_line[5+1])
    else:
	return long(formatted_line[5])

def format_input(input_file, output_file):
#collision
    intermediate = {}
    trace_line_id = 1
    for in_line in input_file:
	entry_l = entry_line(in_line)
	return_l = return_line(in_line)
	intermediate[timestamp(entry_l)] = line_with_id(entry_l, trace_line_id)
	intermediate[timestamp(return_l)] = line_with_id(return_l, trace_line_id)
	trace_line_id = trace_line_id + 1
    for stamp in sorted(intermediate.iterkeys()):
	output_file.write(" ".join(intermediate[stamp]) + "\n")

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as trace_input:
        with open(sys.argv[2], 'r+w') as formatted_file:
	    format_input(trace_input, formatted_file)
