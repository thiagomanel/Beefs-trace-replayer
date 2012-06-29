import os
import sys
import json
import subprocess

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
        subprocess.Popen(" ".join(["scp", src, dst]),
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
        out, err = process.communicate()
        return out, err, process.returncode

    def filter_by_hostname(boot_data, hostname):
        filtered_stos = []
        for line in boot_data:
            entry = Entry.from_json(json.loads(line, encoding="ISO-8859-1"))
            allreplicas = [entry.group.replicas]
            allreplicas.append(entry.group.primary)
            filtered_stos.extend([replica.sto_id for replica in allreplicas
                                                 if replica.osd_id == hostname])
        #we cannot have duplicates, but it's safer to remove them
        return set(filtered_stos)

    with open(boot_data_path) as boot_data
        for sto_id, remote_path in filter_by_hostname(boot_data, osd_hostname):
            src = "@".join([src_hostname, remote_path])
            dst = "@".join(["localhost", os.path.join(dst_dir, sto_id)]) 
            stage_in(sto_id, remote_path, dst_dir)

if __name__ == "__main__":
    boot_data_path = sys.argv[1]
    boot_osd_id_to_stage = sys.argv[2]
    dst_dir = sys.argv[3]
    src_server = sys.argv[4]
    main(boot_data_path, boot_osd_id_to_stage, dst_dir, src_server)
