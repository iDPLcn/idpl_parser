#!/usr/bin/env python
# encoding: UTF-8

import socket
import sys
import time
from thread import *
import fileReader
import re, getopt
import CondorTools

HOST = ""
PORT = 5022 
chirp = CondorTools.CondorChirp()

class Server:
	def __init__(self, path, host, port):
		self.path = path
		HOST = host
		PORT = port		
	
	def commuWithClient(self, conn):
		#conn.send("welcome!\n")
		timestamp = ""
		timestampNew = ""
		offset = ""
		offsetNew = ""
		while True:
			data = conn.recv(64)
			print ("data is: " + data + " type is: " + str(type(data)))
			if self.match(r"\d+(\.\d+)?,\d+", data):
				print("begin to read file!!")
				timestamp, offset = data.split(',')
				print "cat is: " + timestamp + " o is: " + offset + " p is: " + self.path
				strAdded, timestampNew, offsetNew = fileReader.FileReader().chooseLines(float(timestamp), int(offset), self.path)
				dataToSend = strAdded + "KUNSIGN" + timestampNew + "KUNSIGN" + offsetNew
				print(len(strAdded))
				conn.sendall(str(len(dataToSend)))
			elif self.match("kunBegin", data):
				conn.sendall(dataToSend)
			elif self.match("kunStop", data):
				#print("value error")
				raise
			else: 
				print("Done!")
				break
		#conn.send("bye\n")
		#conn.close()

	def match(self, reg, strToMatch):
		return re.compile(reg).match(strToMatch)

		

	def changeFlag(self):
		time.sleep(2)
		chirp.setJobAttr("SocketServer","'%s %d'" % (HOST, PORT))
		print("ChangeFlag()")
	
	def serve(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print ("Socket created")
		try:
			s.bind((HOST, PORT))
		except socket.error, msg:
			print ("Bind failed. Error Code : " + str(msg[0]) + " Message " + msg[1])
			sys.exit()

		print ("Socket bind complete")

		s.listen(1)
		print ("socket now listening")

		flagOfCondor = ""
		start_new_thread(self.changeFlag, ())
		conn, addr = s.accept()
		print ("Connected with " + addr[0] + ":" + str(addr[1]))
		try:
			self.commuWithClient(conn)
		except :
			print ("value error!")
			raise
		finally:
			s.close()
			print ("socket close now !")
			chirp.setJobAttr("SocketServer",None)
		print("exit")
		sys.exit()

if __name__ == '__main__':
	chirp.setJobAttr("SocketServer",None)
	if len(sys.argv) < 4:
		print ("server val num error")
	server = Server(sys.argv[1], sys.argv[2], sys.argv[3])
	server.serve()

