import subprocess,os,collections
import timeit
import datetime

class Fall:
  def __init__(self):
    self.direct = False
    self.delayed = False
    self.onlyPossible = False
    self.timestamp = -1
    self.speed = 0
    self.yCenter = 0
  def __str__(self):
    output = ""
    if self.direct:
        output+= "direct fall"
    if self.delayed:
        output+= "delayed fall"
    if self.onlyPossible:
        output+= "only possible fall"
    output += " ,timestamp: " + str(self.timestamp)
    if self.speed != 0:
        output += " ,speed: " + str(self.speed)
    if self.yCenter != 0:
        output += " ,yCenter: " + str(self.yCenter)

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

  def newEvent(self, type, time,speed=0, yCenter=0):
    if "direct" == type:
      fall = Fall()
      fall.timestamp = time
      fall.direct = True
      fall.speed = speed
      fall.yCenter = yCenter
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
      fall.speed = speed
      fall.yCenter = yCenter
      self.falls.append(fall)
    else:
      print "unexpected type"
      exit(1)

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
            if i in self.foundFalls:
                return -1
            else:
                self.foundFalls.append(i)
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

class EvaluationTools:
  def __init__(self,aedatFileRoot,programDir,proramName,outputDir,ignoreAedatFileParts,takePossibleFallAsTrue):
    self.outputDir = outputDir
    self.programDir=programDir
    self.programName=proramName
    self.timing_already_processed_count=0
    self.ignoreAedatFileParts = ignoreAedatFileParts
    self.takePossibleFallAsTrue = takePossibleFallAsTrue
    self.startTime = timeit.default_timer()
    self.datFiles = self.findAeDatFiles(aedatFileRoot)
    self.timing_exec_count=0

  def findAeDatFiles(self,aedatFileRoot):
    #Finding all aedat files
    aedatFilePathes=[]
    for path, subdirs, files in os.walk(aedatFileRoot):
      for name in files:
        ignore = [s for s in self.ignoreAedatFileParts if s in name]

        if os.path.splitext(name)[1] == ".aedat" and len(ignore) == 0:
          full_path=os.path.join(path, name)
          aedatFilePathes.append(full_path)
        elif len(ignore) > 0:
          print "Skipped: " + name

        aedatFilePathes = aedatFilePathes

    print "Found " + str(len(aedatFilePathes)) + " aedat files for evaluation."
    return aedatFilePathes

  def executeProgAndParseOutput(self,cmdArgs,aedatFilePath):
    print "File: " + aedatFilePath
    command=[]
    command.extend(cmdArgs)
    command.insert(0,self.programName)
    command.append(aedatFilePath)
    #Try to execute programm until no error occurs
    while(True):
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

        info = line.split(", ")
        objID = info[0]
        fType = info[1]
        timestamp = info[2].split(": ")[1]

        type = ""
        if "[Fall]: Delayed" in fType:
            type="delayed"
        elif "[Fall]: Directly" in fType:
            type="direct"
        elif "[Fall]: Possibly" in fType:
            type="possible"

        if objID not in detectedFallsById:
            detectedFallsById[objID] = TrackedObj(objID)
        # Find optional information
        if len(info) == 5:
            speed = info[3].split(": ")[1]
            ycenter = info[4].split(": ")[1]

            # Process new event
            detectedFallsById[objID].newEvent(type, timestamp, speed, ycenter)
        else:
            # Process new event
            detectedFallsById[objID].newEvent(type, timestamp)

    return detectedFallsById

  def importLabelFile(self,aedatFilePath):
    pre, oldExt = os.path.splitext(aedatFilePath)
    labelFileName = pre + ".label"

    labelFile = Labels()
    if os.path.isfile(labelFileName):
      lines = open(labelFileName).read().splitlines()
      for line in lines:
          labelFile.addFall(line.split(";"))

    return labelFile

  def evaluateProgWithParams(self,cmdArgs,classificationResultFileHandle = None, fallInfoFileHandle = None):
    FRSum = 0
    FASum = 0
    CASum = 0
    CRSum = 0

    # Execute programm in its directory
    origWD = os.getcwd() # remember our original working directory
    os.chdir(self.programDir)
    idx = 0
    for aedatFilePath in self.datFiles:
      FRSumOld = FRSum
      FASumOld = FASum
      CASumOld = CASum
      CRSumOld = CRSum

      detectedFallsById = self.executeProgAndParseOutput(cmdArgs,aedatFilePath)
      labels = self.importLabelFile(aedatFilePath)
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
                if fall.onlyPossible and not self.takePossibleFallAsTrue:
                    continue
                res = labels.isValidFalltime(fall.timestamp)
                if res != 0:
                    if res == 1:    # Not found before ?
                        CASum += 1
                        if fallInfoFileHandle != None:
                            fallInfoFileHandle.write(aedatFilePath + ";F;"+fall.speed + ";" + fall.yCenter + "\n")
                            fallInfoFileHandle.flush()
                else:
                    FASum += 1
                    if fallInfoFileHandle != None:
                        fallInfoFileHandle.write(aedatFilePath + ";NF;"+fall.speed + ";" + fall.yCenter + "\n")
                        fallInfoFileHandle.flush()

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
      print "Elapsed time:      " + str(datetime.timedelta(seconds=(timeit.default_timer()-self.startTime)))
      self.timing_already_processed_count+=1
      scaling = float(self.timing_exec_count-self.timing_already_processed_count)/self.timing_already_processed_count
      print "Remaining time:    " + str(datetime.timedelta(seconds=(timeit.default_timer()-self.startTime)*scaling))
      print "------------------------------------"
      print "Progress (files):  " + str(100.0*(idx+1)/len(self.datFiles)) + " %"
      print "Progress (global): " + str(100.0*(self.timing_already_processed_count)/self.timing_exec_count) + " %"
      idx+=1
      if classificationResultFileHandle != None:
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

  def computeScore(self,CA,CR,FA,FR):
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

  def evaluateParameterRange(self,paramName, valueList, addParams, outFileSuffix):
    headerStr = "Samples: "+ str(len(self.datFiles)) + ", Param: \"" + paramName + "\", Values: "
    for i in valueList:
      headerStr += str(i) + ", "
    headerStr=headerStr[:-2]
    headerStr += "\n"
    paramValuesOutFileName = self.outputDir + "/" + paramName + "_" + outFileSuffix + ".txt"

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
      self.timing_exec_count -= skippedValueCnt*len(self.datFiles)
    else:
      # File does not exist, create a new one and write the header
      print "Output file does not exist, create new one!"
      paramValuesHandle = open(paramValuesOutFileName,"w")
      paramValuesHandle.write(headerStr)
      paramValuesHandle.flush()

    # For all parameters, evaluate program
    results = []
    # Load results from already processed values from file
    for i in range(0,skippedValueCnt):
      tmp = lines[i+1][:-1].split(";")
      V, CA, CR, FA, FR = [float(i) for i in tmp[0:5]]
      valueList.remove(V);
      score = self.computeScore(CA, CR, FA, FR)
      results.append([tmp[0], score])

    if skippedValueCnt > 0:
      print "Remaining values to be processed:"
      print(valueList)

    # Continue with remaining values
    for v in valueList:
      args = []
      args.extend(addParams)
      args.append("--" + paramName + "=" + str(v))
      print "Parameters:"
      print(args)

      classificationResultFileName = self.outputDir + "/" + "classification_" +  paramName + "_" + str(v) + "_" + outFileSuffix + ".txt"
      classificationResultFileHandle = open(classificationResultFileName,"w")
      tmp = ""
      for i in args:
          tmp += str(i) + ", "
      tmp=tmp[:-2]
      classificationResultFileHandle.write("Programm arguments: " + tmp + "\n")
      classificationResultFileHandle.flush()

      CA, FA, CR, FR = self.evaluateProgWithParams(args,classificationResultFileHandle)

      classificationResultFileHandle.close()

      paramValuesHandle.write(str(v) + ";")
      paramValuesHandle.write(str(CA) + ";")
      paramValuesHandle.write(str(CR) + ";")
      paramValuesHandle.write(str(FA) + ";")
      paramValuesHandle.write(str(FR) + "\n")
      paramValuesHandle.flush()

      score = self.computeScore(CA, CR, FA, FR)
      results.append([v, score])

    paramValuesHandle.close()
    return results

  def evaluateParameterSet(self, paramSet, defaultParams, additionalCmdArgs, optimizationRuns):
    # runs * files * params
    self.timing_exec_count = optimizationRuns*len(self.datFiles)*len([j for i in paramSet for j in paramSet[i]])
    print "Execute program " + str(self.timing_exec_count) + " times..."
    if not os.path.isdir(self.outputDir):
        os.makedirs(self.outputDir)
    optimizedParams = defaultParams
    for i in range(optimizationRuns):
      print "Current optimal parameters:"
      print optimizedParams
      summaryFileHandle = open(self.outputDir + "/" + "summary.txt","w")
      for paramName in paramSet:
        print "-------- Processing {} ---------".format(paramName)
        print "Values:"
        print(paramSet[paramName])
        args = []
        args.extend(additionalCmdArgs)
        # Take optimal parameters from previous iterations if they exist
        for p in optimizedParams:
          # Don't take current parameter
         if p != paramName:
            args.append("--" + p + "=" + str(optimizedParams[p]))

        results = self.evaluateParameterRange(paramName, paramSet[paramName], args, "iter_" + str(i))
        optimalParam = max(results,key=lambda x:x[1])
        optimizedParams[paramName]=optimalParam[0]
        
        summaryFileHandle.write("Param: " + paramName + ", Optimal value: " + str(optimalParam[0]) + " with score " + str(optimalParam[1]) + "\n")
        summaryFileHandle.flush()
      
    summaryFileHandle.close()

    return optimizedParams
