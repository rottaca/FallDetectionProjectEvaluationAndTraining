#!/bin/bash

# Directory for dataset
dataDir=/datenspeicher/Tausch/FallDetectionProjectRecords
# Subdirectory for unclassfied data
unclassfiedDir=unclassified
# Subdirectory for positive data
posDir=positive
# Subdireectory for negative data
negDir=negative

#window size for classifier
windowW=35
windowH=35

classfierOutputFolder=$dataDir/classifier
