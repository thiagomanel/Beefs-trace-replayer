import sys

# It configs vm /etc/hosts. It is supposed to work on a vm
# that has a file like this. The last 6 lines are copied and
# names and inserted before. It's very specified to the current
# images and vms i'm using right now, do not expected nothing more
# than this.
# -----------------------------------------------------------
# 127.0.0.1       localhost
#
## The following lines are desirable for IPv6 capable hosts
#::1     ip6-localhost ip6-loopback
#fe00::0 ip6-localnet
#ff00::0 ip6-mcastprefix
#ff02::1 ip6-allnodes
#ff02::2 ip6-allrouters

BASE_HOST_INFO = "\n".join(["# The following lines are desirable for IPv6 capable hosts",
                            "::1     ip6-localhost ip6-loopback",
                            "fe00::0 ip6-localnet",
                            "ff00::0 ip6-mcastprefix",
                            "ff02::1 ip6-allnodes",
                            "ff02::2 ip6-allrouters"])

def generate_hosts(ip_to_name, filter_ip):
    localhost_info = " ".join(["127.0.0.1", ip_to_name[filter_ip], "localhost"])
    others_info = "\n".join([" ".join([ip, hostname]) 
                   for ip, hostname in ip_to_name.iteritems() 
                   if not ip == filter_ip])
    return "\n".join([localhost_info, others_info, BASE_HOST_INFO])

if __name__ == "__main__":
    vm_names_path = sys.argv[1]
    selected_ip = sys.argv[2]
    with open(vm_names_path) as vm_names:
        ip_to_name = {}
        for vm_info in vm_names:
            vm_ip, vm_name = vm_info.split()
            ip_to_name[vm_ip] = vm_name
        sys.stdout.write(generate_hosts(ip_to_name, selected_ip))
