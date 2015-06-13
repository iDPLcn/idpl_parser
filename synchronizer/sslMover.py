#!/usr/bin/env python
# encoding: UTF-8

import socket,ssl
import sys,os,traceback
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
		self.hasChanged = False

	def read(self, fileUriNow):
		with open(fileUriNow) as text:
			return text.readlines()

	def match(self, reg, strToMatch, timestamp):
		""" identify if a line matches the rule to add.
			if passes the regular expression test, 
				update timestampNew and offsetNew when first time passes
				compare the timestamp, choose the line timestampNow > timestamp
			else 
				add the line"""

		match = re.compile(reg).search(strToMatch)	
		if match:
			timestampNow = match.group()[1:(len(match.group()) - 1)].split(',')[3]
			if not self.hasChanged:
				self.timestampNew = timestampNow
				self.offsetNew = self.offsetNow
				self.hasChanged = True
			return float(timestampNow) > timestamp				
		else:
			if not self.hasChanged:
				self.offsetNow += 1
			return True

	def getNewFilePath(self, suffix):
		""" get the log rotated """
		return "%s.%d" % (self.fileUri, suffix), suffix + 1
	
	def chooseLinesInAFile(self, fileLines, reg, timestamp, strAdded, isTimeReached):
		""" choose lines match the rules in a file """
		for line in fileLines[::-1]:
			if self.match(reg, line, timestamp):
				strAdded.insert(0, line)
			else:
				isTimeReached = True
				break
		return strAdded, isTimeReached
	
	""" get all lines in a transfer """
	def chooseLines(self, timestamp, offsetL, path):
		iam = "server"
		ulog(iam, "extract data")
		self.fileUri = path
		self.offsetLast = offsetL
		reg = "'iperf.*'"
		isTimeReached = False
		strAdded = []
		fileUriNow = self.fileUri
		suffix = 0
		
		if not os.path.exists(fileUriNow):
			ulog(iam, "file not exist!")
			print("file not exist!")
			sys.exit(0)
		
		""" scan all logs including rotated if exist """	
		while (not isTimeReached and os.path.exists(fileUriNow)):
			fileLines = self.read(fileUriNow)
			strAdded, isTimeReached = self.chooseLinesInAFile(fileLines, reg, timestamp, strAdded, isTimeReached)
			fileUriNow, suffix = self.getNewFilePath(suffix)
		
		return ''.join(strAdded[self.offsetLast:]), self.timestampNew, str(self.offsetNew)

class TransmissionException(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)
		self.msg = msg

class Server:
	def __init__(self, path, port):
		self.path = path
		self.host = socket.getfqdn()
		self.port = port
		self.iam = "server"

	def commuWithClient(self, conn):
		timestamp = ""
		timestampNew = ""
		offset = ""
		offsetNew = ""
		
		""" get data to transfer via timestamp and offset from client and send data to client """
		while True:
			data = conn.recv(64)
			
			if self.match(r"\d+(\.\d+)?,\d+", data):
				timestamp, offset = data.split(',')
				strAdded, timestampNew, offsetNew = FileReader().chooseLines(float(timestamp), int(offset), self.path)
				dataToSend = "%s" % strAdded
				conn.sendall(str(len(dataToSend)))
			
			elif self.match("BEGIN", data):
				conn.sendall(dataToSend)
			
			elif self.match("STOP", data):
				raise TransmissionException("value error")
			
			elif self.match("END", data): 
				break
		
	def match(self, reg, strToMatch):
		return re.compile(reg).match(strToMatch)

	def changeFlag(self):
		time.sleep(2)
		chirp.setJobAttr("SSLServer","'%s %d'" % (self.host, int(self.port)))
	
	def serve(self):
		""" create an x509 cert and an rsa private key """
		ulog(self.iam, "create an ssl certificate and a private key")
		path = "./"
		certpath = "%scert.pem" % path
		keypath = "%skey.pem" % path
		os.popen("echo '\n\n\n\n\n\n\n' | openssl req -newkey rsa:1024 -x509 -days 365 -nodes -out %s -keyout %s" % (certpath, keypath))
		
		""" transfer SSL certificate to client via chirp"""
		ulog(self.iam, "send certificate to client")
		certStr = ""
		with open(certpath) as cert:
			for line in cert.readlines():
				certStr = "%s%s" % (certStr, line.strip("\n"))
		chirp.setJobAttr("SSLCert", "'%s'" % certStr)

		""" create a socket"""
		ulog(self.iam, "create a sockect connection")
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.bind(("", int(self.port)))
		except socket.error, msg:
			ulog(self.iam, "Bind failed. Error Code: %s Message %s" % (str(msg[0]), msg[1]))
			print("Bind failed. Error Code: %s Message %s" % (str(msg[0]), msg[1]))
			sys.exit()

		""" wait to connect from client """
		sock.listen(1)
		ulog(self.iam, "set SSLServer chirp")
		start_new_thread(self.changeFlag, ())
		conn, addr = sock.accept()
		
		""" wrap socket via ssl """
		ulog(self.iam, "transaction with client")
		conn_ssl = ssl.wrap_socket(conn, server_side = True, certfile = certpath, keyfile = keypath)
		try:
			self.commuWithClient(conn_ssl)
		except TransmissionException, trans:
			ulog(self.iam, "%s" % trans.msg)
			print("%s" % trans.msg)
			traceback.print_exc()

		
		finally:
			sock.close()
			ulog(self.iam, "socket close")
			chirp.setJobAttr("SSLServer", None)
			chirp.setJobAttr("SSLCert", None)
			if os.path.exists(certpath):
				os.remove(certpath)
			if os.path.exists(keypath):
				os.remove(keypath)
		sys.exit()


class XmlHandler:
	def __init__(self, xmlfile):
		self.xmlTree = self.readXml(xmlfile)
	
	def readXml(self, in_path):
		""" get the tree of xml file """
		if not os.path.exists(in_path):
			chirp.ulog("client : there is no such file: %s" % in_path)
			print("there is no such file: %s" % in_path)
			sys.exit()
		try:
			tree = ET.parse(in_path)
		except :
			chirp.ulog("client : tree parse error")
			print("tree parse error")
		return tree	
	
	def getNodes(self, tree):
		root = tree.getroot()
		return root.getchildren()		
		
	def findNode(self, nodes, tag):
		for node in nodes:
			if node.tag == tag:
				return node
	
	def getTexts(self, nodes, tags):
		""" get the content in xml flie via tags """
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

	def __init__(self,syn_log):
		self.syn_log = syn_log
		self.iam = "client"

	def get_constant(self, prefix):
		"""Create a dictionary mapping socket module constants to their names."""
		return dict(
			(getattr(socket, n), n)	for n in dir(socket) if n.startswith(prefix)
		)

	def get_constants(self, sock):
		families = self.get_constant('AF_')
		types = self.get_constant('SOCK_')
		protocols = self.get_constant('IPPROTO_')		
		
		ulog(self.iam, 'Family  : %s' % families[sock.family])
		ulog(self.iam, 'Type    : %s' % types[sock.type])
		ulog(self.iam, 'Protocol: %s' % protocols[sock.proto])
	
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

	def getTimestampOffset(self):
		reg = "'iperf.*'"
		pattern = re.compile(reg)
		timestamp = "0"
		offset = 0
		with open(self.syn_log) as s_log:
			fileLines = s_log.readlines()
		for line in fileLines[::-1]:
			match = pattern.search(line)
			if match:
				timestamp = match.group()[1:-1].split(",")[3]
				break
			else:
				offset += 1
		return timestamp, offset

	def request(self):
		
		timestamp, offset = self.getTimestampOffset()

		""" Get host and port from chirp """
		ulog(self.iam, "get SSLServer chirp")
		interval = 5
		maxtries = 12*3
		serverInfo = chirp.getJobAttrWait("SSLServer",None,interval, maxtries)	
		host,port = serverInfo.strip("'").split()
		
		""" Write the ssl certificate """
		ulog(self.iam, "get ssl certificate from server")
		certpath = "./cert.pem"
		sslCert = chirp.getJobAttrWait("SSLCert", None, interval, maxtries).strip("'")
		self.writeSSLCert(certpath, sslCert)

		""" Create a TCP/IP socket with SSL """
		ulog(self.iam, "create a connection with ssl")
		sock = socket.create_connection((host, int(port)))
		self.get_constants(sock)
		sockSSL = ssl.wrap_socket(sock, ca_certs = certpath, cert_reqs = ssl.CERT_REQUIRED)
		

		""" Send data """
		try:
			
			""" get amount of data to receive """
			ulog(self.iam, "begin to get data")
			message = "%s,%s" % (timestamp, offset)
			sockSSL.sendall(message)
			rec = sockSSL.recv(64)
			amount = int(rec)
			amount_received = 0			
			
			""" receive data """
			sockSSL.sendall("BEGIN")
			strAdded = ""
			while amount_received < int(amount):
				data = sockSSL.recv(min(4096, int(amount) - amount_received))
				strAdded += data
				amount_received += len(data)
			sockSSL.sendall("END")
			
			""" write data to log, write timestamp and offset to xml file """
			if not amount_received < amount:
				with open(self.syn_log, "a") as output:
					ulog(self.iam, "update log")
					output.write(strAdded)
		except Exception, e:
			sockSSL.sendall("STOP")
			traceback.print_exc()	

		finally:
			ulog(self.iam, 'closing socket')
			sockSSL.close()
			sock.close()
			if os.path.exists(certpath):
				os.remove(certpath)

def ulog(who, message):
	logMessage = "%s : %s" % (who, message)
	chirp.ulog(logMessage)

def usage():
	print("sslMain.py -l <logpath> -p <port> -s <syn log>")

def main(argv):
	print "argvs are: " + "".join(argv)
	if len(argv) < 6:
		usage()
		sys.exit()
	
	try:
		opts, args = getopt.getopt(argv, "hl:p:s:", ["help", "log_path=", "port=", "syn_log="])
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
		elif opt in ("-s", "--syn_log"):
			syn_log = arg

	if int(os.environ['_CONDOR_PROCNO']) == 0:
		chirp.ulog("client start")
		client = Client(syn_log)
		client.request()
		
	else:
		chirp.ulog("server start")
		chirp.setJobAttr("SSLServer",None)
		chirp.setJobAttr("SSLCert", None)
		server = Server(log_path, port)
		server.serve()
		chirp.setJobAttr("SSLServer", None)
		chirp.setJobAttr("SSLCert", None)

if __name__ == '__main__':
	main(sys.argv[1:])

# vim: ts=4:sw=4
