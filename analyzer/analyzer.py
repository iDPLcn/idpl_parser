# encoding: UTF-8
import re

class Analyzer:
    #regOfIperf = "\\d{3}\\s\\(\\d{4}\\.\\d{3}\\.\\d{3}\\)\\s\\d{2}/\\d{2}\\s(\\d{2}:){2}\\d{2}\\s'iperf.*'"
    #regOfIperf = "'iperf.*'"
    def match(self, reg, strToMatch, result):
        pattern = re.compile(reg)
        match = pattern.search(strToMatch)
        if match:
            result = match.group()[1:(len(result) - 1)]
            #print("bingo! " + result)
            return True, result
        return False,result
            
    def combi(self, strToCombi):
        #print (strToCombi)
        strArray = strToCombi.split(',')[1:]
        if (not self.deal(strArray)):
            return False, ''        
        #print(strArray)
        seq = ' '
        strToCombi = seq.join(strArray)
        #print(strToCombi)
        return True, strToCombi

    def deal(self, strArray):
        bandwidth = float('%0.2f'%((float(strArray[len(strArray) - 1]) * 1024 * 8) / float(strArray[len(strArray) - 2])))
        if (abs(bandwidth) <= 0.000001):
            return False
        strArray.append(str(bandwidth))
        return True
        #print(bandwidth)

    def analyze(self, strToMatch, reg):
#        strToMatch = "008 (3014.000.000) 03/10 22:30:17 'iperf,flashio-osg.calit2.optiputer.net,\
#komatsu.chtc.wisc.edu,1426051806.244003,1426051817.145583,1,10.901580,4697344'" 
        result = ''
        matchResult = self.match(reg, strToMatch, result)
        if matchResult[0]:
            resultSet = self.combi(matchResult[1])
            #print result
            return resultSet
        else:
            return False, result
        

    

'''
file = open("D:\\Homework\\GraduationProject\\analyzer\\placement.log")
for line in file:
    print(line)
file.close

analyzer = Analyzer()
analyzer.analyze()
'''
