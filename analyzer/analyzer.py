# encoding: UTF-8
import re

class Analyzer:
    #regOfIperf = "'iperf.*'"
    def match(self, reg, strToMatch, result):
        pattern = re.compile(reg)
        match = pattern.search(strToMatch)
        if match:
            result = match.group()[1:(len(result) - 1)]
            #print("bingo! " + result)
            return True, result
        return False,result
            
    def combi(self, strToCombi, tool):
		print (tool)
		strArray = strToCombi.split(',')[1:]
		if tool == "netcat":
			datasize = strArray[len(strArray) - 1]
			strArray[len(strArray) - 1] = str(float(datasize) / 1024)
		if (not self.deal(strArray)):
			return False, ''
			#print(strArray)
		seq = ' '
		strToCombi = seq.join(strArray)
		#print(strToCombi)
		return [True, strToCombi]

    def deal(self, strArray):
        bandwidth = float('%0.2f'%((float(strArray[len(strArray) - 1]) * 1024 * 8) / float(strArray[len(strArray) - 2])))
        if (abs(bandwidth) <= 0.000001):
            return False
        strArray.append(str(bandwidth))
        return True
        #print(bandwidth)

    def analyze(self, strToMatch, tools):
		result = ''
		for tool in tools:
			reg = "'" + tool + ".*'"
			matchResult = self.match(reg, strToMatch, result)
			if matchResult[0]:
				resultSet = self.combi(matchResult[1], tool)
				resultSet.append(tool)
				break
			else:
				resultSet = [False, result, tool]
		return resultSet
	

    

'''
file = open("D:\\Homework\\GraduationProject\\analyzer\\placement.log")
for line in file:
    print(line)
file.close

analyzer = Analyzer()
analyzer.analyze()
'''
