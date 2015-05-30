#!/usr/bin/env python
# encoding: UTF-8

import socket,ssl
import sys,os
import time
from thread import *
import re, getopt
import CondorTools
from xml.etree import ElementTree as ET

chirp = CondorTools.CondorChirp()

class FileReader:
	
	def __init__(self):
		
		self.fileUri = ""
		self.offsetLast = 0
		self.offsetNew = 0
		self.offsetNow = 0
		self.timestampNew = ""
		self.isHasChanged = False
	
	def read(self, fileUriNow):
		with open(fileUriNow) as text:
			return text.readlines()
	
	def getALine(self, fileLines):
		 return fileLines.pop()

	def match(self, reg, strToMatch, timestamp):
		match = re.compile(reg).search(strToMatch)
		
		if match:
			timestampNow = match.group()[1:(len(match.group()) - 1)].split(',')[3]
			if not self.isHasChanged:
				self.timestampNew = timestampNow
				self.offsetNew = self.offsetNow
				self.isHasChanged = True
			return float(timestampNow) > timestamp				
		else:
			if not self.isHasChanged:
				self.offsetNow += 1
			return True

	def getNewFilePath(self, suffix):
		return "%s.%d" % (self.fileUri, suffix), suffix + 1
	

	def chooseLinesInAFile(self, fileLines, reg, timestamp, strAdded, isTimeReached):
		while len(fileLines):
			line = self.getALine(fileLines)
			if self.match(reg, line, timestamp):
				strAdded.insert(0, line)
			else:
				isTimeReached = True
				break
		return strAdded, isTimeReached
		

	def chooseLines(self, timestamp, offsetL, path):
		self.fileUri = path
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
		return ''.join(strAdded[self.offsetLast:]), self.timestampNew, str(self.offsetNew)

class Server:
	def __init__(self, path, port):
		self.path = path
		self.host = socket.getfqdn()
		self.port = port
	
	def commuWithClient(self, conn):
		timestamp = ""
		timestampNew = ""
		offset = ""
		offsetNew = ""
		while True:
			data = conn.recv(64)
			
			if self.match(r"\d+(\.\d+)?,\d+", data):
				timestamp, offset = data.split(',')
				strAdded, timestampNew, offsetNew = FileReader().chooseLines(float(timestamp), int(offset), self.path)
				dataToSend = "%sKUNSIGN%sKUNSIGN%s" % (strAdded, timestampNew, offsetNew)
				conn.sendall(str(len(dataToSend)))
			
			elif self.match("KUNBEGIN", data):
				conn.sendall(dataToSend)
			
			elif self.match("KUNSTOP", data):
				print("value error")
				raise
			else: 
				break

	def match(self, reg, strToMatch):
		return re.compile(reg).match(strToMatch)

		

	def changeFlag(self):
		time.sleep(2)
		chirp.setJobAttr("SSLServer","'%s %d'" % (self.host, int(self.port)))
	
	def serve(self):
		""" create an x509 cert and an rsa private key """
		path = "/tmp/"
		certpath = "%scert.pem" % path
		keypath = "%skey.pem" % path
		os.popen("echo '\n\n\n\n\n\n\n' | openssl req -newkey rsa:1024 -x509 -days 365 -nodes -out %s -keyout %s" % (certpath, keypath))
		
		""" transfer SSL certificate to client via chirp"""
		certStr = ""
		with open(certpath) as cert:
			for line in cert.readlines():
				certStr = "%s%s" % (certStr, line.strip("\n"))
		chirp.setJobAttr("SSLCert", "'%s'" % certStr)


		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.bind(("", int(self.port)))
		except socket.error, msg:
			print ("Bind failed. Error Code: %s Message %s" % (str(msg[0]), msg[1]))
			sys.exit()


		sock.listen(1)

		start_new_thread(self.changeFlag, ())
		conn, addr = sock.accept()
		conn_ssl = ssl.wrap_socket(conn, server_side = True, certfile = certpath, keyfile = keypath)
		try:
			self.commuWithClient(conn_ssl)
		except :
			print ("value error!")
			raise
		finally:
			sock.close()
			print ("socket close now !")
			chirp.setJobAttr("SSLServer", None)
			chirp.setJobAttr("SSLCert", None)
		sys.exit()


class XmlHandler:
	def __init__(self, xmlfile):
		self.xmlTree = self.readXml(xmlfile)
	
	def readXml(self, in_path):		
		if not os.path.exists(in_path):
			print ("there is no such file: %s" % in_path)
			sys.exit()
		try:
			tree = ET.parse(in_path)
		except:
			print ("tree parse error")
			raise
		return tree	
	
	def getNodes(self, tree):
		root = tree.getroot()
		return root.getchildren()		
		
	def findNode(self, nodes, tag):
		for node in nodes:
			if node.tag == tag:
				return node
	
	def getTexts(self, nodes, tags):
		texts = []
		for tag in tags:
			texts.append(self.findNode(nodes, tag).text)
		return texts			

	def read(self):		
		nodes = self.getNodes(self.xmlTree)
		path, timestamp, offset= self.getTexts(nodes, ["path", "timestamp", "offset"])
		return  path, timestamp, offset
	
	def writeXml(self, node, text):
		node.text = text
	
	def setTexts(self, texts, tags):
		nodes = self.getNodes(self.xmlTree)
		for text, tag in zip(texts, tags):
			self.writeXml(self.findNode(nodes, tag), text)

	def write(self, newTimestamp, newOffset, xmlfile):
		self.setTexts([newTimestamp, newOffset], ["timestamp", "offset"])
		self.xmlTree.write(xmlfile, encoding="utf-8")



class Client:

	def __init__(self,config):
		self.config = config

	def get_constant(self, prefix):
		"""Create a dictionary mapping socket module constants to their names."""
		return dict( (getattr(socket, n), n)
						for n in dir(socket) if n.startswith(prefix)
					)

	def get_constants(self, sock):
		families = self.get_constant('AF_')
		types = self.get_constant('SOCK_')
		protocols = self.get_constant('IPPROTO_')		
		
		print 'Family  :', families[sock.family]
		print 'Type    :', types[sock.type]
		print 'Protocol:', protocols[sock.proto]
	
	def writeSSLCert(self, path, sslCert):
		certBegin = sslCert[ : 27]
		certEnd = sslCert[-25 : ]
		#TODO if 27 > len -25 ?
		certContent = sslCert[27 : -25]
		certContentList = []
		for i in range(0, len(certContent), 64):
			line = certContent[i : i + 64]
			certContentList.append(line + "\n")
		certContent = "".join(certContentList)
		certDealt = "%s\n%s%s" % (certBegin, certContent, certEnd)
		
		with open(path, "w") as certfile:
			certfile.write(certDealt)


		

	def request(self):
		""" Read xml file """
		try:
			xmlHandler = XmlHandler(self.config)
		except:
			print "xml read error"
			sys.exit()
		path, timestamp, offset = xmlHandler.read()
		
		""" Get host and port from chirp """
		interval = 5
		maxtries = 12*3
		serverInfo = chirp.getJobAttrWait("SSLServer",None,interval, maxtries)	
		host,port = serverInfo.strip("'").split()
		
		""" Write the ssl certificate """
		certpath = "/tmp/cert.pem"
		sslCert = chirp.getJobAttrWait("SSLCert", None, interval, maxtries).strip("'")
		self.writeSSLCert(certpath, sslCert)

		""" Create a TCP/IP socket with SSL """
		sock = socket.create_connection((host, int(port)))
		self.get_constants(sock)
		sockSSL = ssl.wrap_socket(sock, ca_certs = certpath, cert_reqs = ssl.CERT_REQUIRED)
		

		try:
			""" Send data """
			message = "%s,%s" % (timestamp, offset)
			sockSSL.sendall(message)
			amount_received = 0			
			rec = sockSSL.recv(64)
			amount = int(rec)
			sockSSL.sendall("KUNBEGIN")
    			
			dataComp = ""
			while amount_received < int(amount):
				data = sockSSL.recv(min(4096, int(amount) - amount_received))
				dataComp += data
				amount_received += len(data)
			
			strAdded, timestamp, offset = dataComp.split("KUNSIGN")
			
			if not amount_received < amount:
				with open(path, "a") as output:
					output.write(strAdded)
				#if timestamp and offset:
					#xmlHandler.write(timestamp, offset, self.config)
		except:
			sockSSL.sendall("KUNSTOP")
			print "amount value error"
			raise

		finally:
			print 'closing socket'
			sockSSL.close()
			sock.close()


def usage():
	print("sslMain.py -l <logpath> -p <port> -c <clientconfigfile>")


def main(argv):
	if len(sys.argv) < 6:
		usage()
		sys.exit()

	try:
		opts, args = getopt.getopt(argv, "hl:p:c:", ["help", "log_path=", "port=", "config="])
	except getopt.GetoptError:
		usage()
		sys.exit()

	for opt, arg in opts:
		if opt in ("-h", "--help" ):
			usage()
			sys.exit()
		elif opt in ("-l", "--log_path"):
			log_path = arg
		elif opt in ("-p", "--port"):
			port = arg
		elif opt in ("-c", "--config"):
			config = arg

	if int(os.environ['_CONDOR_PROCNO']) == 0:
		client = Client(config)
		client.request()
		
	else:
		chirp.setJobAttr("SSLServer",None)
		chirp.setJobAttr("SSLCert", None)
		server = Server(log_path, port)
		server.serve()

if __name__ == '__main__':
	main(sys.argv[1:])

# vim: ts=4:sw=4
