#!/bin/bash

back_trace_out=$1
out_dir=`dirname $back_trace_out`

out_collapsed=$out_dir/collapsedbt.`basename $back_trace_out`
./stackcollapse-stap.pl $back_trace_out > $out_collapsed

out_plot=$out_dir/flame.`basename $back_trace_out`
./flamegraph.pl $out_collapsed > $out_plot
