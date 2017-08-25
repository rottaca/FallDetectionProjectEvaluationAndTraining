import subprocess,os,collections
import timeit
import datetime
import evaluationTools
import sys

programDir="../../build-FallDetectionProject-Desktop_Qt_5_8_0_GCC_64bit-Release/"
programName="./FallDetectionProject"
aedatFileRoot="/tausch/FallDetectionProjectRecords/Preliminary/"
outputDir="/tausch/FallDetectionProjectRecords/EvaluationOutput/"

ignoreAedatFileParts= [] #["fallingObjects"];

# Ignore classifier ?
takePossibleFallAsTrue = False

# Additional parameters
additionalCmdArgs=[str(i) for i in sys.argv[1:]]#["--max", "--minSpeed=2.5", "--maxSpeed=5"]

f=open("FallInfo.txt","w")

evalTools = evaluationTools.EvaluationTools(aedatFileRoot,programDir,programName,outputDir,ignoreAedatFileParts,takePossibleFallAsTrue)
evalTools.timing_exec_count = len(evalTools.datFiles)
CASum, FASum, CRSum, FRSum = evalTools.evaluateProgWithParams(additionalCmdArgs,fallInfoFileHandle=f)

f.close()
