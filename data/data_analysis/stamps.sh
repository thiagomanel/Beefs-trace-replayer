#!/bin/bash


if [ $# -ne 1 ]; then
    echo "Usage:" $0 "workflow_file_to_process"
    exit 1
fi

file2process=$1

if [ ! -f $file2process ]
then
	echo "File"  $file2process " not found"
	exit 1
fi

function useconds {
   value=`echo $1 | cut -d"-" -f 1`
   echo $value
}


#{"args": ["/home/heitor/.bash_logout", "32768", "0"], "parents": [], "stamp": {"begin": 1318626482306287.0, "elapsed": 973}, "call": "open", "rvalue": -2, "caller": {"tid": "12782", "pid": "12782", "uid": "1324", "exec": "(bash)"}, "id": 1, "session_id": 1376, "children": []}
begin_stamp=`head -n 2 $file2process | tail -n 1 | awk -F'begin\": ' '{print $2}' | awk -F',' '{print $1}'`
end_stamp=`tail -n 1 $file2process | tail -n 1 | awk -F'begin\": ' '{print $2}' | awk -F',' '{print $1}'`

begin_useconds=`useconds $begin_stamp`
begin_date=`date -d @${begin_useconds:0:10}`

end_useconds=`useconds $end_stamp`
end_date=`date -d @${end_useconds:0:10}`

duration=`echo "scale=2;($end_useconds - $begin_useconds) / 1000000" | bc`

echo "begin:" $begin_date "end:"$end_date "duration:"$duration
