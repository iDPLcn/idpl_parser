#!/usr/bin/env python
# encoding: UTF-8

import analyzer
import os,time
import sys,getopt

class Client:
    #uriLog = '/home/idpl/results/idpl.cnic/b2c.log'
    #uriTime = '/home/kunq/DataAccessor0.12/timeRead.txt'
    #uriLog = '/home/kun/GraduationProject/b2c.log'
    #uriTime = '/home/kun/GraduationProject/DataAccessor0.12/timeRead.txt'
	uriLog = ""
	uriTime = ""
	shellPath = ""
	sorceFile = []

	def getOptions(self):
		opts, args = getopt.getopt(sys.argv[1:], "hl:t:s:", ["help", "log=", "timeStamp=", "shellScript="])
		for op,value in opts:
			if op in ("-h", "--help"):
				print("client.py -l <log file> -t <timeRead file> -s <shell path>")
				sys.exit(1)
			elif op in ("-l", "--log"):
				self.uriLog = value
			elif op in ("-t", "--timeStamp"):
				self.uriTime = value
			elif op in ("-s", "--shellScript"):
				self.shellPath = value

	def readLog(self, uri):
		with  open(uri) as self.sourceFile:
			return self.sourceFile.readlines(), True

	def closeFile(self):
		self.sourceFile.close
    
	def combi(self, result, reg):
		return self.shellPath + "post_" + reg + "_time.sh" + " " + result + " USERNAME=username PASSWORD=password HOSTNAME=hostname:port"

	def excuteShell(self, result):
		output = os.popen(result)
		#print(output.read())

	def check(self, result, timeR):
		resultArray = result[1].split(' ')
		if(float(resultArray[len(resultArray) - 5]) < float(timeR[1])):
			return True
		elif(abs(float(resultArray[len(resultArray) - 5]) - float(timeR[1])) < 0.000001):
			return result[2] == timeR[0]
		return False

	def splitStr(self, string, char, offset):
		stringArray = string.split(char)
		return stringArray[len(stringArray) - offset]
       
	def readTimeRead(self, uri): 
   		try:
			timeReadFile = open(uri)
		except:
			print "file not exists!"			
		timeRead = timeReadFile.read().strip("\n")
		timeReadFile.close
		return timeRead

	def main(self, analyzer):

		isFinished = False
		isNewTime = True
		self.getOptions()
		tools = ["iperf", "netcat"]

		if not os.path.exists(self.uriTime):
			print('WARN! Create a timeRead file!')
			sys.exit(0)
        
		timeRead = self.readTimeRead(self.uriTime)
		timeR = timeRead.split(",")
		timeRNew = timeRead
        
		while(not isFinished):
			fileLines, isFinished = self.readLog(self.uriLog)            
            
			for i in range (len(fileLines) - 1, 0, -1):
				#print(line)
				result = analyzer.analyze(fileLines[i], tools)
				if result[0]:
					if self.check(result, timeR):
						isFinished =  True
						break
                    
					if (isNewTime):
						timestampNew = self.splitStr(result[1], ' ', 6)
						timeRNew = result[2] + "," + timestampNew
						isNewTime = False
					print self.combi(result[1], result[2])  
					#self.excuteShell(self.combi(result[1], result[2]))
			self.closeFile()

		with open(self.uriTime, 'w') as timeReadFile:
			print(timeRNew)
			timeReadFile.write(timeRNew)



        
client = Client()
analyzer = analyzer.Analyzer()
client.main(analyzer)
print('****************' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + '****************\n')
