#!/bin/bash

# This is command is to be run on vm machine
# It'd be better to make it as a ssh command and execute on
# head node but I do not want to block and it's boring to code
# a remote ssh comand to run on background (it needs nohup and dev/null
# redirections if you want to try)

apt-get -y update
apt-get -y upgrade
apt-get install -y rsync libjansson4 libjansson-dev  openjdk-7-jdk openjdk-7-jre
