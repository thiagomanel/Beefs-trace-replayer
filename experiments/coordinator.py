import sys

def copy_package(tarball_path, dst_dir, machine_addr):
    pass

def sync_clock(machine_addr):
    pass

def execute(remote_command, machine_addr, delay=None):
    pass

def time(machine_addr):
    pass

if __name__ == "__main__":

    num_samples = int(sys.argv[1])
    with open(sys.argv[2) as machine_addr_file:
        machines_addr = machine_addr_file.readline()

    map(sync_clock, machines_addr)
    for machine_addr in machines_addrs:
        copy_package(tarball_path, remote_path, machine_addr)
        install_package(tarball_remote_path, machine_addr)

    for sample in range(num_samples):

        for machine_addr in machines_addrs:
            umount_client(machine_addr, mount_point)

        #no clients should be mounted
        clients_mount_status = [ (machine_addr, 
                                   check_mount(machine_addr, mount))
                                   for machine_addr in machines_addr]
        if any([mount_up for (machine, up) in clients_mount_status]):
            sys.stderr.write("Error on umounting clients" +
                              " ".join(clients_mount_status) + "\n")
            continue
        
        for machine_addr in machines_addrs:
            mount_client(machine_addr, mount_point)
        #now, we want everybody up
        clients_mount_status = [ (machine_addr, 
                                   check_mount(machine_addr, mount))
                                   for machine_addr in machines_addr]

        if not all([mount_up for (machine, up) in clients_mount_status]):
            sys.stderr.write("Error on mounting clients" +
                              " ".join(clients_mount_status) + "\n")
            continue
        
        #executing pre-replay
        pre_replay_path = "/".join([remote_path, "replayer", "pre_replay.py"])
        pre_replay_args = ["replay_dir_path", "replay_input_path", "join_file_path"]

        for machine_addr in machines_addr:
            execute("python " + pre_replay_path, pre_replay_args, machine_addr)


        pre_replay_path = "/".join([remote_path, "replayer", "beefs_replayer"])

        date_millis = date(machines_addr[0])
        for machine_addr in machines_addr:
            pre_replay_args = ["/".join([remote_path, "replayer", "beefs_replayer"])]
            execute("python " + pre_replay_path, pre_replay_args, machine_addr)

        #executing replay
        for machine_addr in machines_addr:
            pre_replay_args = ["/".join([remote_path, "replayer", "beefs_replayer"])]
            execute("python " + pre_replay_path, pre_replay_args, machine_addr)

        #collecting results
        #TODO

        #rolling back file system modifications
