#!/bin/bash

# mounts raw storage using /dev/sda2

if [ $# -ne 2 ]
then
	echo "Usage:" $0 "instance_ip_address raw_dir"
	exit 1
fi

instance_ip=$1
raw_dir=$2

ssh root@$instance_ip "mkdir $raw_dir; mount /dev/sda2 $raw_dir"
