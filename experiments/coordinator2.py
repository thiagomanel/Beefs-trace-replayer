import sys
import os
import subprocess
import random
import time

def execute(remote_command, machine_addr, delay=None):
    if machine_addr.startswith("150"):#cloudgley machine, for lan we use names
        process = subprocess.Popen(" ".join(["ssh -i /home/patrickjem/cloudigley/.euca/patrick_key.private",
                                         "root@"+machine_addr,
                                          remote_command]), shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    else:
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
    out, err, rcode = execute("mount | grep 150.165.85.239:/local/nfs_manel", addr)
    return out#if it is mounted, out is not empty, so it is true

def replayer_is_running(addr):
    out, err, rcod = execute("ps xau | grep beefs_replayer | grep -v grep", addr)
    return out#if it is running, out it not emptu, so it's is true

if __name__ == "__main__":
    """
        We assume:
             worker node have had their clocks syncronized
             worker nodes share a remote distributed file system to get replay input data
             communication to worker nodes is made by no-pass ssh
    """
    if len(sys.argv) < 4:
        sys.stderr.write("Usage: python coordinator.py num_samples machines_file mount_point\n")
        sys.exit(-1)

    num_samples = int(sys.argv[1])
    with open(sys.argv[2]) as machine_addr_file:
        machines_addr2replay_input = {}
        for line in machine_addr_file:
            addr, r_input = line.split()
            machines_addr2replay_input[addr.strip()] = r_input.strip()
        machines_addr = machines_addr2replay_input.keys()

    sys.stdout.write(" ".join(["loaded machines", str(machines_addr), "\n"]))

    mount_point = sys.argv[3]

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
        out, err, rcode = execute("python /home/thiagoepdc/experiments/nfs/do_pre_replay.py < /home/thiagoepdc/experiments/nfs/pre_replay_on_server_side.all", "espadarte.lsd.ufcg.edu.br")

        sys.stdout.write("checking pre_replay\n")
        out, err, rcode = execute("bash /home/thiagoepdc/experiments/nfs/do_pre_replay_check.sh /home/thiagoepdc/experiments/nfs/pre_replay_on_server_side.all", "espadarte.lsd.ufcg.edu.br")
        if not rcode == 0:
            sys.stderr.write("pre_replay didn't work\n")

        #executing replay
        now_epoch_secs = time(machines_addr[0])
        deadline = now_epoch_secs + 30
        sys.stdout.write("now is: " + str(now_epoch_secs) + " deadline will be " + str(deadline) + "\n")

        for addr, r_input in machines_addr2replay_input.iteritems():
            sys.stdout.write("executing replay addr " + addr + " input " + r_input + "\n")

            base_out = "/tmp/" + addr + "." + str(sample) + "." + str(int(random.random() * 10000000))
            out_file = base_out + ".replay.out"
            err_file = base_out + ".replay.err"

            execute(" ".join(["bash /home/thiagoepdc/experiments/nfs/wait_and_replay.sh",
                              "/root/nfs_lsd/thiagoepdc/experiments/nfs/beefs_replayer",
                              str(deadline),
                              r_input, out_file, err_file,
                              "&"]),
                           addr)

        #wait for replay termination in all nodes
        while any([replayer_is_running(addr) for addr in machines_addr]):
            sys.stdout.write("Waiting worker nodes job termination\n")
            time.sleep(30)

        for addr, r_input in machines_addr2replay_input.iteritems():
            sys.stdout.write("collection results " + addr + "\n")
            execute("cp /tmp/*replay* /home/thiagoepdc/experiments/nfs/results/", addr)
"""
        #rolling back file system modifications
        #sys.stdout.write("rolling back\n")
        #execute("/home/thiagoepdc/experiments/nfs/rollbackfs.sh", "espadarte.lsd.ufcg.edu.br")"""
