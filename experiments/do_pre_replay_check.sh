#!/bin/bash

# It checks if do_pre_replay.py works properly
#
# pre_replay data format
#  /local/thiagoepdc/espadarte_nfs//home/manoelfmn/workspace/dev-0.2/.svn/entries  f       881     1319217032469221-174
#  /local/thiagoepdc/espadarte_nfs//home/manoelfmn/.java   d

if [ $# -ne 1 ]; then
    echo "Usage: $0 do_pre_replay_input"
    exit 1
fi

do_pre_replay_input=$1

if [ ! -f $do_pre_replay_input ]; then
    echo $do_pre_replay_input " does not exist. Usage: $0 do_pre_replay_input"
    exit 1
fi

echo "" > pre_replay_check.out

while read line
do
    path=`echo $line | cut -d" " -f 1`
    ftype=`echo $line | cut -d" " -f 2`

    if [ $ftype = "d" ]
    then
        if [ -d $path ]
        then
            echo $path "true" >> pre_replay_check.out  
        else
            echo $path "false" "path does not exist" >> pre_replay_check.out
        fi
    elif [ $ftype = "f" ]
    then
        if [ -f $path ]
        then
            expected_size=`echo $line | cut -d" " -f 3`
            if [ $expected_size = "None" ]
            then
                expected_size="0"
            fi 
            if [ "$expected_size" -eq "-1" ]
            then
                expected_size="0"
            fi 
            actual_size=$(stat -c%s "$path")
            if [ "$expected_size" -eq "$actual_size" ]
            then
                echo $path "true" $expected_size $actual_size >> pre_replay_check.out
            else
                echo $path "false" $expected_size $actual_size >> pre_replay_check.out
            fi
        else
            echo $path "false" "path does not exist" >> pre_replay_check.out
        fi
    else
        echo "unknow type" $line >> pre_replay_check.out
        exit 3
    fi 
done < $do_pre_replay_input

grep "false" pre_replay_check.out >/dev/null
#I didn't manage to get return codes properlys from coordinator, so I'm
#returning a string false or true. we should do process.wait() and get 
#the returncode FIXME
EXITSTATUS=$?
if [ $EXITSTATUS = "0" ]
then
    echo "false"
    exit 3
else
    echo "true"
fi
