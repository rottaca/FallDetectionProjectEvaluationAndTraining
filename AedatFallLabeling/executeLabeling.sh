#!/bin/bash

dataDir=/tausch/FallDetectionProjectRecords
labelTool=../build-AedatFallLabeling-Desktop_Qt_5_8_0_GCC_64bit-Release/AedatFallLabeling


for filename in $dataDir/*.aedat; do
  labelFile="${filename%.*}.label"
  if [[ ! -f $labelFile ]]; then
    $labelTool $filename || exit 1;
  else
    echo "Label file $labelFile already exists"
  fi
done
