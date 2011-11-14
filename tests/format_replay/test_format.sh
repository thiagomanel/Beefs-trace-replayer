replay_inputfile=$1
output_msg="Testing replay formatting - \t"

if [ $# -ne 1 ]
then
    echo "Usage: " $0 " replayinputfile"
    exit 1
fi

if [[ ! -f $replay_inputfile ]]
then
    echo "file " $replay_inputfile " does not exist"
    exit 1
fi

# cleaning state
echo "empty" > formatted_output
python format_replayinput.py $replay_inputfile formatted_output
cmp expected_formatted_replay formatted_output
if [[ $? -eq 0 ]]
then
    echo -e $output_msg " OK"
else
    echo -e $output_msg " FAILED"
fi
