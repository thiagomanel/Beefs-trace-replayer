#!/bin/bash

# It copies replay scripts to VMs

if [ $# -ne 2 ]
then
	echo "Usage:" $0 "instance_ip_address out_dir"
	exit 1
fi

instance_ip=$1
out_dir=$2

ssh root@$instance_ip "mkdir $out_dir"
