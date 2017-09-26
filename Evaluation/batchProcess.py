import subprocess,os,collections
import timeit
import datetime
import evaluationTools

programDir="../../build-FallDetectionProject-Desktop_Qt_5_8_0_GCC_64bit-Release/"
programName="./FallDetectionProject"
aedatFileRoot="/datenspeicher/LinuxDaten/Tausch/FallDetectionProjectRecords/Preliminary/"
outputDir="/datenspeicher/LinuxDaten/Tausch/FallDetectionProjectRecords/EvaluationOutput/"

ignoreAedatFileParts= [] #["fallingObjects"];

# Ignore classifier ?   
takePossibleFallAsTrue = False
# Parameters to be evaluated
paramSet = collections.OrderedDict()
paramSet["minSpeed"] = [x / 10.0 for x in range(5, 41, 1)]
paramSet["maxSpeed"] = [x / 10.0 for x in range(20, 46, 1)]
paramSet["fallY"] = [x for x in range(100, 171, 5)]

# Initial default parameters
defaultParams = {
    "minSpeed": 1.8, #1.8,
    "maxSpeed": 6, #4.5,
    "fallY": 115 #145
}
# Additional parameters
additionalCmdArgs=["--min", "--unfallY=110"]
# Number of optimization loops
optimizationRuns = 1


evalTools = evaluationTools.EvaluationTools(aedatFileRoot,programDir,programName,outputDir,ignoreAedatFileParts,takePossibleFallAsTrue)
optimizedParams = evalTools.evaluateParameterSet(paramSet,defaultParams,additionalCmdArgs, optimizationRuns)
print optimizedParams
