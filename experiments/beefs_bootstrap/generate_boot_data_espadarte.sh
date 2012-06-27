#!/bin/bash

# this script is supposed to run in espadarte
> osd.map
chmod 666 osd.map
sudo python generate_boot_data.py /local/nfs_manel/ 3 osd.map /local/nfs_manel/antonio /local/nfs_manel/edigley /local/nfs_manel/isabellylr /local/nfs_manel/joseamaf /local/nfs_manel/suporte /local/nfs_manel/tiagohsl /local/nfs_manel/tmp > boot.out 2> boot.err
