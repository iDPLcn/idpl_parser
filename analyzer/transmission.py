#! /usr/bin/env python
import os,time
import sys
import socketClient
import socketServer
import socket
import TimedExec
from IDPLException import *


def myprint(string):
	print("*********************************************************\n" + string)

## *****************************
## main routine
## *****************************

print('************************' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + '************************\n')
serverTimeout = 120
clientTimeout = 120
server = "./socketServer.py"
client = "./socketClient.py"

if len(sys.argv) < 3:
	print ("val number error")
for string in sys.argv:
	print string

path = sys.argv[1]
host = ""
port = sys.argv[2]
config = sys.argv[3]

print path, host, port, config
if int(os.environ['_CONDOR_PROCNO']) == 0:
	print ("client start")
	client = socketClient.Client(config)
	client.demand()
	#print socket.gethostname(), socket.gethostbyname(socket.gethostname()) 
	#resultcode,output,err=TimedExec.runTimedCmd(clientTimeout,[client, config])
	#print(output)
	#if resultcode < 0:
		#print("Timeout! Result code: %d" % resultcode)
		#print(err)
                #raise TimeOutException("client")
else:
	print("server start")
	server = socketServer.Server(path, host, port)
	server.serve()
	#resultcode,output,err=TimedExec.runTimedCmd(serverTimeout, [server, path, host, port])
	#print(output)
	#if resultcode < 0:
		#print("Result code: %d" % resultcode)
		#print(err)
		#raise TimeOutException("server")
