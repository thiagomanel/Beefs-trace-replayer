# It reads a file storing raw date file paths, one line per directory e.g 
# /local/tracer/logs/morcego
# /local/tracer/logs/mulato
# ...

if [ $# -ne 1 ];
then
    echo "Usage: $0 processed_dir"
    exit 1
fi

processed_dir=$1

for dir in `ls -t $processed_dir`
do
    bash sort_and_remove_old_data.sh $processed_dir/$dir
done
