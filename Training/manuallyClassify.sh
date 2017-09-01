#!/bin/bash
source setup.sh

pushd $dataDir

fileNrPos=`ls -l $posDir | wc -l`
fileNrPos=$(expr $fileNrPos - 1)
fileNrNeg=`ls -l $negDir | wc -l`
fileNrNeg=$(expr $fileNrNeg - 1)

echo "Already found positive samples: $fileNrPos"
echo "Already found negative samples: $fileNrNeg"

for filename in $unclassfiedDir/*.png; do
  if [ -f $filename ]; then
    eog $filename || exit 1
    # Repead if invalid input
    while : ; do
      echo "Is this a posiitve or negative sample (p/n)?"
      read class
      # Valid answer?
      if [[ $class == *"p"* ]] || [[ $class == *"n"* ]]; then
          break;
      fi
    done

    if [[ $class == *"p"* ]]; then
      mv $filename $posDir/pos$fileNrPos.png
      fileNrPos=$(expr $fileNrPos + 1)
    elif [[ $class == *"n"* ]]; then
      mv $filename $negDir/neg$fileNrNeg.png
      fileNrNeg=$(expr $fileNrNeg + 1)
    fi
  fi
done

popd
