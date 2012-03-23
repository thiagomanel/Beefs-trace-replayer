for file in 2011_10_14-*;
do 
  stamp=`cat $file | sort -k 1 -n | head -n2 | cut -d" " -f1`
done
