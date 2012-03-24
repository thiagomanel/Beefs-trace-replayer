for file in `ls $1/*order`
do
    ./beefs_replayer $file > $file.replay.out 2> $file.replay.out.err &
done
