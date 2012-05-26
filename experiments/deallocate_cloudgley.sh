#!/bin/bash

# It terminates all the instances that are allocated
./instances_info.sh -id | xargs euca-terminate-instances
