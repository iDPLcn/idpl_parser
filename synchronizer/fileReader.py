#!/usr/bin/env python
# encoding: UTF-8

import re,os

class FileReader:

	fileUri = ""

	offsetLast = 0
	offsetNew = 0
	offsetNow = 0
	timestampNew = ""
	isHasChanged = False
	
	def read(self, fileUriNow):
		with open(fileUriNow) as text:
			#print("fileReader, file is " + fileUriNow)
			return text.readlines()
	
	def getALine(self, fileLines):
		 return fileLines.pop()

	def match(self, reg, strToMatch, timestamp):
		match = re.compile(reg).search(strToMatch)
		
		if match:
			timestampNow = match.group()[1:(len(match.group()) - 1)].split(',')[3]
			#print (timestampNow)
			if not self.isHasChanged:
				#print (self.offsetNow)
				self.timestampNew = timestampNow
				self.offsetNew = self.offsetNow
				self.isHasChanged = True
			return float(timestampNow) > timestamp				
		else:
			if not self.isHasChanged:
				#print("add!!!!")
				self.offsetNow += 1
				#print(self.offsetNow)
			return True

	def getNewFilePath(self, suffix):
		return self.fileUri + '.' + str(suffix), suffix + 1
		

	def chooseLinesInAFile(self, fileLines, reg, timestamp, strAdded, isTimeReached):
		while len(fileLines):
			line = self.getALine(fileLines)
			#print ("line: " + line)
			if self.match(reg, line, timestamp):
				strAdded.insert(0, line)
			else:
				isTimeReached = True
				break
		return strAdded, isTimeReached
		

	def chooseLines(self, timestamp, offsetL, path):
		#self.fileUri = "/home/kun/GraduationProject/ServerClient0.11/test.txt"
		self.fileUri = path
		print "file is: " + self.fileUri + " t is: " + str(timestamp) + " o is: " + str(offsetL)
		self.offsetLast = offsetL
		reg = "'iperf.*'"
		isTimeReached = False
		strAdded = []
		fileUriNow = self.fileUri
		suffix = 0
		if not os.path.exists(fileUriNow):
			print("file not exist!")
			sys.exit(0)
		while (not isTimeReached and os.path.exists(fileUriNow)):
			fileLines = self.read(fileUriNow)
			strAdded, isTimeReached = self.chooseLinesInAFile(fileLines, reg, timestamp, strAdded, isTimeReached)
			fileUriNow, suffix = self.getNewFilePath(suffix)
			print ("isTimeReached: " + str(isTimeReached) + " file is: " + fileUriNow + " suffix is: " + str(suffix) + " is: " + str(os.path.exists(fileUriNow)))
		#print (''.join(strAdded))
		#print("Now offset is: " + str(self.offsetNew))
		return ''.join(strAdded[self.offsetLast:]), self.timestampNew, str(self.offsetNew)

if __name__ == '__main__':
	timestamp = 0
	fileReader = FileReader()
	fileReader.chooseLines(timestamp)

	
