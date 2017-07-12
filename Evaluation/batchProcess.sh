#!/bin/bash
EXEC_FILE_DIR=../../build-FallDetectionProject-Desktop_Qt_5_8_0_GCC_64bit-Release/
EXEC_FILE_NAME=FallDetectionProject
AEDAT_FILE_DIR=/tausch/FallDetectionProjectRecords

TMP_FILE_NAME=/tausch/FallDetectionProjectRecords/tmp.txt
OUTPUT_FILE_NAME=/tausch/FallDetectionProjectRecords/output.txt

# Clears file
echo "filename | possible falls | delayed falls | direct falls  | proofed falls | unproofed alarms | individual timestamps (possible, delayed, direct)" > $OUTPUT_FILE_NAME

pushd $EXEC_FILE_DIR
for file in $AEDAT_FILE_DIR/*.aedat
do
  echo "----------------------------------"
  echo "Processing file $file"
  ./$EXEC_FILE_NAME $file > $TMP_FILE_NAME

  if [[ $? -eq 0 ]]; then

    directFallCnt=$(cat $TMP_FILE_NAME | grep -F "[Fall]: Directly" | wc -l)
    delayedFallCnt=$(cat $TMP_FILE_NAME | grep -F "[Fall]: Delayed" | wc -l)
    possibleFallCnt=$(cat $TMP_FILE_NAME | grep -F "[Fall]: Possibly" | wc -l)

    provedFallCnt=$(( $directFallCnt + $delayedFallCnt ))
    unprovedAlarmCnt=$(( $possibleFallCnt - $delayedFallCnt ))

    timestampsDirect=$(cat $TMP_FILE_NAME | grep -F "[Fall]: Directly" | cut -d:  -f4 | tr -d '\n' )
    timestampsDelayed=$(cat $TMP_FILE_NAME | grep -F "[Fall]: Delayed" | cut -d:  -f4 | tr -d '\n' )
    timestampsPossible=$(cat $TMP_FILE_NAME | grep -F "[Fall]: Possibly" | cut -d:  -f4 | tr -d '\n' )

    echo "Possible falls: $possibleFallCnt"
    echo "Delayed falls: $delayedFallCnt"
    echo "Direct falls: $directFallCnt"
    echo "Proofed falls: $provedFallCnt"
    echo "Unproofed alarms: $unprovedAlarmCnt"
    echo "Times: $timestampsPossible | $timestampsDelayed | $timestampsDirect"

    echo "$file $possibleFallCnt $delayedFallCnt $directFallCnt $provedFallCnt $unprovedAlarmCnt $timestampsPossible $timestampsDelayed $timestampsDirect " | tr -s ' ' >> $OUTPUT_FILE_NAME
  else
    echo "$file skipped file due to error" >> $OUTPUT_FILE_NAME
  fi
  echo "----------------------------------"

done

rm $TMP_FILE_NAME
popd
