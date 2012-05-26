#!/bin/bash

# It copies root rsa pubkey to remote instance authorized keys. In doing so, root can make no-pass ssh to cloudgley instances

if [ $# -ne 1 ]
then
	echo "Usage:" $0 "instance_ip_address"
	exit 1
fi

instance_ip=$1

key="ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA1BSwxCJnL3yNTZnTcJ83K2JB8A8Ns/T3jhmr47OlKVfhZZ/e3iJKxBYNdwACMtXhlRnt/DziEAxEojLAR/azGIvWQcwHuyWeYvtQWt8jrfR1g4sfoq6A2tGVWrLYqVlt2gyGSfxZTUUHSDU8RdlTRtHh78spyzpB/U1BDfwzBkDmgZwvc3V3vjMSg9v4TDdzZ78N9wEWjKyPy65ckfskM5Zqmmy8CYs3nSZkx2H2jqr4l2eHx03c2gpavliLq4aLcuEXHdGUdmclRKSXmVCs7IRoXrUyfef8AXMno5/w7v6dqel6zozfThL2f9PiKxHV30g8DYeBXUmu10SEyHdAaQ== root@abelhinha"

ssh -i /home/thiagoepdc/.euca/thiagoepdc_key.private root@$instance_ip "echo $key >> /root/.ssh/authorized_keys"
