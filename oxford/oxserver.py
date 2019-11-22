#!/usr/bin/env python
##################################################################################
##	oxserver.py
##	Python script to:
##  * accept the connection
##  * read a 32 bit integer, NNNN (0-9999), in network order
##  * read 2000 bytes and discard them
##  * check if the server side file $PWD/NNNN exists
##  * if the file exists, return its content to the client,
##    or socket EOF otherwise. Note that files can be of any
##    size and type.
##  * update a single file (eg, $PWD/counts), viewable while
##    the server runs, with the number of times each file
##    NNNN has been requested;

##################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	03/30/2011	Denis M. Putnam		Created.
##################################################################################

#########################################
#	Import section.
#########################################
import getopt, sys #@UnusedImport
import os, socket #@UnusedImport
from stat import *  #@UnusedWildImport
from pylib.Utils.MyLogger import * #@UnusedWildImport
#from pylib.Utils.MySocket import * #@UnusedWildImport
from pylib.Tasks.FileTask import * #@UnusedWildImport

#########################################
#	Global variables.
#########################################
CONFIG = {}

#########################################
#	Function definitions.
#########################################

#######################################################
#	initialize()
#
#	DESCRIPTION:
#		This function initializes this program.
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def initialize():
	"""Initialize this module."""
	mytime = time.localtime()
	mytimestr = time.strftime("%Y%m%d-%H_%M_%S", mytime);

	#CONFIG['logfile'	]		= "/tmp/mywas.log"
	CONFIG['thisprogram'] = os.path.basename(sys.argv[0])
	CONFIG['hostname'	] = ''
	CONFIG['port'		] = 50007
	CONFIG['logfile'	] = "/tmp/" + CONFIG['thisprogram'] + "_" + mytimestr + ".log"
	#CONFIG['logfile'	]		= CONFIG['thisprogram'] + ".log"
	CONFIG['stdout'	 	] = False
	CONFIG['debug'	  	] = False

#######################################################
#	Enddef
#######################################################

#######################################################
#	resetInit()
#
#	DESCRIPTION:
#		Reset the initialized values based on what
#		the user specified on the command line.
#
#	PARAMETERS:
#		myopts - a dictionary of the command line
#
#	RETURN:
#######################################################
def resetInit(myopts):
	"""Reset the initialize values based on what the user specified on the command line."""
	for my_opt in myopts.keys():
		CONFIG[my_opt] = myopts[my_opt]
		#print( my_opt + '=' + str( CONFIG[my_opt] ) )
	#Endfor

	CONFIG['utils'] = MyLogger(LOGFILE=CONFIG['logfile'], STDOUT=CONFIG['stdout'], DEBUG=CONFIG['debug']);

	#CONFIG['utils'].logIt( "resetInit(): Here I am.\n" );

#######################################################
#	Enddef
#######################################################

#######################################################
#	usage()
#
#	DESCRIPTION:
#		Display the usage of this program to standard
#		output.
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def usage():
	"""Display the command line usage."""
	usage_string = "oxserver.py\n" + \
		"\t[-p, --port]     -- Something like 50007(optional: default is " + str(CONFIG['port']) + ")\n" + \
		"\t[-l, --logfile]  -- log file(optional: default is " + str(CONFIG['logfile']) + ")\n" + \
		"\t[-s, --stdout]   -- stdout on.\n" + \
		"\t[-d, --debug]    -- debug on.\n" + \
		"\t[-h, --help]     -- show usage.\n\n" + \
		"oxserver.py --port 9999 --logfile /tmp/oxserver.log --stdout\n"
	print(usage_string)
#######################################################
#	Enddef
#######################################################

#######################################################
#	getCmdOptions()
#
#	DESCRIPTION:
#		Get the command line options and store them
#		into the CONFIG dictionary.
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def getCmdOptions():
	"""Get the command line arguments."""
	#print( "getCmdOptions() entered...\n )"
	my_opts = {}
	err = None
	required_opts = { 'port': True, 'help': True, 'debug': True, 'stdout': True, 'logfile': True }
	rc = 1

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hdsp:l:", ["help", "debug", "stdout", "port=", "logfile="]) #@UnusedVariable
	except(getopt.GetoptError, err):
		# print help information and exit:
		print(str(err)) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-p", "--port"):
			my_opts['port'] = a
			required_opts['port'] = True
		elif o in ("-l", "--logfile"):
			my_opts['logfile'] = a
		elif o in ("-s", "--stdout"):
			my_opts['stdout'] = True
		elif o in ("-d", "--debug"):
			my_opts['debug'] = True
		else:
			rc = 0
			assert False, "unhandled option"
		#Endif
	#Endfor

	if(rc == 0):
		usage()

	#for k, v in required_opts.iteritem():
	for k, v in required_opts.items(): #@UnusedVariable
		if(required_opts[k] == False):
			msg = sys.argv[0] + " Must provide: " + "--" + str(k)
			print(msg)
			rc = 0
		#Endif
	#Endfor

	if(rc == 0):
		usage()
		sys.exit(2)
	#Endif

	resetInit(my_opts)
#######################################################
#	Enddef
#######################################################

#######################################################
#	printVersionInfo()
#
#	DESCRIPTION:
#		Print the version and other information about
#		this program.
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def printVersionInfo():
	"""Print the version and other information about this program."""
	#pass
	pathname = sys.argv[0]
	myMtime = os.stat(pathname)[ST_MTIME]
	modDate = CONFIG['utils'].mktime(myMtime)
	logIt("Python Script: " + pathname + "\n")
	logIt("Version Date:  " + modDate + "\n")
#######################################################
#	Enddef
#######################################################

#######################################################
#	printInfo()
#
#	DESCRIPTION:
#		Print the detailed information about 
#		this program.
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def printInfo():
	"""Print the detailed information about this program."""
	utils = CONFIG['utils']
	mytime = utils.mytime()
	logIt("Todays date:   " + mytime + "\n")
	logIt("          Port is: " + str(CONFIG['port']) + "\n")
	logIt("      Log file is: " + str(CONFIG['logfile']) + "\n")
	logIt("   Stdout flag is: " + str(CONFIG['stdout']) + "\n")
	logIt("    Debug flag is: " + str(CONFIG['debug']) + "\n")
#######################################################
#	Enddef
#######################################################

#######################################################
#	logIt()
#
#	DESCRIPTION:
#		Logs the given message.
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def logIt(msg):
	"""Logs the given message."""
	utils = CONFIG['utils'].logIt(msg) #@UnusedVariable
#######################################################
#	Enddef
#######################################################

#######################################################
#	debug()
#
#	DESCRIPTION:
#		Logs the given message.
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def debug(msg):
	"""Logs the given message."""
	if(CONFIG['debug']):
		logIt(msg)
#######################################################
#	Enddef
#######################################################

#######################################################
#	doWork()
#
#	DESCRIPTION:
#		This function does all work for this program.
#
#	PARAMETERS:
#
#	RETURN:
#		0 for success or non-zero.
#######################################################
def doWork():
	"""Do all the real work for this program."""
	#rVal	= True
	rc = 0
	printInfo()
	statusFileHome	 = '/tmp'
	myFileTask 		 = FileTask(
							port=CONFIG['port'],
							statusFileHome=statusFileHome,
							logger=CONFIG['utils']
							)
	myFileTask.fileTask(timeout=None)
	#logIt('main(): ' + str(myFileTask.message))

	return rc

#######################################################
#	Enddef
#######################################################

#######################################################
#	cleanUp()
#
#	DESCRIPTION:
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def cleanUp():
	"""Do any clean up required for this program."""
	pass
#######################################################
#	Enddef
#######################################################

#######################################################
#	main()
#
#	DESCRIPTION:
#		The entry point into this program.
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def main():
	"""The entry point into this program."""
	#print( "main() entered..." )
	initialize()
	getCmdOptions()
	printVersionInfo()

	rc = doWork()

	cleanUp()
	sys.exit(rc)
#######################################################
#	Enddef
#######################################################

#########################################
#	End
#########################################
if __name__ == "__main__":
	main()
