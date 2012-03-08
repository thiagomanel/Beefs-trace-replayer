#!/bin/bash

filtered_data_dir=$1

if [ ! -d "$filtered_data_dir" ] ; then
    echo "filtered_data_dir={" $filtered_data_dir "} does not exist"
    exit 1
fi

bash ../sort.sh $filtered_data_dir

if [ $? -eq 0 ]; then
    find $filtered_data_dir -name "*filtered" -type f -exec rm -f '{}' \;
fi 
