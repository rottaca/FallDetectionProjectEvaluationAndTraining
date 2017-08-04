#!/bin/bash

source setup.sh

imageFiles="$dataDir/$posDir/*"
classifier="$classfierOutputFolder/cascade_15stages.xml"

if [[ ! -f ./TestTraining/build/TestTraining ]]; then
  mkdir TestTraining/build
  pushd TestTraining/build
  cmake .. && make
  popd
fi

for file in $imageFiles; do
  ./TestTraining/build/TestTraining $classifier $file || exit 1
done
