#!/bin/bash

# It cleans any processed data out withing a directory. Processed data
# follows this pattern:
# /mnt/backup_storage3/pepino/20111014/2011_10_14-pepino
# /mnt/backup_storage3/pepino/20111021/2011_10_21-pepino
# /mnt/backup_storage3/pepino/20111019/2011_10_19-pepino

#1319217000000000 10 13 ('stuart', 20L) ('charroco', 2371L) ('abelhinha', 89518L) ('mussum', 2273L) ('sargento', 5548L) ('cherne', 30205L) ('mulato', 20598L) ('pepino', 7282L) ('traira', 15076L) ('roncador', 256L) ('pitu', 10876L) ('celacanto', 118855L) ('ourico', 70L)
#Fri Oct 21 14:10:00 BRT 2011
#pepino  pimpim  pitu  roncador  sargento  stuart  surubim  traira  viola

#these are machines with high load at 1319217000000000 timestamp
machines="sargento traira viola stuart pitu pepino roncador"
processed_dir="/mnt/backup_storage3/processed"

#so, i'm lasy, as our cut is at 2011 oct 21, it's hardcoded below
for machine in $machines
do
    #from Fri Oct 21 14:11:00 BRT 2011 to Fri Oct 21 14:20:00 BRT 2011
    python ../clean_trace.py 1319217000000000 1319217600000000 < $processed_dir/$machine/20111021/2011_10_21-$machine > $processed_dir/$machine/20111021/2011_10_21-$machine.clean.cut 2> $processed_dir/$machine/20111021/2011_10_21-$machine.clean.cut.err
done
