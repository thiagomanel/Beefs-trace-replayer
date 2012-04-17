#!/bin/bash

# It allocated a number of instances on cloudgley

if [ $# -ne 1 ]
then
	echo "Usage:" $0 "number_instances_to_allocate"
	exit 1
fi

num_instances=$1

# defining the credentials directory
EUCA_CONF_DIR="/home/thiagoepdc/.euca"

# sourcing the credentials info
. $EUCA_CONF_DIR/eucarc

# preparing keypairs for run instances
KEY=thiagoepdc_key
KEYFILE=$EUCA_CONF_DIR/$KEY.private
if [ ! -f $KEYFILE ];
then
	echo $KEY $KEYFILE
	euca-add-keypair $KEY | tee $KEYFILE
	chmod 0600 $KEYFILE
fi

# running instances
EMI=emi-43B9122D
euca-run-instances -k $KEY -t c1.medium -n $num_instances $EMI

# authorizing ssh access
euca-authorize -P tcp -p 22 -s 0.0.0.0/0 default
euca-authorize -P icmp -s 0.0.0.0/0 default
