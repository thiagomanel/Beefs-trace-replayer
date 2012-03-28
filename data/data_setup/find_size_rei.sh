#!/bin/bash

# It cleans any processed data out withing a directory. Processed data
# follows this pattern:
# /mnt/backup_storage3/pepino/20111014/2011_10_14-pepino
# /mnt/backup_storage3/pepino/20111021/2011_10_21-pepino
# /mnt/backup_storage3/pepino/20111019/2011_10_19-pepino

#machines="abelhinha bandeira celacanto charroco cherne gupi jurupoca morcego mulato mussum ourico palmito"
machines="abelhinha celacanto charroco cherne mulato mussum"
processed_dir="/local/tracer/processed"

for machine in $machines
do
    filename="2011_10_21-${machine}"
    python ../pre_replay.py /local/thiagoepdc/espadarte_nfs/ -f ~/processed_24marc/$filename.clean.cut.pidfid_order > ~/processed_24marc/$filename.clean.cut.pidfid_order.to_create 2> ~/processed_24marc/$filename.clean.cut.pidfid_order.to_create.err
    python ../pre_replay.py /local/thiagoepdc/espadarte_nfs/ -s ~/processed_24marc/$filename.clean.cut.pidfid_order.to_create $processed_dir/$machine/20111021/$filename.join ~/processed_24marc/$filename.clean.cut.pidfid_order > ~/processed_24marc/$filename.clean.cut.pidfid_order.pre_replay 2> ~/processed_24marc/$filename.clean.cut.pidfid_order.pre_replay.err

    echo $filename " #to_create " `cat ~/processed_24marc/$filename.clean.cut.pidfid_order.to_create | wc -l` " #pre_replay " `cat ~/processed_24marc/$filename.clean.cut.pidfid_order.pre_replay | wc -l`
done
