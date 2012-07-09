#!/bin/bash

# vm_names_file format
# ip hostname

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
    new_hostname=`echo $line | cut -d" " -f2`
    python config_hostname.py $vm_names_file $ip > $ip.hosts.tmp
    ssh -n root@$ip "cp /etc/hosts /etc/hosts.bak" > /dev/null
    scp $ip.hosts.tmp root@$ip:/etc/hosts > /dev/null
    ssh -n root@$ip "hostname $new_hostname"
done < $vm_names_file
