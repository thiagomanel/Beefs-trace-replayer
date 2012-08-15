#!/bin/bash

# It copies replay scripts to VMs

if [ $# -ne 3 ]
then
	echo "Usage:" $0 "instance_ip_address src_dir dst_dir"
	exit 1
fi

instance_ip=$1
src_dir=$2
dst_dir=$3

if [ ! -d $src_dir ]
then
    echo "Directory" $src_dir "does not exist"
    exit 1
fi

ssh root@$instance_ip "mkdir $dst_dir"
scp $src_dir/* root@$instance_ip:$dst_dir/
