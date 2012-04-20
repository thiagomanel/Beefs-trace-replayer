import sys

if __name__ == "__main__":
    """
       Usage: python frame_with_loader_ge.py num_machines given_load < load_data > frames_ge

       It gives timeframes in which num_machine machines had load superior or equals
       to given_load.
    """
    num_machines = int(sys.argv[1])
    floor_load = long(sys.argv[2])
    frame_to_machine_loads = {}

    #we don't have much data here, so I'll read them all
    for line in sys.stdin:
        tokens = line.split()
        frame, load, machine = long(tokens[0]), long(tokens[1]), tokens[2]
        if not frame in frame_to_machine_loads:
            frame_to_machine_loads[frame] = set()
        frame_to_machine_loads[frame].add((machine, load))

    for frame, loads in frame_to_machine_loads.iteritems():
        num_machines_high_load = len([(machine, load) for machine, load in loads if load >= floor_load])
        if num_machines_high_load >= num_machines:
            num_machines = len(loads)
            machines_load = [str((machine, load)) for machine, load in loads]
            sys.stdout.write(" ".join([str(frame), str(num_machines_high_load),
                             str(num_machines), " ".join(machines_load), "\n"]))
