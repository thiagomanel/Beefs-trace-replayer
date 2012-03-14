if [ -d "data_package" ] ; then
    rm -rf data_package
fi

mkdir -p data_package/data_setup
mkdir -p data_package/data_analysis
cp -r data/*py data/*sh data_package
cp -r data/data_setup/*sh data_package/data_setup
cp -r data/data_setup/*py data_package/data_setup
cp -r data/data_analysis/*py data_package/data_analysis
cp -r data/data_analysis/*sh data_package/data_analysis

TIME_DATE=$(date +%Y%m%d%H%M%S)
tar cvf data_package.$TIME_DATE.tar data_package
bzip2 data_package.$TIME_DATE.tar
