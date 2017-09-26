import subprocess,os,collections
import timeit
import datetime
import evaluationTools
import sys

programDir="../../build-FallDetectionProject-Desktop_Qt_5_8_0_GCC_64bit-Release/"
programName="./FallDetectionProject"
aedatFileRoot="/datenspeicher/LinuxDaten/Tausch/FallDetectionProjectRecords/Preliminary/"
outputDir="/datenspeicher/LinuxDaten/Tausch/FallDetectionProjectRecords/EvaluationOutput"

ignoreAedatFileParts= [] #["fallingObjects"];

# Ignore classifier ?
takePossibleFallAsTrue = False

if len(sys.argv[1:]) == 0:
  print "No additional parameters were set, defaults are used!"

# Additional parameters
additionalCmdArgs=[str(i) for i in sys.argv[1:]]#["--max", "--minSpeed=2.5", "--maxSpeed=5"]

print "Opening " + outputDir + "/FinalFallSpeedAndVerticalPosition.txt"
f=open(outputDir + "/FinalFallSpeedAndVerticalPosition.txt","w")
print "Opening " + outputDir + "/FinalClassificationPerFile.txt"
f2=open(outputDir + "/FinalClassificationPerFile.txt","w")

evalTools = evaluationTools.EvaluationTools(aedatFileRoot,programDir,programName,outputDir,ignoreAedatFileParts,takePossibleFallAsTrue)
evalTools.timing_exec_count = len(evalTools.datFiles)
CASum, FASum, CRSum, FRSum = evalTools.evaluateProgWithParams(additionalCmdArgs,classificationResultFileHandle=f2,fallInfoFileHandle=f)

f.close()
f2.close()
