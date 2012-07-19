import sys

SEC_TO_USEC= 1000000

def elapsed_millis(begin_sec, begin_usec, end_sec, end_usec):
    return ((end_sec * SEC_TO_USEC + end_usec) - 
                       (begin_sec * SEC_TO_USEC + begin_usec))

if __name__ == "__main__":
    """ It converts replayer output to ease plotting:
        plotting data input format:
        operation_type\tlatency\tactual_rvalue

        Usage: python transform_output.py workflow_ops replay_output > output
        
        format workflow_ops
                operation_type rvalue
    """
    workflow_ops_path = sys.argv[1]#it starts by real operation
    replay_out_path = sys.argv[2]#it starts by fake root it

    with open(workflow_ops_path) as workflow_ops:
        with open(replay_out_path) as replay_out:
            replay_out.readline()#excluding fake root
            for op_line in workflow_ops:
                operation_type, rvalue = op_line.split()
                begin_secs, begin_usec, end_sec, end_usec, delay,\
                    exp_rvalue, actual_rvaluec = replay_out.readline().split()

                elapsed = elapsed_millis(long(begin_secs), long(begin_usec),\
                                     long(end_sec), long(end_usec))
                sys.stdout.write("\t".join([operation_type, str(elapsed),
                                            str(actual_rvaluec)]) + "\n")
