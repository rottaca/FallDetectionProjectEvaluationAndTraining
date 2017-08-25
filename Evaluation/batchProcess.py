import subprocess,os,collections
import timeit
import datetime
import evaluationTools

programDir="../../build-FallDetectionProject-Desktop_Qt_5_8_0_GCC_64bit-Release/"
programName="./FallDetectionProject"
aedatFileRoot="/tausch/FallDetectionProjectRecords/Preliminary/"
outputDir="/tausch/FallDetectionProjectRecords/EvaluationOutput/"

ignoreAedatFileParts= [] #["fallingObjects"];

# Ignore classifier ?
takePossibleFallAsTrue = False
# Parameters to be evaluateds
paramSet = collections.OrderedDict()
paramSet["minSpeed"] = [x / 10.0 for x in range(15, 41, 1)]
paramSet["maxSpeed"] = [x / 10.0 for x in range(30, 81, 1)]

# Initial default parameters
defaultParams = {
    "minSpeed": 3.2,
    "maxSpeed": 10
}
# Additional parameters
additionalCmdArgs=["--min"]
# Number of optimization loops
optimizationRuns = 1


evalTools = evaluationTools.EvaluationTools(aedatFileRoot,programDir,programName,outputDir,ignoreAedatFileParts,takePossibleFallAsTrue)
optimizedParams = evalTools.evaluateParameterSet(paramSet,defaultParams,additionalCmdArgs, optimizationRuns)
print optimizedParams
