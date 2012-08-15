import os
import sys
import json
import subprocess
from beefs_bootstrapper import *

def main(boot_data_path, osd_hostname, dst_dir, src_hostname):
    """ It stages stos held to a specified osd into a local directory.
        Args:
            boot_data_path (str) - path to boot data
            osd_hostname (str) - all stos held by this osd_hostname, as defined
                                 on boot_data, will be staged.
            dst_dir (str) - path to stage-in dst dir.
            src_hostname (str) - hostname where data is stored.
    """
    def stage_in(src, dst):
        #both src and dst are hostname:/path strings
        process = subprocess.Popen(["scp", src, dst],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
        out, err = process.communicate()
        return out, err, process.returncode

    def sto_and_remote_path_by_hostname(boot_data, hostname):
        """
            It gives a collection of (sto_id, remove_path) held by an osd with a
            given hostname.
            Args:
                 boot_data
                 hostname
        """
        def replica_by_hostname(group, hostname):
            replicas_by_osdid = group.replicas_by_osdid()
            for osd_id in replicas_by_osdid.keys():
                if osd_id.hostname == hostname:
                   return replicas_by_osdid[osd_id]
            return []

        sto_and_path = []
        for line in boot_data:
            entry = Entry.from_json(json.loads(line, encoding="ISO-8859-1"))
            if not entry.is_dir():
                replicas = replica_by_hostname(entry.group, hostname)
                for replica in replicas:
                    sto_and_path.append((replica.sto_id, entry.fullpath))

        return sto_and_path

    with open(boot_data_path) as boot_data:
        for sto_id, remote_path in \
                sto_and_remote_path_by_hostname(boot_data, osd_hostname):

            safe_remote_path = "\"" + remote_path + "\""
            src = ":".join([src_hostname, safe_remote_path])
            dst = os.path.join(dst_dir, sto_id)
            out, err, ret = stage_in(src, dst)
            if out: sys.stdout.write(out)
            if err: sys.stderr.write(err)

if __name__ == "__main__":
    boot_data_path = sys.argv[1]
    boot_osd_id_to_stage = sys.argv[2]
    dst_dir = sys.argv[3]
    src_server = sys.argv[4]
    main(boot_data_path, boot_osd_id_to_stage, dst_dir, src_server)
