#fullpath here
data_dir=$1
for file in `find $data_dir -name "*" -type f ! -name "*.filtered"`
do
    cat $file | python filter_trace.py > $file.filtered
done