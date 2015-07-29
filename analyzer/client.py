#!/usr/bin/env python
# encoding: UTF-8

import analyzer
import os,time
import sys,getopt

class Client:
	def __init__(self):
		self.uriLog = ""
		self.uriTime = ""
		self.shellPath = ""
		self.reg_prefix = "undefined"
		self.sourceFile = []
	
	def usage(self):
		print("client.py -l <log file> -t <timeRead file> -s <shell path> [-r <regular>]")

	def getOptions(self):
		
		if len(sys.argv) < 7:
			self.usage()
			sys.exit()
		
		opts, args = getopt.getopt(sys.argv[1:], "hl:t:s:r:", ["help", "log=", "timeStamp=", "shellScript=", "regular="])
		for op,value in opts:
			if op in ("-h", "--help"):
				self.usage()
				sys.exit()
			elif op in ("-l", "--log"):
				self.uriLog = value
			elif op in ("-t", "--timeStamp"):
				self.uriTime = value
			elif op in ("-s", "--shellScript"):
				self.shellPath = value
			elif op in ("-r", "--regular"):
				self.reg_prefix = value
		if self.reg_prefix == "undefined":
		  self.reg_prefix = ".*writerecord:"
		elif self.reg_prefix == "NULL":
		  self.reg_prefix = ""

	""" read the log rotated """
	def readLog(self, uri):
		#TODO
		with  open(uri) as self.sourceFile:
			return self.sourceFile.readlines(), True

	def closeFile(self):
		self.sourceFile.close
    
	""" choose the corresponding shell to insert into database """
	def combi(self, result, tool):
		return self.shellPath + "post_measuredata.sh " + result + "  USERNAME=username PASSWORD=password HOSTNAME=hostname:port"
	
	""" insert data into database """
	def excuteShell(self, result):
		output = os.popen(result)

	""" check the data if inserted 
		if timestmap in the line analyzed now less than timestamp last, indicate the data is inserted
		else if timestamps are equal, if tool is equal, indicate the data is inserted 
		else the data has not inserted"""
	def check(self, result, timeR, offset):
		resultArray = result[1].split(' ')
		if(float(resultArray[-offset]) < float(timeR[1])):
			return True
		elif(abs(float(resultArray[-offset]) - float(timeR[1])) < 0.000001):
			return result[2] == timeR[0]
		return False

	def splitStr(self, string, char, offset):
		stringArray = string.split(char)
		return stringArray[-offset]
      
	""" get the timestamp last read to """
	def readTimeRead(self, uri): 
   		try:
			timeReadFile = open(uri)
		except:
			print "timestamp file not exists!"			
		timeRead = timeReadFile.read().strip("\n")
		timeReadFile.close
		return timeRead

	def main(self, analyzer):
		
		offset = 6
		isFinished = False
		isNewTime = True
		self.getOptions()
		tools = ["iperf", "scp", "netcat"]

		if not os.path.exists(self.uriTime):
			print('WARN! Create a timeRead file!')
			sys.exit(0)
        
		timeRead = self.readTimeRead(self.uriTime)
		timeR = timeRead.split(",")
		timeRNew = timeRead
        
		""" analyze log """
		while(not isFinished):
			#TODO read log rotated
			fileLines, isFinished = self.readLog(self.uriLog)            
            
			for line in range fileLines[::-1]:
				result = analyzer.analyze(line, tools, self.reg_prefix)
				if result[0]:
					if self.check(result, timeR, offset):
						isFinished =  True
						break
                    
					if (isNewTime):
						timestampNew = self.splitStr(result[1], ' ', offset)
						timeRNew = result[2] + "," + timestampNew
						isNewTime = False
					#print self.combi(result[1], result[2])  
					self.excuteShell(self.combi(result[1], result[2]))
			self.closeFile()

		with open(self.uriTime, 'w') as timeReadFile:
			timeReadFile.write(timeRNew)



        
client = Client()
analyzer = analyzer.Analyzer()
client.main(analyzer)
print('****************' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + '****************\n')
