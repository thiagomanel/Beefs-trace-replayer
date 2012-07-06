#!/bin/bash

# It changes beefs config.

# deploy_config pattern
#
# honeybee.conf filesystem=localhost:8891 prop_one=value_one prop_two=value_two
# queenbee.conf prop_one=value_one prop_two=value_two
# honeycomb.conf prop_one=value_one prop_two=value_two

if [ $# -ne 2 ]
then
    echo "Usage:" $0 "beefs_dir" "deploy_config_file"
    exit 1
fi

beefs_dir=$1
deploy_config=$2

if [ ! -d $beefs_dir ]
then
    echo "beefs dir" $beefs_dir "not found"
    exit 1
fi

if [ ! -f $deploy_config ]
then
    echo "deploy config file" $deploy_config "not found"
    exit 1
fi

function replace {
    local file=$1
    local str_to_replace=$2
    
    local key=`echo $str_to_replace | cut -d"=" -f1`
    local new_value=`echo $str_to_replace | cut -d"=" -f2`

    local old_value=`grep $key $file | cut -d"=" -f2`

    sed "s/${key}=${old_value}/${key}=${new_value}/g" $file > $file.new && mv $file.new $file
}

while read line
do
    #beefconf_path=`path $line`
    beefconf_path=`echo $line | cut -d" " -f1`
    props=`echo $line | cut -d" " -f2-`
    for prop in $props
    do
        replace $beefs_dir/conf/$beefconf_path $prop
    done
done < $deploy_config
