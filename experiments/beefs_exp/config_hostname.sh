#!/bin/bash

if [ $# -ne 1 ]
then   
    echo "Usage:" $0 "vm_names_file"
    exit 1
fi

vm_names_file=$1

if [ ! -f $vm_names_file ]
then
    echo "File" $vm_names_file "was not found"
    exit 1
fi

while read line
do
    ip=`echo $line | cut -d" " -f1`
    python config_hostname.py $vm_names_file $ip > $ip.hosts.tmp
    ssh -n root@$ip "cp /etc/hosts /etc/hosts.bak" > /dev/null
    scp $ip.hosts.tmp root@$ip:/etc/hosts > /dev/null
done < $vm_names_file
