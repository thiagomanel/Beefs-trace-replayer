#!/bin/bash

# FIXME note we have duplicated code with stamps.sh
useconds=$1
date=`date -d @${useconds:0:10}`
echo $date
