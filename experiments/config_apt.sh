#!/bin/bash

if [ $# -ne 1 ]
then
	echo "Usage:" $0 "machine_addr"
	exit 1
fi

machine_addr=$1

ssh root@$machine_addr "sed 's/squeeze/unstable/g' /etc/apt/sources.list > /etc/apt/sources.list.new && mv /etc/apt/sources.list.new /etc/apt/sources.list"
