
for file in 2011_10_14 2011_10_15 2011_10_16 2011_10_17 2011_10_18 2011_10_19 2011_10_20 2011_10_21 ;
do
    R --slave --args $file < plot.r
done