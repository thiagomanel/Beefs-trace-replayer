#!/bin/bash

num_samples=$1
machine_ips_file=$2
exp_remote_dir=$3
exp_tarball=$4

function exp_remove_dir_exist {
    machine_addr=$1
    remote_dir=$3
}

function install_exp_remote_dir {
    machine_addr=$1
    local_zip=$2
    remote_dir=$3
}

function pre_replay_and_wait {
    machine_addr=$1
}

for sample in `seq $num_samples`
do
    for $machine_addr in $machines
    do 
        if [ `exp_remove_dir_exist $machine_addr $remote_dir` ]; then
            install_exp_remote_dir $machine_addr $exp_tarball
        fi
    done

    for $machine_addr in $machines
    do
        pre_replay_and_wait $machine_addr
    done

    
    
done
