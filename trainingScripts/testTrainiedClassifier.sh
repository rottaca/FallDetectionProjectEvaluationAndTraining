#!/bin/bash

source setup.sh

classifiers="$dataDir/classifier/cascade.xml
            "

if [[ ! -f ./TestTraining/build/TestTraining ]]; then
  mkdir TestTraining/build
  pushd TestTraining/build
  cmake .. && make
  popd
fi

for classifier in $classifiers; do
  echo $classifier
  ./TestTraining/build/TestTraining $classifier $dataDir $@ || exit 1
done
