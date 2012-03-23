#bash filter_and_group.sh /local/tracer/logs/jurupoca /local/tracer/processed/jurupoca

# It reads a file storing raw date file paths, one line per directory e.g 
# /local/tracer/logs/morcego
# /local/tracer/logs/mulato
# ...

raw_dir_file=$1
output_dir=$2

while read raw_dir
do
    # when raw_dir_file=/local/tracer/logs/morcego
    # machine_name=morcego
    machine_name=`basename $raw_dir`
    if [ ! -d $output_dir/$machine_name ]; then 
        mkdir -p $output_dir/$machine_name
    fi 
    bash filter_and_group.sh $raw_dir $output_dir/$machine_name
done < $raw_dir_file
