#!/bin/bash

if [ $# -ne 1 ]
then
	echo "Usage:" $0 "machine_addr"
	exit 1
fi

machine_addr=$1

ssh root@$machine_addr "sed 's/squeeze/unstable/g' /etc/apt/sources.list > /etc/apt/sources.list.new && mv /etc/apt/sources.list.new /etc/apt/sources.list"
ssh root@$machine_addr "apt-get update ; apt-get upgrade"
ssh root@$machine_addr "apt-get install libjansson4 libjansson-dev"
#ssh root@$machine_addr "apt-get update; apt-get install libstdc++5 lib32gcc1 lib32stdc++6 lib32ncurses5 libsdl1.2-dev ia32-libs"
