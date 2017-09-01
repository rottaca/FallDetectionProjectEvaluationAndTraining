import subprocess,os,collections
import timeit
import datetime
import evaluationTools
import sys


f=open(sys.argv[1],'r')
lines = f.readlines()[1:]

CA = 0
FA = 0
CR = 0
FR = 0
for line in lines:
  tokens = line.split(";")
  fName=tokens[0]
  CA+=int(tokens[1])
  CR+=int(tokens[2])
  FA+=int(tokens[3])
  FR+=int(tokens[4])
  
print "CA: " + str(CA)
print "FA: " + str(FA)
print "CR: " + str(CR)
print "FR: " + str(FR)
  

