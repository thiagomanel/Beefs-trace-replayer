#!/bin/bash

if [ $# -ne 1 ]
then
	echo "Usage:" $0 "machine_addr"
	exit 1
fi

machine_addr=$1

ssh root@$machine_addr "apt-get update; apt-get install libstdc++5 lib32gcc1 lib32stdc++6 lib32ncurses5 libsdl1.2-dev ia32-libs"
