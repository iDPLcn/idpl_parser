#! /usr/bin/env python
import os,time
import sys,getopt
import TimedExec
from IDPLException import *
import sslMover

## *****************************
## main routine
## *****************************

print("\n%s\n" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
timeout = 120
sslexe = "./sslMover.py"
log_path = ""
port = ""
syn_log = ""

def usage():
	print("sslMain.py -l <logpath> -p <port> -s <syn file>")

if len(sys.argv) < 7:
	usage()
	sys.exit()

try:
	opts, args = getopt.getopt(sys.argv[1:], "hl:p:s:", ["help", "log_path=", "port=", "syn_log="])
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


resultcode,output,err=TimedExec.runTimedCmd(timeout,[sslexe, "-l", log_path, "-p", port, "-s", syn_log])
sys.stdout.write("output: %s" % " ".join(output))
sys.stderr.write("err: %s" % " ".join(err))
if resultcode < 0:
	side = int(os.environ['_CONDOR_PROCNO'])
	sys.stderr.write("Timeout! Result code %d" % resultcode)
	if side == 0:
		raise TimeOutException("client")
	else:
		raise TimeOutException("server")

# vim: ts=4:sw=4
