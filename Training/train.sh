#!/bin/bash
source setup.sh

# Parameters
# -info annotated positive samples
# -w target widht
# -h target height
# -vec output file
pushd $dataDir
mkdir -p $classfierOutputFolder
opencv_traincascade -data $classfierOutputFolder \
                    -bg "bg.txt" \
                    -vec "data.vec" \
                    -numPos `wc -l < info.dat`\
                    -numNeg `wc -l < bg.txt`\
                    -featureType LBP \
                    -numStages 12 \
                    -w $windowW \
                    -h $windowH

popd
