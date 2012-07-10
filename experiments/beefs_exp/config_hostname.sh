#!/bin/bash

if [ $# -ne 1 ]
then   
    echo "Usage:" $0 "replay_config_file"
    exit 1
fi

replay_config=$1

if [ ! -f $replay_config ]
then
    echo "File" $replay_config "was not found"
    exit 1
fi

while read line
do
    ip=`echo $line | cut -d" " -f1`
    new_hostname=`echo $line | cut -d" " -f3`
    python config_hostname.py $replay_config $ip > $ip.hosts.tmp
    ssh -n root@$ip "cp /etc/hosts /etc/hosts.bak" > /dev/null
    scp $ip.hosts.tmp root@$ip:/etc/hosts > /dev/null
    ssh -n root@$ip "hostname $new_hostname"
done < $replay_config
