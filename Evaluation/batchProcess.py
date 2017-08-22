import subprocess,os,collections
import timeit
import datetime

programDir="../../build-FallDetectionProject-Desktop_Qt_5_8_0_GCC_64bit-Release/"
programName="./FallDetectionProject"
aedatFileRoot="/tausch/FallDetectionProjectRecords/Preliminary/"
outputDir="/tausch/FallDetectionProjectRecords/EvaluationOutput/"

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



timing_exec_count = 0
timing_already_processed_count = 0
startTime = timeit.default_timer()

def findAeDatFiles(aedatFileRoot):
    #Finding all aedat files
    aedatFilePathes=[]
    for path, subdirs, files in os.walk(aedatFileRoot):
        for name in files:
            if os.path.splitext(name)[1] == ".aedat":
                full_path=os.path.join(path, name)
                aedatFilePathes.append(full_path)
    aedatFilePathes = aedatFilePathes

    print "Found " + str(len(aedatFilePathes)) + " aedat files for evaluation."
    return aedatFilePathes

class Fall:
    def __init__(self):
        self.direct = False
        self.delayed = False
        self.onlyPossible = False
        self.timestamp = -1
    def __str__(self):
        output = ""
        if self.direct:
            output+= "direct fall"
        if self.delayed:
            output+= "delayed fall"
        if self.onlyPossible:
            output+= "only possible fall"
        output += " ,timestamp: " + str(self.timestamp)
        return output
    def __repr__(self):
        return self.__str__()

class TrackedObj:
    def __init__(self,id):
        self.falls = []
        self.id = id

    def __str__(self):
        output="[" + str(self.id) + "]: \n"
        for fall in self.falls:
            output+= fall.__str__() + "\n"

        return output

    def __repr__(self):
        return self.__str__()

    def countPossible(self):
        cnt = 0
        for fall in self.falls:
            if fall.onlyPossible == True:
                cnt+=1
        return cnt

    def countDirect(self):
        cnt = 0
        for fall in self.falls:
            if fall.direct == True:
                cnt+=1
        return cnt

    def countDelayed(self):
        cnt = 0
        for fall in self.falls:
            if fall.delayed == True:
                cnt+=1
        return cnt

    def getFalls(self):
        return self.falls

    def newEvent(self, type, time):
        if "direct" == type:
            fall = Fall()
            fall.timestamp = time
            fall.direct = True
            self.falls.append(fall)
        elif "delayed" == type:
            if len(self.falls) == 0:
                print "unexpected state 1"
                exit(1)
            elif self.falls[-1].onlyPossible:
                self.falls[-1].onlyPossible = False
                self.falls[-1].delayed = True
        elif "possible" == type:
            fall = Fall()
            fall.timestamp = time
            fall.onlyPossible = True
            self.falls.append(fall)
        else:
            print "unexpected type"
            exit(1)


def executeProgAndParseOutput(cmdArgs,aedatFilePath):
    print "File: " + aedatFilePath
    command=[]
    command.extend(cmdArgs)
    command.insert(0,programName)
    command.append(aedatFilePath)

    #print "Starting programm: " + programName
    #print "With parameters: " + " ".join( str(x) for x in commandArgs)
    #print "Full command: " + " ".join( str(x) for x in command)
    while True:
        process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()

        # Get programm output
        out, err = process.communicate()

        # Check for errors
        if process.returncode != 0:
            print "Non-zero return code: " + str(process.returncode)
            print err
            print out
            #exit(1)
    	else:
	    break

    # Analize programm output
    lines = out.splitlines()

    # Extract falltype and timestamp
    detectedFallsById = {}

    for line in lines:
        if "[Fall]:" in line:

            objID = line.split(",")[0]

            type = ""
            if "[Fall]: Delayed" in line:
                type="delayed"
            elif "[Fall]: Directly" in line:
                type="direct"
            elif "[Fall]: Possibly" in line:
                type="possible"

            # extract time
            timestamp = line.split("Time: ")[1]

            if objID not in detectedFallsById:
                detectedFallsById[objID] = TrackedObj(objID)
            # Process new event
            detectedFallsById[objID].newEvent(type, timestamp)

    return detectedFallsById

class Labels:
    def __init__(self):
        self.falls = []
        self.foundFalls = []
    def addFall(self,times):
        assert len(times) == 4
        self.falls.append(times)
    def resetFoundFalls(self):
        self.foundFalls = []
    def isValidFalltime(self,time):
        i=0
        for fall in self.falls:
            # Valid fall ?
            if time >= fall[0] and time <= fall[3]:
                # Already detected ?
                if i in foundFalls:
                    return -1
                else:
                    foundFalls.append(i)
                    return 1
            i+=1
        return 0

    def getLen(self):
        return len(self.falls)

    def __str__(self):
        output = ""
        for fall in self.falls:
            output += str(fall) + "\n"

        return output

    def __repr__(self):
        return self.__str__()

def importLabelFile(aedatFilePath):
    pre, oldExt = os.path.splitext(aedatFilePath)
    labelFileName = pre + ".label"

    labelFile = Labels()
    if os.path.isfile(labelFileName):
        lines = open(labelFileName).read().splitlines()
        for line in lines:
            labelFile.addFall(line.split(";"))

    return labelFile

def evaluateProgWithParams(cmdArgs, aedatFilePathes,classificationResultFileHandle):

    global timing_exec_count
    global timing_already_processed_count
    global startTime

    FRSum = 0
    FASum = 0
    CASum = 0
    CRSum = 0

    # Execute programm in its directory
    origWD = os.getcwd() # remember our original working directory
    os.chdir(programDir)
    idx = 0
    for aedatFilePath in aedatFilePathes:
        FRSumOld = FRSum
        FASumOld = FASum
        CASumOld = CASum
        CRSumOld = CRSum

        detectedFallsById = executeProgAndParseOutput(cmdArgs,aedatFilePath)
        labels = importLabelFile(aedatFilePath)
        print "Labels:"
        print(labels)
        print "Detected falls:"
        print(detectedFallsById)

        if len(detectedFallsById) == 0:
            print "Nothing detected"
            if labels.getLen() > 0:
                FRSum += labels.getLen()
            else:
                CRSum += 1
        else:
            # Check if there is a valid fall
            # for each object
            labels.resetFoundFalls()
            for objId in detectedFallsById:
                # Check each fall
                falls = detectedFallsById[objId].getFalls()
                for fall in falls:
                    if fall.onlyPossible and not takePossibleFallAsTrue:
                        continue
                    res = labels.isValidFalltime(fall.timestamp)
                    if res == 1:
                        CASum += 1
                    else:
                        FASum += 1

        print "------------- summary --------------"
        tmp = ""
        for a in cmdArgs:
            tmp += a + " "
        print "Args:              " + tmp
        print "------------------------------------"
        print "CA:                " + str(CASum)
        print "CR:                " + str(CRSum)
        print "FA:                " + str(FASum)
        print "FR:                " + str(FRSum)
        print "------------------------------------"
        print "Sum N:             " + str(FASum+CRSum)
        print "Sum P:             " + str(CASum+FRSum)
        print "------------------------------------"
        print "Elapsed time:      " + str(datetime.timedelta(seconds=(timeit.default_timer()-startTime)))
        timing_already_processed_count+=1
        scaling = (timing_exec_count-timing_already_processed_count)/timing_already_processed_count
        print "Remaining time:    " + str(datetime.timedelta(seconds=(timeit.default_timer()-startTime)*scaling))
        print "------------------------------------"
        print "Progress (files):  " + str(100.0*(idx+1)/len(aedatFilePathes)) + " %"
        print "Progress (global): " + str(100.0*(timing_already_processed_count)/timing_exec_count) + " %"
        idx+=1

        classificationResultFileHandle.write(aedatFilePath + ";")
        classificationResultFileHandle.write(str(CASum-CASumOld) + ";")
        classificationResultFileHandle.write(str(CRSum-CRSumOld) + ";")
        classificationResultFileHandle.write(str(FASum-FASumOld) + ";")
        classificationResultFileHandle.write(str(FRSum-FRSumOld))
        classificationResultFileHandle.write("\n")
        classificationResultFileHandle.flush()

    os.chdir(origWD) # get back to our original working directory

    print "----------------------------------"
    print "------------ Results -------------"
    print "Correct accepted: " + str(CASum)
    print "False accepted:   " + str(FASum)
    print "Correct rejected:  " + str(CRSum)
    print "False rejected:    " + str(FRSum)
    print "Test cases (P/N):   " + str(CASum + FASum + CRSum + FRSum) + " ("+ str(CASum+FRSum) + "/"+ str(FASum+CRSum)  +")"

    return CASum, FASum, CRSum, FRSum

def computeScore(CA,CR,FA,FR):
    if CA+FR > 0:
        sensitivity = float(CA)/(CA+FR)
    else:
        sensitivity = 0
    if CR+FA > 0:
        specificity = float(CR)/(CR+FA)
    else:
        specificity = 0
    # Youden's index
    return sensitivity + specificity - 1

def evaluateParameterRange(paramName, valueList, aedatFilePathes, addParams, outFileSuffix):
    global timing_already_processed_count
    global timing_exec_count
    global outputDir

    headerStr = "Samples: "+ str(len(aedatFilePathes)) + ", Param: \"" + paramName + "\", Values: "
    for i in valueList:
        headerStr += str(i) + ", "
    headerStr=headerStr[:-2]
    headerStr += "\n"
    paramValuesOutFileName = outputDir + "/" + paramName + "_" + outFileSuffix + ".txt"
    skippedValueCnt = 0
    # Check if file exists (backup) and continue with next value
    if os.path.isfile(paramValuesOutFileName):
        paramValuesHandle = open(paramValuesOutFileName,"a+")

        # Read text from file
        lines = paramValuesHandle.readlines()
        # Header has to be equal
        if lines[0] != headerStr:
            print "Invalid output file found: " + paramValuesOutFileName
            print "Expected header:"
            print headerStr
            exit(1)
        # Count number of already processed values
        skippedValueCnt = len(lines)-1
        print "Output file found! Contains already " + str(skippedValueCnt) + " parameter value(s)."
        # Update numer of required executions
        timing_exec_count -= skippedValueCnt*len(aedatFilePathes)
        valueList = valueList[skippedValueCnt:]
        print "Remaining values to be processed:"
        print(valueList)
    else:
        # File does not exist, create a new one and write the header
        paramValuesHandle = open(paramValuesOutFileName,"w")
        paramValuesHandle.write(headerStr)
        paramValuesHandle.flush()

    # For all parameters, evaluate program
    results = []
    # Load results from already processed values from file
    for i in range(0,skippedValueCnt):
        tmp = lines[i+1][:-1].split(";")
        CA, CR, FA, FR = [float(i) for i in tmp[1:5]]

        score = computeScore(CA, CR, FA, FR)
        results.append([tmp[0], score])
    # Continue with remaining values
    for v in valueList:
        args = []
        args.extend(addParams)
        args.append("--" + paramName + "=" + str(v))
        print "Parameters:"
        print(args)

        classificationResultFileName = outputDir + "/" + "classification_" +  paramName + "_" + str(v) + "_" + outFileSuffix + ".txt"
        classificationResultFileHandle = open(classificationResultFileName,"w")
        tmp = ""
        for i in args:
            tmp += str(i) + ", "
        tmp=tmp[:-2]
        classificationResultFileHandle.write("Programm arguments: " + tmp + "\n")
        classificationResultFileHandle.flush()

        CA, FA, CR, FR = evaluateProgWithParams(args,aedatFilePathes,classificationResultFileHandle)

        classificationResultFileHandle.close()

        paramValuesHandle.write(str(v) + ";")
        paramValuesHandle.write(str(CA) + ";")
        paramValuesHandle.write(str(CR) + ";")
        paramValuesHandle.write(str(FA) + ";")
        paramValuesHandle.write(str(FR) + "\n")
        paramValuesHandle.flush()

        score = computeScore(CA, CR, FA, FR)
        results.append([v, score])
    paramValuesHandle.close()
    return results

def evaluateParameterSet(paramSet,aedatFilePathes, optimizedParams, optimizationRuns):
    global outputDir
    for i in range(0,optimizationRuns):
        print "Current optimal parameters:"
        print optimizedParams
        summaryFileHandle = open(outputDir + "/" + "summary.txt","w")
        for paramName in paramSet:
            print "Param values for \""+ paramName+ "\":"
            print(paramSet[paramName])
            args = []
            args.extend(additionalCmdArgs)
            # Take optimal parameters from previous iterations if they exist
            for p in optimizedParams:
                # Don't take current parameter
                if p != paramName:
                    args.append("--" + p + "=" + str(optimizedParams[p]))

            results = evaluateParameterRange(paramName, paramSet[paramName], aedatFilePathes, args, "iter_" + str(i))
            optimalParam = max(results,key=lambda x:x[1])
            summaryFileHandle.write("Param: " + paramName + ", Optimal value: " + str(optimalParam[0]) + " with score " + str(optimalParam[1]) + "\n")
            summaryFileHandle.flush()
            optimizedParams[paramName]=optimalParam[0]
        summaryFileHandle.close()

    return optimizedParams

aedatFilePathes = findAeDatFiles(aedatFileRoot)
# runs * files * params
timing_exec_count = optimizationRuns*len(aedatFilePathes)*len([j for i in paramSet for j in paramSet[i]])
print "Execute program " + str(timing_exec_count) + " times..."
if not os.path.isdir(outputDir):
    os.makedirs(outputDir)
optimizedParams = evaluateParameterSet(paramSet,aedatFilePathes,defaultParams, optimizationRuns)
print optimizedParams
