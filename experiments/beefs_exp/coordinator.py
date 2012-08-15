import sys
import os
import random
import subprocess
from time import sleep

#pass them as args
SCRIPTS_DIR="/tmp/replay_scripts/"
EXP_OUT_DIR = "/data/results/"

class Component:
    def __init__(self, process_name, name):
        self.__process_name = process_name
        self.__name = name

    def process_name(self):
        return self.__process_name

    def name(self):
        return self.__name

DATA_SERVER = Component("Honeycomb", "honeycomb")
META_SERVER = Component("Queenbee", "queenbee")
CLIENT = Component("Honeybee", "honeybee")

class Config():
    def __init__(self, config_data):
        """
           Args:
               config_data: (dict) - a {ip:[type, name, replay_input, 
                                            backup_raw_dir, backup_metadir]} 
                                     dict
        """
        self.config_data = config_data
        self.__ds_nodes__ = [ip for ip in self.config_data.keys() 
                if self.component_type(ip) is DATA_SERVER]
        self.__ms_node__ = None
        for ip in self.config_data.keys():
            if self.component_type(ip) is META_SERVER:
                self.__ms_node__ = ip
                break

    def ds_nodes(self):
        return self.__ds_nodes__

    def ms_node(self):
        return self.__ms_node__

    def component_type(self, ip):
        return self.config_data[ip][0]

    def node_name(self, ip):
        return self.config_data[ip][1]

    def replay_input_path(self, ip):
        return self.config_data[ip][2]

    def backup_raw_dir(self, ip):
        return self.config_data[ip][3]

    def backup_metadir(self, ip):
        return self.config_data[ip][4]

class Deploy():
    def __init__(self, config, install_dir, mount_point, raw_dir):
        self.config = config
        self.mount_point = mount_point
        self.install_dir = install_dir
        self.raw_dir = raw_dir

        self.beefs_script = "/".join([install_dir, "bin", "beefs"])
        self.wait_and_replay_script_path = "/".join([SCRIPTS_DIR, 
                                                     "wait_and_replay.sh"])
        self.beefs_replayer_path = "/".join([SCRIPTS_DIR, 
                                             "beefs_replayer"])

    def ds_nodes(self):
        return self.config.ds_nodes()

    def ms_node(self):
        return self.config.ms_node()

    def component_is_running(self, node, component):
        out, err, rcod = execute("ps xau | grep " + 
                                  component.process_name() + 
                                  " | grep -v grep", node)
        return out#if it is running, out it not empty, so it's is true

    def umount(self, node):
        #I do not like much this check within the call (and raising an exception
        #but main code is a way more cleaner because of this.
        def do_umount(node, mount_point):
            return execute(" ".join(["umount", mount_point]), node)

        def is_mounted(node):
           out, err, rcode = execute("mount", node)
           return "beefs" in out

        if is_mounted(node):
            sys.stdout.write("umount node=%s mount_point=%s\n"
                             % (node, self.mount_point))
            out, err, rvalue = do_umount(node, self.mount_point)
            sleep(5)
            if is_mounted(node):
                raise Exception("unable to umount node=%s out=%s err=%s"
                                % (node, out, err))
        else:
            sys.stdout.write("not mounted. skipping node=%s mount_point=%s\n"
                             % (node, self.mount_point))

    def start(self, component, node):
        def command(component):
            return " ".join([self.beefs_script, "start", component.name()])

        if self.component_is_running(node, component):
            sys.stdout.write("component is running. skipping start node=%s\n" 
                             % (node))
        else:
            remote_cmd = command(component)
            out, err, rvalue = execute(remote_cmd, node, delay=None)
            sys.stdout.write("start cmd sent component=%s node=%s cmd=%s out=%s err=%s\n"
                             % (component.name(), node, remote_cmd, out, err))
            sleep(10)
            if not self.component_is_running(node, component):
                raise Exception("unable to start component=%s node=%s cmd=%s out=%s err=%s\n"
                                % (component.name(), node, remote_cmd, out, err))
            return out, err, rvalue
            
    def stop(self, component, node):

        def do_stop(component, node):
            remote_command = " ".join([self.beefs_script, "stop", component.name()])
            return execute(remote_command, node, delay=None)

        if not self.component_is_running(node, component):
            sys.stdout.write("component was not running. skipping stop component=%s node=%s\n" 
                             % (component.name(), node))
        else:
            out, err, rvalue = do_stop(component, node)
            sleep(5)
            if self.component_is_running(node, component):
                raise Exception("unable to stop component=%s node=%s out=%s err=%s"
                                % (component.name(), node, out, err))
            return out, err, rvalue

    def rollback(self, component, node):

        def rollback_ds_raw_data(node):
            backup_path = self.config.backup_raw_dir(node)
            dst_path = "root@" + ":".join([node, self.raw_dir])

            rollback_cmd = " ".join(["rsync", "-progtl", "--delete",
                                     backup_path + "/",
                                     dst_path])
            print "rollback raw dir cmd", rollback_cmd
            process = subprocess.Popen(rollback_cmd,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            out, err = process.communicate()
            return out, err, process.returncode

        def rollback_metadata(node):
            backup_path = self.config.backup_metadir(node)
            #note that base beefs deployment conf file should use this path
            #as metadata dir
            #we cannot user /* on src rsync path, because the number of files
            #is greater than max num args. instead we rsync the whole directory

            vm_metadir = "/".join([self.install_dir, "metadata/"])
            dst_path = "root@" + ":".join([node, vm_metadir])

            rollback_cmd = " ".join(["rsync", "-progtl", "--delete",
                                     backup_path + "/*",
                                     dst_path])
            print "rollback metadata cmd", rollback_cmd
            process = subprocess.Popen(rollback_cmd,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            out, err = process.communicate()
            return out, err, process.returncode

        def rollback_deploy(node):
            sys.stdout.write("rolling back deploy node=%s\n" % (node))
            backup_path = "beefs/"
            dst_path = "root@" + ":".join([node, self.install_dir])
            rollback_cmd = " ".join(["rsync", "-progtl", "--delete",
                                     backup_path,
                                     dst_path])
            print "rollback deploy cmd", rollback_cmd
            process = subprocess.Popen(rollback_cmd,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            out, err = process.communicate()
            return out, err, process.returncode

        if component is DATA_SERVER:
            sys.stdout.write("rollback raw data node=%s\n" % (node))
            out, err, rvalue = rollback_ds_raw_data(node)
            sys.stdout.write("rollback done node=%s out=%s err=%s\n" 
                             % (node, out, err))

            sys.stdout.write("rollback beefs deploy node=%s\n" % (node))
            out, err, rvalue = rollback_deploy(node)
            sys.stdout.write("rollback done node=%s out=%s err=%s\n" 
                             % (node, out, err))

            sys.stdout.write("rollback metadata node=%s\n" % (node))
            out, err, rvalue = rollback_metadata(node)
            sys.stdout.write("rollback done node=%s out=%s err=%s\n" 
                             % (node, out, err))
            
        elif component is META_SERVER:
            sys.stdout.write("rollback beefs deploy node=%s\n" % (node))
            out, err, rvalue = rollback_deploy(node)
            sys.stdout.write("rollback done node=%s out=%s err=%s\n" 
                             % (node, out, err))

            sys.stdout.write("rollback metadata node=%s\n" % (node))
            out, err, rvalue = rollback_metadata(node)
            sys.stdout.write("rollback done node=%s out=%s err=%s\n" 
                             % (node, out, err))

    def wait_and_start_replay(self, node, deadline, out_path, err_path):
        sys.stdout.write("wait and start node=%s\n" % (node))
        input_path = self.config.replay_input_path(node)
        cmd = " ".join(["bash", 
                        self.wait_and_replay_script_path,
                        str(deadline), self.beefs_replayer_path, input_path,
                        out_path, err_path, "&"])
        print "wait&start cmd", cmd
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

    def move_result(self, node, local_dst_path):
        out, err, rvalue = self.copy_result(node, local_dst_path)
        print "copy done", out, err, rvalue
        if rvalue == 0:
            rm_cmd = " ".join(["rm", "-r", EXP_OUT_DIR + "/*"])
            print "copy ok, removing remote data cmd", rm_cmd
            out, err, rvalue = execute(rm_cmd, node)
            print "remote rm done", out, err, rvalue

    def copy_result(self, node, local_dst_path):
        remote_path = "root@" + node + ":" + EXP_OUT_DIR
        getdata_cmd = " ".join(["scp", "-r",
                                remote_path + "/*",
                                local_dst_path])

        print "copy results cmd", getdata_cmd
        process = subprocess.Popen(getdata_cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        out, err = process.communicate()
        return out, err, process.returncode

    def copy_beefs_log(self, node, local_dst_path):
        remote_log_path = "root@" + node + ":" + self.install_dir + "/logs/beefs.log"
        getlog_cmd = " ".join(["scp",
                               remote_log_path,
                               local_dst_path + "/" + "beefs.log." + node])

        print "copy beefs.log cmd", getlog_cmd
        process = subprocess.Popen(getlog_cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        out, err = process.communicate()
        print out, err, process.returncode

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

def main(num_samples, deploy):

    def base_out_path(node, sample):
        #EXP_OUT_DIR/node.sample.random
        return os.path.join(EXP_OUT_DIR, 
                            ".".join([node, str(sample), 
                                      str(int(random.random() * 10000000))])
                           )

    queenbee_node = deploy.ms_node()
    nodes = deploy.ds_nodes()
    for sample in range(num_samples):
        sys.stdout.write("Running sample " +  str(sample) + "\n")
        for node in nodes:
            deploy.umount(node)
            deploy.stop(CLIENT, node)
            deploy.stop(DATA_SERVER, node)
            deploy.rollback(DATA_SERVER, node)

        deploy.stop(META_SERVER, queenbee_node)
        deploy.rollback(META_SERVER, queenbee_node)
 
        deploy.start(META_SERVER, queenbee_node)
        for node in nodes:
            deploy.start(DATA_SERVER, node)
            deploy.start(CLIENT, node)

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
        local_result_path = "_".join(["results", str(sample)])
        if not os.path.exists(local_result_path):
            os.mkdir(local_result_path)
        for node in nodes:
            deploy.move_result(node, local_result_path)
            deploy.copy_beefs_log(node, local_result_path)
        deploy.copy_beefs_log(queenbee_node, local_result_path)


def load_config(data):
    """ It creates a dict {ip:
                           [type, name, replay_input, backup_raw_dir,
                             backup_metadir]
        based on a file with the following format:
            ip type name replay_input backup_raw_dir backup_metadir
    """
    def component_from_name(name):
        if name == "honeybee":
            return CLIENT
        elif name == "honeycomb":
            return DATA_SERVER
        elif name == "queenbee":
            return META_SERVER

    config = {}
    for line in data:
        if not line.startswith("#"):
            tokens = line.split()
            if not len(tokens) == 6:
                raise ValueError("wrong format:%s" % line)
            ip = tokens[0]
            if ip in config:
                raise Exception("duplicated ip:%s" % ip )
            tokens[1] = component_from_name(tokens[1])
            config[ip] = tokens[1:]
    return config

if __name__ == "__main__":
    """
        We assume:
             worker node have had their clocks syncronized
             worker nodes share a remote distributed file system to get replay 
                 input data
             communication to worker nodes is made by no-pass ssh
    """
    if len(sys.argv) < 6:
        sys.stderr.write("Usage: python coordinator.py num_samples config_file mount_point beefs_dir_on_vm storage_raw_dir\n")
        sys.exit(-1)

    num_samples = int(sys.argv[1])
    config_file = sys.argv[2]
    mount_point = sys.argv[3]
    beefs_dir_vm = sys.argv[4]
    storage_raw_dir = sys.argv[5]

    with open(config_file) as config_data:
        _conf = load_config(config_data)
        sys.stdout.write(" ".join(["loaded machines", str(_conf.keys()), "\n"]))
        config = Config(_conf)

    deploy = Deploy(config, beefs_dir_vm, mount_point, storage_raw_dir)
    main(num_samples, deploy)
