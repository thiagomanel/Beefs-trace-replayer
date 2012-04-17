#!/bin/bash

# It configs worker node fstab to mount lsd NFS. It is used to store replay inputs and code. It also configures the mount point is going to be used in replay

if [ $# -ne 1 ]
then
	echo "Usage:" $0 "instance_ip_address"
	exit 1
fi

instance_ip=$1

m_point="150.165.85.161:/home /home nfs defaults 0 0"
ssh root@$instance_ip "echo $m_point >> /etc/fstab"
ssh root@$instance_ip "mount -a"

replay_m_point="150.165.85.239:/local/nfs_manel /tmp/home nfs defaults 0 0"
ssh root@$instance_ip "mkdir /tmp/home"
ssh root@$instance_ip "echo $replay_m_point >> /etc/fstab"
