#!/usr/bin/env jython
##################################################################################
##	setTrace.py
##	Python script privides the 
##################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	11/04/2009	Denis M. Putnam		Created.
##################################################################################

#########################################
#	Import section.
#########################################
import getopt, sys
import os, socket
from stat import *
from shutil import *
from subprocess import *
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.WasOps import *
from pylib.Was.AdminClient import *
from pylib.Was.ConfigService import *
#from pylib.Was.WasSession import *
from com.ibm.websphere.management import Session
from javax.management import Attribute
from javax.management import AttributeList
from javax.management import ObjectName
from  com.ibm.websphere.management.configservice import ConfigServiceHelper
from java.lang import String

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
	mytimestr = time.strftime("%Y%m%d-%H:%M:%S",mytime);

	#CONFIG['logfile'	]		= "/tmp/mywas.log"
	CONFIG['myutils'	]		= MyUtils()
	CONFIG['status'		]		= 0
	#try:
	#	CONFIG['thisprogram']		= os.path.basename( sys.argv[0] )
	#except IndexError, e:
	#	CONFIG['thisprogram']		= 'setTrace.py'
	##Endif
	CONFIG['thisprogram']		= 'setTrace.py'
	#print "CONFIG['thisprogram']=" + CONFIG['thisprogram']
	CONFIG['logfile'	]		= "/tmp/" + CONFIG['thisprogram'] + "_" + mytimestr + ".log"
	CONFIG['stdout'		]		= False
	CONFIG['debug'		]		= False
	CONFIG['action'		]		= "byCluster"
	CONFIG['entity_name'	]	= "cl_was6tools"
	CONFIG['domain'		]		= "V6_DEV"
	CONFIG['myid'		]		= os.getlogin()
	if CONFIG['myid'] == 'root':
		CONFIG['logfile']		= '/dmp/logs/admin/' + str( CONFIG['thisprogram'] ) + '.log'
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

	CONFIG['logger']		= MyLogger( LOGFILE=CONFIG['logfile'], STDOUT=CONFIG['stdout'], DEBUG=CONFIG['debug'] );

	#CONFIG['logger'].logIt( "resetInit(): Here I am.\n" );

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
	usage_string = "setTrace.py\n" + \
		"\t[-l, --logfile]      -- log file(optional: default is " + CONFIG['logfile'] + ")\n" + \
		"\t[-s, --stdout]       -- stdout on.\n" + \
		"\t[-d, --debug]        -- debug on.\n" + \
		"\t[-h, --help]         -- show usage.\n\n" + \
		"setTrace.py --logfile /tmp/setTrace.log --stdout\n"
	print( usage_string )
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
	required_opts = { }
	rc 			= 1
	INDEX		= 1

	INDEX = CONFIG['myutils'].calcArgsvIndex( sys.argv[0], CONFIG['thisprogram'] )
	#print "INDEX=" + str( INDEX )

	#####################################################
	#	Process the command line arguments.
	#####################################################
	try:
		opts, args = getopt.getopt(sys.argv[INDEX:], "hdsl:", ["help", "debug", "stdout", "logfile="])
	except getopt.GetoptError, err:
		# print help information and exit:
		print( str(err) ) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	#Endtry

	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-l", "--logfile"):
			my_opts['logfile'] = a
		elif o in ("-s", "--stdout"):
			my_opts['stdout'] = True
		elif o in ("-d", "--debug"):
			my_opts['debug'] = True
		else:
			rc = 0
			print "o=" + str( o )
			print "a=" + str( a )
			assert False, "unhandled option"
		#Endif
	#Endfor

	if( rc == 0 ):
		usage()

	for k, v in required_opts.items():
		if( required_opts[k] == False ):
			#msg = sys.argv[0] + " Must provide: " + "--" + str( k )
			msg = " Must provide: " + "--" + str( k )
			print( msg )
			rc = 0
		#Endif
	#Endfor

	if( rc == 0 ):
		usage()
		sys.exit(2)
	#Endif

	resetInit( my_opts )
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
	if pathname == CONFIG['thisprogram']:
		myMtime	= os.stat(pathname)[ST_MTIME]
		modDate = CONFIG['logger'].mktime(myMtime)
		logIt( "Python Script: " + pathname + "\n" )
		logIt( "Version Date:  " + modDate + "\n" )
	else:
		logIt( "Python Script: " + CONFIG['thisprogram'] + "\n" )
	#Endif
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
	logger = CONFIG['logger']
	mytime = logger.mytime()
	logIt( "Todays date:   " + mytime + "\n" )
	logIt( "          My ID is: " + str( CONFIG['myid'] ) + "\n" )
	logIt( "       Log file is: " + str( CONFIG['logfile'] ) + "\n" )
	logIt( "    Stdout flag is: " + str( CONFIG['stdout'] ) + "\n" )
	logIt( "     Debug flag is: " + str( CONFIG['debug'] ) + "\n" )
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
	logger = CONFIG['logger'].logIt( msg )
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
	if( CONFIG['debug'] ):
		logIt( msg )
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
	rVal	= True
	rc		= 0
	printInfo()

	wasAdminClient	= AdminClient( hostname="dilabvirt31-v1", logger=CONFIG['logger'] )
	myclient		= wasAdminClient.createSOAPDefault()

	configService	= ConfigService( adminClient=myclient, logger=CONFIG['logger'] )
	session			= Session()

	# query to get dmgr
	dmgr			= configService.resolve( session, "Node=cell101N2:Server=as_cell101a_01" )[0]
	
	# query to get the trace service component in dmgr.
	#pattern			= configService.configServiceHelper.createObjectName( None, "TraceService" )
	pattern			= ConfigServiceHelper.createObjectName( None, "TraceService" )
	traceService	= ObjectName( configService.queryConfigObjects( session, dmgr, pattern, None )[0].toString() )
	
	# get the current dmgr's trace specification.
	trace			= configService.getAttribute( session, traceService, "startupTraceSpecification" )
	print "trace is " + str( trace )

	# set the dmgr's trace specification to new value.
	newTrace		= String( "*=all=enabled" )
	#newTrace		= String( "*=info" )
	attrList		= AttributeList()
	attrList.add( Attribute( "startupTraceSpecification", newTrace ) )
	configService.setAttributes( session, traceService, attrList )
	newTrace		= String( configService.getAttribute( session, traceService, "startupTraceSpecification" ) )

	print "new trace is " + str( newTrace )

	## save the chanage.
	configService.save( session, False )

	# set it back.
	#configService.configServiceHelper.setAttributeValue( attrList, "startupTraceSpecification", trace )
	ConfigServiceHelper.setAttributeValue( attrList, "startupTraceSpecification", trace )
	configService.setAttributes( session, traceService, attrList )
	newTrace = configService.getAttribute( session, traceService, "startupTraceSpecification" )
	print "trace is set back to " + str( newTrace )
	configService.save( session, False )

	configService.discard( session )

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
	if CONFIG['status'] != 0:
		logIt( "cleanUp(): " + CONFIG['thisprogram'] + " failed.\n" )
	else:
		logIt( "cleanUp(): " + CONFIG['thisprogram'] + " successful.\n" )
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
	sys.exit( rc )
#######################################################
#	Enddef
#######################################################

#########################################
#	End
#########################################
if __name__ == "__main__":
	main()
