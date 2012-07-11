#!/bin/bash

# this script is supposed to run in espadarte
> osd.map
chmod 666 osd.map
sudo python generate_boot_data.py /local/thiagoepdc/beefs_backup/ 3 osd.map > boot.out 2> boot.err
