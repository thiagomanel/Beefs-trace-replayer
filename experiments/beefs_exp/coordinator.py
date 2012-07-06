import sys
import os
import random
#import logging
import subprocess
from time import sleep

EXPERIMENT_INPUT_DIR="/tmp/home/thiagoepdc/experiments/beefs"
EXP_OUT_DIR = EXPERIMENT_INPUT_DIR + "/results/"

#and stuff running at lsd LAN
LAN_INPUT_DIR="/home/thiagoepdc/experiments/"

class Component:
    DATA_SERVER, CLIENT, META_SERVER = range(3)

class Deploy():
    def __init__(self, ms_node, node2replay_input, install_dir, mount_point):
        """
           Args:
               ms_node (str) - addr of metadata server node.
               node2replay_input (dict) - a dict from to node addr to the replay
                                          input to be replayed on this node.
               install_dir (str) - path to a dir where beefs was installed.
               mount_point (str) - path to the directory where honeybee mounts
                                   beefs.
        """
        self.ms_node = ms_node
        self.node2replay_input = node2replay_input
        self.mount_point = mount_point
        self.install_dir = install_dir
        self.beefs_script = "/".join([install_dir, "beefs", "bin", "beefs"])
        self.wait_and_replay_script_path = "/".join([EXPERIMENT_INPUT_DIR, 
                                                     "wait_and_replay.sh"])

        self.beefs_replayer_path = "/".join([EXPERIMENT_INPUT_DIR, 
                                             "beefs_replayer"])

    def ds_nodes(self):
        return self.node2replay_input.keys()

    def ms_node(self):
        return self.ms_node

    def umount(self, node):
        #I do not like much this check within the call (and raising an exception
        #but main code is a way more cleaner because of this.
        def do_umount(node, mount_point):
            return execute(" ".join(["umount", mount_point]), node)

        def check(node):
            #out, err, rcode = execute("mount | grep 150.165.85.239:/local/nfs_manel", )
            #fixme check by mount point (mount cmd provides some check ?)
           return out#if it is mounted, out is not empty, so it is true

        sys.stdout.write("umount node=%s mount_point=%s\n"
                          % (node, self.mount_point))
        out, err, rvalue = do_umount(node, self.mount_point)
        if not check(node):
            raise Exception("Unable to umount node=%s out=%s err=%s"
                            % (node, out, err))
        return out, err, rvalue

    def start(self, component_type, node):
        if component_type == Component.DATA_SERVER:
            remote_command = " ".join([self.beefs_script, "start", "honeycomb"])
            execute(remote_command, node, delay=None)
        elif component_type == Component.META_SERVER:
            remote_command = " ".join([self.beefs_script, "start", "queenbee"])
            execute(remote_command, node, delay=None)
	
    def stop(self, component_type, node):

        def do_stop(component_type, node):
            if component_type == Component.DATA_SERVER:
                remote_command = " ".join([self.beefs_script, "stop", "honeycomb"])
                return execute(remote_command, node, delay=None)
            elif component_type == Component.META_SERVER:
                remote_command = " ".join([self.beefs_script, "stop", "queenbee"])
                return execute(remote_command, node, delay=None)
            elif component_type == Component.CLIENT:
                remote_command = " ".join([self.beefs_script, "stop", "honeybee"])
                return execute(remote_command, node, delay=None)

        def check(node):#FIXME
            return True

        sys.stdout.write("stop component=%d node=%s\n" % (component_type, node))
        out, err, rvalue = do_stop(component_type, node)
        if not check(node):
            raise Exception("Unable to stop component=%d node=%s out=%s err=%s"
                            % (component_type, node, out, err))
        return out, err, rvalue

    def rollback(self, component_type, node):
        #CHECK rollback ?
        def rollback_ds_raw_data(node):
            pass
        def rollback_metadata(node):
            #we should specify a directory to store meta on beefs conf
            #and execute a rsync on this directory. we also need to store
            #all metadata, a directory per node at coordination local fs
            pass
        if component_type == Component.DATA_SERVER:
            rollback_ds_raw_data(node)
            rollback_metadata(node)
        elif component_type == Component.META_SERVER:
            rollback_metadata(node)

    def wait_and_start_replay(self, node, deadline, out_path, err_path):
        sys.stdout.write("wait and start node=%s\n" % (node))
        input_path = self.node2replay_input[node]
        cmd = " ".join(["bash", 
                        self.wait_and_replay_script_path,
                        str(deadline), self.beefs_replayer_path, input_path,
                        out_path, err_path, "&"])

        return execute(cmd, node)

    def time(self, node):
        out, err, rcode = execute("date +%s", node)
        return long(out)

    def wait_replay_end(self):
        def replayer_is_running(addr):
            out, err, rcod = execute("ps xau | grep beefs_replayer | grep -v grep", addr)
            return out#if it is running, out it not emptu, so it's is true

        sys.stdout.write("wait for replay termination in all nodes\n")
        while any([replayer_is_running(node) for node in self.ds_nodes()]):
            sys.stdout.write("Waiting worker nodes job termination\n")
            sleep(30)

    def copy_result(self, node):
        sys.stdout.write("collection results " + node + "\n")
        out, err, rcode = execute("mv /tmp/*replay* " + EXP_OUT_DIR, node)
        print out, err, rcode

def execute(remote_command, machine_addr, delay=None):
    process = subprocess.Popen(" ".join(["ssh",
	                                     "root@" + machine_addr,
                                             remote_command]),
					shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
    out, err = process.communicate()
    return out, err, process.returncode

def mount_client(addr, mount_point):
    return execute(" ".join(["mount", mount_point]), addr)

def main(num_samples, ms_node, node2replay_input, mount_point, install_dir):

    def base_out_path(node, sample):
        #/tmp/node.sample.random
        return os.path.join("/tmp", 
                            ".".join([node, str(sample), 
                                      str(int(random.random() * 10000000))])
                           )

    deploy = Deploy(ms_node, node2replay_input, install_dir, mount_point)

    nodes = node2replay_input.keys()#sugar
    for sample in range(num_samples):
        sys.stdout.write("Running sample " +  str(sample) + "\n")
        for node in nodes:
            deploy.umount(node)
            deploy.stop(Component.CLIENT, node)
            deploy.stop(Component.DATA_SERVER, node)
            deploy.rollback(Component.DATA_SERVER, node)

        deploy.stop(Component.META_SERVER, queenbee_node)
        deploy.rollback(Component.META_SERVER, queenbee_node)
 
        deploy.start(Component.META_SERVER, queenbee_node)
        for node in nodes:
            deploy.start(Component.DATA_SERVER, node)
            deploy.start(Component.CLIENT, node)

        now_epoch_secs = deploy.time(nodes[0])#nodes are sync'ed, just pick one
        deadline = now_epoch_secs + 30
        sys.stdout.write("now is: " + str(now_epoch_secs) +
                          " deadline will be " + str(deadline) + "\n")
        for node in nodes:#it'se better to have a separated for, help sync
            base_out = base_out_path(node, sample)
            out_file = base_out + ".replay.out"
            err_file = base_out + ".replay.err"
            deploy.wait_and_start_replay(node, deadline, out_file, err_file)

        deploy.wait_replay_end()
        for node in nodes:
            deploy.copy_result(node)

if __name__ == "__main__":
    """
        We assume:
             worker node have had their clocks syncronized
             worker nodes share a remote distributed file system to get replay input data
             communication to worker nodes is made by no-pass ssh
    """
    #logging.basicConfig(filename='example.log',level=logging.DEBUG)
    #logging.info('So should this')

    if len(sys.argv) < 7:
        sys.stderr.write("Usage: python coordinator.py num_samples queenbee_hostname machines_file trace_file mount_point beefs_dir_on_vm\n")
        sys.exit(-1)

    num_samples = int(sys.argv[1])
    queenbee_node = sys.argv[2]
    machine_file = sys.argv[3]
    trace_file = sys.argv[4]
    mount_point = sys.argv[5]
    beefs_dir_vm = sys.argv[6]

    with open(machine_file) as machines:
        with open(trace_file) as traces:
            machines_addr2replay_input = {}
            for addr in machines:
                trace_line = traces.readline()
                machines_addr2replay_input[addr.strip()] = trace_line.strip()
            machines_addr = machines_addr2replay_input.keys()

    sys.stdout.write(" ".join(["loaded machines", str(machines_addr), "\n"]))
    main(num_samples, queenbee_node, machines_addr2replay_input, mount_point, beefs_dir_vm)
