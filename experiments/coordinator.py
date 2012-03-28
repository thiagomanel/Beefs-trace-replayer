import sys
import os
import subprocess
import random

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
    out, err = process.communicate()
    return out, err, process.returncode

def time(machine_addr):
    out, err, rcode = execute("date +%s", machine_addr)
    return long(out)

def umount_client(addr, mount_point):
    return execute(" ".join(["umount", mount_point]), addr)

def mount_client(addr, mount_point):
    return execute(" ".join(["mount", mount_point]), addr)

def check_mount(addr, mount_point):
    out, err, rcode = execute("mount | grep /local/thiagoepdc/espadarte_nfs/home", addr)
    return out#if it is mounted, out is not empty, so it is true

if __name__ == "__main__":
    """ 
        We assume:
             worker node have had their clocks syncronized
             worker nodes share a remote distributed file system to get replay input data and binaries (see /home/thiagoepdc/experiments/nfs/ below)
             communication to worker nodes is made by no-pass ssh
    """
    if len(sys.argv) < 5:
        sys.stderr.write("Usage: python coordinator.py num_samples machines_file base_remote_path mount_point\n")
        sys.exit(-1)

    num_samples = int(sys.argv[1])
    with open(sys.argv[2]) as machine_addr_file:
        machines_addr2replay_input = {}
        for line in machine_addr_file:
            addr, r_input = line.split()
            machines_addr2replay_input[addr.strip()] = r_input.strip()
        machines_addr = machines_addr2replay_input.keys()

    sys.stdout.write(" ".join(["loaded machines", str(machines_addr), "\n"]))

    remote_path = sys.argv[3]
    mount_point = sys.argv[4]

    for sample in range(num_samples):
        sys.stdout.write("Running sample " +  str(sample) + "\n")

        for addr in machines_addr:
            sys.stdout.write(" ".join(["Umounting", addr, mount_point, "\n"]))
            umount_client(addr, mount_point)

        #no clients should be mounted
        clients_mount_status = [(addr, 
                                   check_mount(addr, mount_point))
                                   for addr in machines_addr]
        if any([up for (machine, up) in clients_mount_status]):
            sys.stderr.write("Error on umounting clients " +
                              " ".join([str(status) 
                                        for status in clients_mount_status])
                              + "\n")
            continue
        
        for addr in machines_addr:
            sys.stdout.write(" ".join(["Mounting", addr, mount_point, "\n"]))
            mount_client(addr, mount_point)
        #now, we want everybody up
        clients_mount_status = [ (addr, 
                                   check_mount(addr, mount_point))
                                   for addr in machines_addr]
        if not all([up for (machine, up) in clients_mount_status]):
            sys.stderr.write("Error on mounting clients " +
                              " ".join([str(status) 
                                        for status in clients_mount_status])
                              + "\n")
            continue

        #executing pre-replay
        sys.stdout.write("executing pre_replay\n")
        out, err, rcode = execute("python /home/thiagoepdc/experiments/nfs/do_pre_replay.py < /home/thiagoepdc/experiments/nfs/pre_replay_on_server_side.all", "espadarte")

        sys.stdout.write("checking pre_replay\n")
        out, err, rcode = execute("bash /home/thiagoepdc/experiments/nfs/do_pre_replay_check.sh /home/thiagoepdc/experiments/nfs/pre_replay_on_server_side.all", "espadarte")
        if not rcode == 0:
            sys.stderr.write("pre_replay didn't work\n")

        #date_millis = date(machines_addr[0])
        #executing replay
        for addr, r_input in machines_addr2replay_input.iteritems():
            sys.stdout.write("executing replay addr " + addr + " input " + r_input + "\n")
            base_out = "/tmp/" + addr + "." + str(sample) + "." + str(int(random.random() * 10000000))
            out_file = base_out + ".replay.out"
            err_file = base_out + ".replay.err"
            execute("/home/thiagoepdc/experiments/nfs/beefs_replayer " + r_input + " > " + out_file + " 2> " + err_file,
                           addr)

        for addr, r_input in machines_addr2replay_input.iteritems():
            sys.stdout.write("collection results " + addr + "\n")
            execute("cp /tmp/*replay* /home/thiagoepdc/experiments/nfs/results/", addr)
"""
        #rolling back file system modifications
        #sys.stdout.write("rolling back\n")
        #execute("/home/thiagoepdc/experiments/nfs/rollbackfs.sh", "espadarte")"""
