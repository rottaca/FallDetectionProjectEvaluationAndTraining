import subprocess,os,collections

programDir="../../build-FallDetectionProject-Desktop_Qt_5_8_0_GCC_64bit-Release/"
programName="./FallDetectionProject"
aedatFileRoot="/tausch/FallDetectionProjectRecords/Preliminary/"
takePossibleFallAsTrue=True
paramSet = collections.OrderedDict()
paramSet["minSpeed"] = [x / 10.0 for x in range(10, 51, 1)]
paramSet["maxSpeed"] = [x / 10.0 for x in range(25, 101, 1)]

additionalCmdArgs=["--min"]

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

    process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()

    # Get programm output
    out, err = process.communicate()

    # Check for errors
    if process.returncode != 0:
        print "Non-zero return code: " + str(process.returncode)
        print err
        print out
        exit(1)

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

    def addFall(self,times):
        assert len(times) == 4
        self.falls.append(times)

    def isValidFalltime(self,time):
        for fall in self.falls:
            if time >= fall[0] and time <= fall[3]:
                return True
        return False

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

def evaluateProgWithParams(cmdArgs, aedatFilePathes, takePossibleFallAsTrue):

    testCasePositiveCount = 0
    testCaseNegativeCount = 0

    fallFR = 0
    fallFA = 0
    fallCA = 0
    fallCR = 0

    # Execute programm in its directory
    origWD = os.getcwd() # remember our original working directory
    os.chdir(programDir)
    idx = 0
    for aedatFilePath in aedatFilePathes:

        detectedFallsById = executeProgAndParseOutput(cmdArgs,aedatFilePath)
        labels = importLabelFile(aedatFilePath)
        print "Labels:"
        print(labels)
        print "Detected falls:"
        print(detectedFallsById)

        delayed = 0
        onlyPossible = 0
        direct = 0
        for ID in detectedFallsById:
            delayed += detectedFallsById[ID].countDelayed()
            direct += detectedFallsById[ID].countDirect()
            onlyPossible += detectedFallsById[ID].countPossible()
        sumDetected = direct + delayed


        if len(detectedFallsById) == 0:
            print "Nothing detected"
            if labels.getLen() > 0:
                fallFR += labels.getLen()
                testCasePositiveCount += 1
            else:
                fallCR += 1
                testCaseNegativeCount += 1
        else:
            # Check if there is a valid fall
            # for each object
            for objId in detectedFallsById:
                # Check each fall
                falls = detectedFallsById[objId].getFalls()
                for fall in falls:
                    if labels.isValidFalltime(fall.timestamp):
                        if fall.onlyPossible and not takePossibleFallAsTrue:
                            fallFR += 1
                        else:
                            fallCA += 1

                        testCasePositiveCount += 1
                    else:
                        if fall.onlyPossible and not takePossibleFallAsTrue:
                            fallCR += 1
                        else:
                            fallFA += 1

                        testCaseNegativeCount += 1

        print "------ summary -------"
        tmp = ""
        for a in cmdArgs:
            tmp += a + " "
        print "Args: " + tmp
        print "----------------------"
        print "CA: " + str(fallCA)
        print "CR: " + str(fallCR)
        print "FA: " + str(fallFA)
        print "FR: " + str(fallFR)
        print "----------------------"
        print "Sum N: " + str(testCaseNegativeCount)
        print "Sum P: " + str(testCasePositiveCount)
        print "Progress: " + str(100.0*(idx+1)/len(aedatFilePathes)) + " %"
        idx+=1

    os.chdir(origWD) # get back to our original working directory
    testCasesSum = testCasePositiveCount + testCaseNegativeCount
    if testCasePositiveCount > 0:
        fallCA = float(fallCA)/float(testCasePositiveCount)
        fallFR = float(fallFR)/float(testCasePositiveCount)
    else:
        fallCA = 0
        fallFR = 0
    if testCaseNegativeCount > 0:
        fallFA = float(fallFA)/float(testCaseNegativeCount)
        fallCR = float(fallCR)/float(testCaseNegativeCount)
    else:
        fallFA = 0
        fallCR = 0

    print "-------------------"
    print "Results"
    print "Correct acceptance: " + str(fallCA)
    print "False acceptance: " + str(fallFA)
    print "Correct rejection: " + str(fallCR)
    print "False rejection: " + str(fallFR)
    print "Test cases (P/N): " + str(testCasesSum) + " ("+ str(testCasePositiveCount) + "/"+ str(testCaseNegativeCount)  +")"

    return fallCA, fallFA, fallCR, fallFR, testCasePositiveCount,testCaseNegativeCount

def computeScore(CA,CR,FA,FR):
    if CA+FR > 0:
        recall = CA/(CA+FR)
    else:
        recall = 0
    if CA+FA > 0:
        precision = CA/(CA+FA)
    else:
        precision = 0
    # Youden's index
    return recall + precision - 1

def evaluateParameterRange(paramName, valueList, aedatFilePathes, addParams, takePossibleFallAsTrue):
    headerStr = "Header: Samples: "+ str(len(aedatFilePathes)) + ", Param: \"" + paramName + "\", Values: "
    for f in valueList:
        headerStr += str(f) + ", "
    headerStr=headerStr[:-2]
    headerStr += "\n"
    outFile = paramName + ".txt"

    skippedValueCnt = 0
    # Check if file exists (backup) and continue with next value
    if os.path.isfile(outFile):
        f = open(outFile,"a+")
        # Read text from file
        lines = f.readlines()
        # Header has to be equal
        if lines[0] != headerStr:
            print "Invalid output file found: " + outFile
            print "Expected header:"
            print headerStr
            exit(1)
        # Count number of already processed values
        skippedValueCnt = len(lines)-1
        print "Output file found! Contains already " + str(skippedValueCnt) + " parameter value(s)."
        valueList = valueList[skippedValueCnt:]
        print "Remaining values to be processed:"
        print(valueList)
    else:
        # File does not exist, create a new one and write the header
        f = open(outFile,"w")
        f.write(headerStr)
        f.flush()

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
        CA, FA, CR, FR, P, N = evaluateProgWithParams(args,aedatFilePathes, takePossibleFallAsTrue)
        f.write(str(v) + ";")
        f.write(str(CA) + ";")
        f.write(str(CR) + ";")
        f.write(str(FA) + ";")
        f.write(str(FR) + ";")
        f.write(str(P) + ";")
        f.write(str(N) + "\n")
        f.flush()

        score = computeScore(CA, CR, FA, FR)
        results.append([v, score])
    f.close()
    return results

def evaluateParameterSet(paramSet,aedatFilePathes,takePossibleFallAsTrue):
    optimizedParams = {};
    for i in range(0,2):
        f = open("summary.txt","w")
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

            results = evaluateParameterRange(paramName, paramSet[paramName], aedatFilePathes, args, takePossibleFallAsTrue)
            optimalParam = max(results,key=lambda x:x[1])
            f.write("Param: " + paramName + ", Optimal value: " + str(optimalParam[0]) + " with score " + str(optimalParam[1]))
            f.flush()
            optimizedParams[paramName]=optimalParam[0]
        f.close()
    return optimizedParams

aedatFilePathes = findAeDatFiles(aedatFileRoot)[1:10]
optimizedParams = evaluateParameterSet(paramSet,aedatFilePathes,takePossibleFallAsTrue)
print optimizedParams
