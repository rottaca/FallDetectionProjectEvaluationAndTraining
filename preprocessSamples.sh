#!/bin/bash
source setup.sh

pushd $dataDir

# Parameters
# -info annotated positive samples
# -w target widht
# -h target height
# -vec output file
opencv_createsamples -info info.dat -w $windowW -h $windowH -vec data.vec -num `wc -l < info.dat` || exit 1

# Create bg.txt
ls $negDir -1 > bg.txt  || exit 1
# Add folder prefix to each line
sed -i -e "s/^/$negDir\//" bg.txt  || exit 1


popd
