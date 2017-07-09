#!/bin/bash

./manuallyClassify.sh
./annotatePosSamples.sh
./preprocessSamples.sh

echo "Processing of input data done!"
echo "Execute ./train.sh to start training"
