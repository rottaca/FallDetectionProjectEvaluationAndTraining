#!/bin/bash
source setup.sh

pushd $dataDir

# Parameters
# --annotations Output file name for annotated positive samples
# --images Input images

# Controls
# c confirm annotations
# d delete last annotation
# n continue to next image
# ESC exit programm

if [ -f info.dat ]; then
  posTmpDir="$posDir"_tmp
  echo "Create tmp dir: $posTmpDir"
  mkdir $posTmpDir  || exit 1
  files_to_move=$(cat info.dat | awk -F ' ' '{ print $1 }')
  echo "Move already classified files to tmp dir"
  mv $files_to_move $posTmpDir  || exit 1

  echo "Annotate remaining images"
  opencv_annotation --annotations=info.dat_tmp --images=$posDir  || exit 1
  cat info.dat_tmp >> info.dat && rm info.dat_tmp || exit 1 # Concat files

  mv $posTmpDir/* $posDir || exit 1
  rm -rf $posTmpDir || exit 1
else
  opencv_annotation --annotations=info.dat --images=$posDir || exit 1
fi
popd
