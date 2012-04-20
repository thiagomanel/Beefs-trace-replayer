#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 processed_dir_root"
    exit 1
fi

processed_dir_root=$1

if [ ! -d $processed_dir_root ]; then
    echo $processed_dir_root " does not exist. Usage: $0 processed_dir_root"
    exit 1
fi

# It cleans any processed data out withing a directory. Processed data
# follows this pattern:
# /mnt/backup_storage3/pepino/20111014/2011_10_14-pepino
# /mnt/backup_storage3/pepino/20111021/2011_10_21-pepino
# /mnt/backup_storage3/pepino/20111019/2011_10_19-pepino


for machine_dir in `ls -t $processed_dir_root`
do
    machine_name=`basename $machine_dir`
    processed_files=`find $processed_dir_root -type f -name "*$machine_name"`
    for file in $processed_files
    do
        python ../clean_trace.py < $file > $file.clean 2> $file.clean.err
    done
done

python ../clean_trace.py 1319220000000000 1319220600000000 < /local/tracer/processed/abelhinha/20111021/2011_10_21-abelhinha > /local/tracer/processed/abelhinha/20111021/2011_10_21-abelhinha.clean.cut 2> /local/tracer/processed/abelhinha/20111021/2011_10_21-abelhinha.clean.cut.err
python ../clean_trace.py 1319220000000000 1319220600000000 < /local/tracer/processed/bandeira/20111021/2011_10_21-bandeira > /local/tracer/processed/bandeira/20111021/2011_10_21-bandeira.clean.cut 2> /local/tracer/processed/bandeira/20111021/2011_10_21-bandeira.clean.cut.err
python ../clean_trace.py 1319220000000000 1319220600000000 < /local/tracer/processed/celacanto/20111021/2011_10_21-celacanto > /local/tracer/processed/celacanto/20111021/2011_10_21-celacanto.clean.cut 2> /local/tracer/processed/celacanto/20111021/2011_10_21-celacanto.clean.cut.err
python ../clean_trace.py 1319220000000000 1319220600000000 < /local/tracer/processed/charroco/20111021/2011_10_21-charroco > /local/tracer/processed/charroco/20111021/2011_10_21-charroco.clean.cut 2> /local/tracer/processed/charroco/20111021/2011_10_21-charroco.clean.cut.err
python ../clean_trace.py 1319220000000000 1319220600000000 < /local/tracer/processed/cherne/20111021/2011_10_21-cherne > /local/tracer/processed/cherne/20111021/2011_10_21-cherne.clean.cut 2> /local/tracer/processed/cherne/20111021/2011_10_21-cherne.clean.cut.err
python ../clean_trace.py 1319220000000000 1319220600000000 < /local/tracer/processed/gupi/20111021/2011_10_21-gupi > /local/tracer/processed/gupi/20111021/2011_10_21-gupi.clean.cut 2> /local/tracer/processed/gupi/20111021/2011_10_21-gupi.clean.cut.err
python ../clean_trace.py 1319220000000000 1319220600000000 < /local/tracer/processed/jurupoca/20111021/2011_10_21-jurupoca > /local/tracer/processed/jurupoca/20111021/2011_10_21-jurupoca.clean.cut 2> /local/tracer/processed/jurupoca/20111021/2011_10_21-jurupoca.clean.cut.err
python ../clean_trace.py 1319220000000000 1319220600000000 < /local/tracer/processed/mulato/20111021/2011_10_21-mulato > /local/tracer/processed/mulato/20111021/2011_10_21-mulato.clean.cut 2> /local/tracer/processed/mulato/20111021/2011_10_21-mulato.clean.cut.err
python ../clean_trace.py 1319220000000000 1319220600000000 < /local/tracer/processed/mussum/20111021/2011_10_21-mussum > /local/tracer/processed/mussum/20111021/2011_10_21-mussum.clean.cut 2> /local/tracer/processed/mussum/20111021/2011_10_21-mussum.clean.cut.err
python ../clean_trace.py 1319220000000000 1319220600000000 < /local/tracer/processed/ourico/20111021/2011_10_21-ourico > /local/tracer/processed/ourico/20111021/2011_10_21-ourico.clean.cut 2> /local/tracer/processed/ourico/20111021/2011_10_21-ourico.clean.cut.err
