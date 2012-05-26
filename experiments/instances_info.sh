#!/bin/bash

option=$1
case "$option" in
    -ip) euca-describe-instances | grep INSTANCE | cut -f4
         ;;
    -id) euca-describe-instances | grep INSTANCE | cut -f2
         ;;
    -status) euca-describe-instances | grep INSTANCE | cut -f2,4,6
         ;;
    *) echo "Invalid option! Usage: $0 -ip -id -status"
         exit 1
         ;;
esac
