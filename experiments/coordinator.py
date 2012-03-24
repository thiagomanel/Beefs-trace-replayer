import sys
import subprocess
import os

def copy_package(tarball_path, dst_dir, machine_addr):
    remote = ":".join([machine_addr, dst_dir])
    process = subprocess.Popen(" ".join(["scp -r", 
                                         tarball_path, 
                                         remote
                                        ]), shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    return process.communicate()

def execute(remote_command, machine_addr, delay=None):
    process = subprocess.Popen(" ".join(["ssh",
                                         machine_addr,
                                          remote_command]), shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    return process.communicate()

def install_package(remote_path, tarball_name, machine_addr):
    remote_tar_path = remote_path + "/" + tarball_name
    return execute(" ".join(["tar", "xjvf", remote_tar_path, "-C", remote_path]), machine_addr)

def time(machine_addr):
    out, err = execute("date +%s", machine_addr)
    return long(out)

def umount_client(addr, mount_point):
    pass

def mount_client(addr, mount_point):
    pass

def check_mount(addr, mount_point):
    return True

if __name__ == "__main__":
    """ 
        We assume:
             worker node have had their clocks syncronized
    """

    if len(sys.argv) < 6:
        sys.stderr.write("Usage: python coordinator.py num_samples machines_file tarball_path base_remote_path mount_point\n")
        sys.exit(-1)

    num_samples = int(sys.argv[1])
    with open(sys.argv[2]) as machine_addr_file:
		machines_addr = [addr.strip() for addr in machine_addr_file.readlines()]
    sys.stdout.write(" ".join(["loaded machines", str(machines_addr), "\n"]))

    tarball_path = sys.argv[3]
    remote_path = sys.argv[4]
    mount_point = sys.argv[5]

    for addr in machines_addr:
        sys.stdout.write(" ".join(["copying", tarball_path, "to", addr, "\n"]))
        out, err = copy_package(tarball_path, remote_path, addr)
        sys.stdout.write(" ".join(["DONE", "out", str(out), "err", str(err), "\n"]))
        if err:
            sys.exit(-1)

    for addr in machines_addr:
        sys.stdout.write(" ".join(["Installing package", tarball_path, "to", addr, "\n"]))
        out, err = install_package(remote_path, os.path.basename(tarball_path), addr)
        sys.stdout.write(" ".join(["DONE", "out", str(out), "err", str(err), "\n"]))
        if err:
            sys.exit(-1)

    for sample in range(num_samples):

        for addr in machines_addr:
            umount_client(addr, mount_point)

        #no clients should be mounted
        clients_mount_status = [ (addr, 
                                   check_mount(addr, mount_point))
                                   for addr in machines_addr]
        if any([up for (machine, up) in clients_mount_status]):
            sys.stderr.write("Error on umounting clients" +
                              " ".join([str(status) 
                                        for status in clients_mount_status])
                              + "\n")
            continue
        
        for addr in machines_addr:
            mount_client(addr, mount_point)
        #now, we want everybody up
        clients_mount_status = [ (addr, 
                                   check_mount(addr, mount_point))
                                   for addr in machines_addr]

        if not all([up for (machine, up) in clients_mount_status]):
            sys.stderr.write("Error on mounting clients" +
                              " ".join([str(status) 
                                        for status in clients_mount_status])
                              + "\n")
            continue
        
        #executing pre-replay
            #maybe we can run the pre-replay at server side instead of
		    #before each sample. To do so, is safer to keep one data set equals to
            #nfs extraction.
        pre_replay_path = "/".join([remote_path, "replayer", "pre_replay.py"])
        pre_replay_args = ["replay_dir_path", "replay_input_path", "join_file_path"]

        for addr in machines_addr:
            execute("python " + pre_replay_path, pre_replay_args, addr)


        pre_replay_path = "/".join([remote_path, "replayer", "beefs_replayer"])

        date_millis = date(machines_addr[0])
        for addr in machines_addr:
            pre_replay_args = ["/".join([remote_path, "replayer", "beefs_replayer"])]
            execute("python " + pre_replay_path, pre_replay_args, addr)

        #executing replay
        for addr in machines_addr:
            replay_path = ["/".join([remote_path, "replayer", "beefs_replayer"])]
            execute(replay_path, replay_args, addr)

        #collecting results
        #TODO

        #rolling back file system modifications
        for addr in machines_addr:
            execute("bash " + "rollbackfs.sh", addr)
