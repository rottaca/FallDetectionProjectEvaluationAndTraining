#!/bin/bash

source setup.sh

classifier="$classfierOutputFolder/cascade.xml"

if [[ ! -f ./TestTraining/build/TestTraining ]]; then
  mkdir TestTraining/build
  pushd TestTraining/build
  cmake .. && make
  popd
fi

./TestTraining/build/TestTraining $classifier $@ || exit 1
