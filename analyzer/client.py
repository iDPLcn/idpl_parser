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
	uriShell = ""
	sourceFile = []

	def getOptions(self):
		opts, args = getopt.getopt(sys.argv[1:], "hl:t:s:", ["help", "log=", "timeStamp=", "shellScript="])
		for op,value in opts:
			if op in ("-h", "--help"):
				print("help")
				sys.exit(1)
			elif op in ("-l", "--log"):
				self.uriLog = value
			elif op in ("-t", "--timeStamp"):
				self.uriTime = value
			elif op in ("-s", "--shellScript"):
				self.uriShell = value

	def read(self, uri):
		self.sourceFile = open(uri)
		return self.sourceFile.readlines(), True

	def closeFile(self):
		self.sourceFile.close
    
	def combi(self, result):
		return self.uriShell+ " " + result + " USERNAME=username PASSWORD=password HOSTNAME=hostname:port"

	def excuteShell(self, result):
		output = os.popen(result)
		#print(output.read())

	def check(self, result, time):
		resultArray = result.split(' ')
		#print('checktime', resultArray[len(resultArray) - 5], time)
		if(float(resultArray[len(resultArray) - 5]) <= float(time[0])):
			return True

	def splitStr(self, string, char, offset):
		stringArray = string.split(char)
		return stringArray[len(stringArray) - offset]
        
    
	def main(self, analyzer):

		isFinished = False
		isNewTime = True
		self.getOptions()

		if not os.path.exists(self.uriTime):
			print('WARN! Create a timeRead file!')
			sys.exit(0)
        
		timeReadFile = open(self.uriTime)
		timeR = timeReadFile.readlines();
		if (len(timeR) == 0):
			timeR = [0.0]
		timeReadFile.close
		timeRNew = str(timeR[0])
        
		while(not isFinished):
			fileLines, isFinished = self.read(self.uriLog)            
            
			for i in range (len(fileLines) - 1, 0, -1):
				#print(line)
				result = analyzer.analyze(fileLines[i], "'iperf.*'")
				if result[0]:
					if self.check(result[1],timeR):
						isFinished =  True
						break
                    
					if (isNewTime):
						timeRNew = self.splitStr(result[1], ' ', 5)
						isNewTime = False
					#print self.combi(result[1])  
					self.excuteShell(self.combi(result[1]))
			self.closeFile()

		timeReadFile = open(self.uriTime, 'w')
		#print(timeRNew)
		timeReadFile.write(timeRNew)
		timeReadFile.close()



        
client = Client()
analyzer = analyzer.Analyzer()
client.main(analyzer)
print('****************' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + '****************\n')
