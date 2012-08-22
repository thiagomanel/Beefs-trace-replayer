#!/bin/bash
# It prepares data to plot
#     1. add a column with machine name
#     2. add a column with timing police

#2011_10_21-abelhinha.clean.cut.order.load.conservative
#2011_10_21-abelhinha.clean.cut.order.load.fast

file=$1
if [ ! -f $file ]
then
    echo "File" $file "does not exist"
    exit 1
fi

cp $file $file.bak
machine=`echo $file | cut -d"." -f1 | cut -d"-" -f2`
timing_policy=`echo $file | awk -F"." '{print $NF}'`
awk -v police="$timing_policy" -v mac="$machine" '{printf("%s\t%s\t%s\t%s\n", $1, $2, police, mac); }' $file > $file.final
