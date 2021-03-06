# encoding: UTF-8
import re

class Analyzer:
	""" use regular expression to judge if a line matches """
	def match(self, reg, strToMatch, result):
		pattern = re.compile(reg)
		match = pattern.search(strToMatch)
		if match:
			result = match.group()[1:-1]
			return True, result
		return False,result
            
	""" combine bandwidth into a line """
	def combi(self, strToCombi, tool):
		strArray = strToCombi.split(',')[1:]

		""" transform the unit of datasize in scp from B to KB """
		if tool != "iperf":
			datasize = strArray[-1]
			strArray[-1] = str(float(datasize) / 1024)
		
		""" append bandwidth and remove the point whose bandwidth is 0 """
		if (not self.deal(strArray, tool)):
			return [False, '']

		strToCombi = ' '.join(strArray)
		return [True, strToCombi]

	""" compute and append bandwidth """
	def deal(self, strArray, tool):
		bandwidth = float('%0.2f'%((float(strArray[-1]) * 1024 * 8) / float(strArray[-2])))
		
		""" remove the point whose bandwidth is 0 """
		if (abs(bandwidth) <= 0.000001):
			return False

		strArray.append(str(bandwidth))
		strArray.append(tool)
		return True
	
	""" analyze a line """
	def analyze(self, strToMatch, tools, reg_prefix):
		result = ''
		for tool in tools:
			reg = "'" + reg_prefix + tool + ".*'"
			matchResult = self.match(reg, strToMatch, result)
			if matchResult[0]:
				resultSet = self.combi(matchResult[1], tool)
				resultSet.append(tool)
				break
			else:
				resultSet = [False, result, tool]
		return resultSet
	
