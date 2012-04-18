#!/bin/bash

if [ $# -ne 1 ]
then
	echo "Usage:" $0 "machine_address"
	exit 1
fi

machine_addr=$1

ssh root@$machine_addr "ntpdate ntp.pop-pb.rnp.br"
