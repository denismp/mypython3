#!/usr/bin/env jython
##################################################################################
##	gen_giblets.py
##	Python script to extract the PUKE file from a java call and to parse it to
##	generate the daemons.<host> and <MNE>.toc files and all the other giblet
##	files.
##################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	08/19/2009	Denis M. Putnam		Created.
##################################################################################

#########################################
#	Import section.
#########################################
import getopt, sys
import os, socket
from stat import *
from shutil import *
from subprocess import *
import urllib2
from urllib2 import *
from pylib.Utils.MyLogger import *
from pylib.Utils.StatusCookie import *
from pylib.Amp.AppUpdateProperties import *

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
	CONFIG['thisprogram']		= os.path.basename( sys.argv[0] )
	CONFIG['logfile'	]		= "/tmp/" + CONFIG['thisprogram'] + "_" + mytimestr + ".log"
	CONFIG['stdout'		]		= False
	CONFIG['debug'		]		= False
	CONFIG['jobname'	]		= ""
	CONFIG['ampid'		]		= ""
	CONFIG['tag_version']		= "1.0"
	CONFIG['max_was_version']	= "7.0"
	CONFIG['lib_version']		= "1.0"
	CONFIG['generic_version']	= "1.0"
	CONFIG['quasi_version']		= "1.0"
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

	CONFIG['utils']		= MyLogger( LOGFILE=CONFIG['logfile'], STDOUT=CONFIG['stdout'], DEBUG=CONFIG['debug'] );

	#CONFIG['utils'].logIt( "resetInit(): Here I am.\n" );

	CONFIG['cookie']		= StatusCookie( jobname=CONFIG['jobname'], logger=CONFIG['utils'] )
	CONFIG['work_dir']		= CONFIG['cookie'].getWorkDir()
	CONFIG['xml_file']		= CONFIG['work_dir'] + "/" + CONFIG['jobname'] + ".xml"
	CONFIG['fqdn']			= "dapp41:31854"
	CONFIG['userid']		= "appd4ec"
	CONFIG['password']		= "ss9319"
	CONFIG['master_file']	= "daemons.master"
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
	usage_string = "gen_giblets.py\n" + \
		"\t[-j, --jobname]         -- Something like QAMP_UAT0000000_090504130000i(required: default is " + CONFIG['jobname'] + ")\n" + \
		"\t[-a, --ampid]           -- ID from AMP(required: default is " + CONFIG['ampid'] + ")\n" + \
		"\t[-t, --tag_version]     -- General XML tag version to use(optional: default is " + CONFIG['tag_version'] + ")\n" + \
		"\t[-m, --max_was_version] -- max WAS XML tag version to use for component defs(optional: default is " + CONFIG['max_was_version'] + ")\n" + \
		"\t[--lib_version]         -- LIB XML tag version to use for component defs(optional: default is " + CONFIG['lib_version'] + ")\n" + \
		"\t[-g, --generic_version] -- Generic XML tag version to use for component defs(optional: default is " + CONFIG['generic_version'] + ")\n" + \
		"\t[-q, --quasi_version]   -- quasi WAS XML tag version to use for component defs(optional: default is " + CONFIG['quasi_version'] + ")\n" + \
		"\t[-l, --logfile]         -- log file(optional: default is " + CONFIG['logfile'] + ")\n" + \
		"\t[-s, --stdout]          -- stdout on.\n" + \
		"\t[-d, --debug]           -- debug on.\n" + \
		"\t[-h, --help]            -- show usage.\n\n" + \
		"gen_giblets.py --jobname QAMP_UAT0000000_090504130000i --ampid 1000350  --logfile /tmp/gen_giblets.log --stdout\n"
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
	required_opts = { 'jobname': False, 'ampid': False }
	rc = 1

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hdsj:a:t:m:g:q:l:", ["help", "debug", "stdout", "jobname=", "ampid=", "tag_version=", "max_was_version=", "lib_version=", "generic_version=", "quasi_version=", "logfile="])
	except( getopt.GetoptError, err ):
		# print help information and exit:
		print( str(err) ) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-j", "--jobname"):
			my_opts['jobname'] = a
			required_opts['jobname'] = True
		elif o in ("-a", "--ampid"):
			my_opts['ampid'] = a
			required_opts['ampid'] = True
		elif o in ("-t", "--tag_version"):
			my_opts['tag_version'] = a
		elif o in ("-m", "--max_was_version"):
			my_opts['max_was_version'] = a
		elif o in ("--lib_version"):
			my_opts['lib_version'] = a
		elif o in ("-g", "--generic_version"):
			my_opts['generic_version'] = a
		elif o in ("-q", "--quasi_version"):
			my_opts['quasi_version'] = a
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

	if( rc == 0 ):
		usage()

	#for k, v in required_opts.iteritem():
	for k, v in required_opts.items():
		if( required_opts[k] == False ):
			msg = sys.argv[0] + " Must provide: " + "--" + str( k )
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
	myMtime	= os.stat(pathname)[ST_MTIME]
	modDate = CONFIG['utils'].mktime(myMtime)
	logIt( "Python Script: " + pathname + "\n" )
	logIt( "Version Date:  " + modDate + "\n" )
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
	logIt( "Todays date:   " + mytime + "\n" )
	logIt( "                 Jobname file is: " + str( CONFIG['jobname'] ) + "\n" )
	logIt( "                   AmpID file is: " + str( CONFIG['ampid'] ) + "\n" )
	logIt( "             tag_version file is: " + str( CONFIG['tag_version'] ) + "\n" )
	logIt( "         max_was_version file is: " + str( CONFIG['max_was_version'] ) + "\n" )
	logIt( "             lib_version file is: " + str( CONFIG['lib_version'] ) + "\n" )
	logIt( "         generic_version file is: " + str( CONFIG['generic_version'] ) + "\n" )
	logIt( "           quasi_version file is: " + str( CONFIG['quasi_version'] ) + "\n" )
	logIt( "                     Log file is: " + str( CONFIG['logfile'] ) + "\n" )
	logIt( "                  Stdout flag is: " + str( CONFIG['stdout'] ) + "\n" )
	logIt( "                   Debug flag is: " + str( CONFIG['debug'] ) + "\n" )
	logIt( "               Work directory is: " + str( CONFIG['cookie'].getWorkDir() ) + "\n" )
	logIt( "              Email directory is: " + str( CONFIG['cookie'].getEmailDir() ) + "\n" )
	logIt( "              Admin directory is: " + str( CONFIG['cookie'].getWorkDir() ) + "/admin\n" )
	logIt( "             Config directory is: " + str( CONFIG['cookie'].getWorkDir() ) + "/config\n" )
	logIt( "                    PUKE file is: " + str( CONFIG['xml_file'] ) + "\n" )
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
	utils = CONFIG['utils'].logIt( msg )
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

	rVal = mkDirs()
	rVal = getThePuke()
	if( not rVal ): return 1

	###################################################
	#	Get an instance of the AppUpdateProperties
	###################################################
	myObject = AppUpdateProperties( logger=CONFIG['utils'], xml_file=CONFIG['xml_file'] )
	if( myObject ):
		rVal = myObject.writeDaemonTables( CONFIG['work_dir'] + "/config", CONFIG['master_file'] )
		logIt( "doWork(): writeDaemonTables() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeConfigFiles( CONFIG['work_dir'] + "/config" )
		logIt( "doWork(): writeConfigFiles() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeSelectedUpdateFile( CONFIG['work_dir'] )
		logIt( "doWork(): writeSelectedUpdateFile() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeTOC( CONFIG['work_dir'], "master_filelist.dat" )
		logIt( "doWork(): writeTOC() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeComponentDefinitions( CONFIG['work_dir'] + "/admin" )
		logIt( "doWork(): writeComponentDefinitions() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeAmpId( CONFIG['work_dir'] )
		logIt( "doWork(): writeAmpId() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeMne( CONFIG['work_dir'] )
		logIt( "doWork(): writeMne() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeEnv( CONFIG['work_dir'] )
		logIt( "doWork(): writeEnv() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeJobname( CONFIG['work_dir'] )
		logIt( "doWork(): writeJobname() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeCCID( CONFIG['work_dir'] )
		logIt( "doWork(): writeCCID() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeIsStageAcceptRequired( CONFIG['work_dir'] )
		logIt( "doWork(): writeIsStageAcceptRequired() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeIsRestartRequired( CONFIG['work_dir'] )
		logIt( "doWork(): writeIsRestartRequired() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeIsCleanInstallRequired( CONFIG['work_dir'] )
		logIt( "doWork(): writeIsCleanInstallRequired() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeIsMaintencePathRequired( CONFIG['work_dir'] )
		logIt( "doWork(): writeIsMaintencePathRequired() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeIsRestartAcceptRequired( CONFIG['work_dir'] )
		logIt( "doWork(): writeIsRestartAcceptRequired() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeIsCheckAcceptRequired( CONFIG['work_dir'] )
		logIt( "doWork(): writeIsCheckAcceptRequired() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeRuntimeHosts( CONFIG['work_dir'] )
		logIt( "doWork(): writeRuntimeHosts() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeNonRuntimeHosts( CONFIG['work_dir'] )
		logIt( "doWork(): writeNonRuntimeHosts() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeRestartGroups( CONFIG['work_dir'] )
		logIt( "doWork(): writeRestartGroups() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeWasAsHosts( CONFIG['work_dir'] )
		logIt( "doWork(): writeWasAsHosts() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeWasWsHosts( CONFIG['work_dir'] )
		logIt( "doWork(): writeWasWsHosts() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeWasDmgrHosts( CONFIG['work_dir'] )
		logIt( "doWork(): writeWasDmgrHosts() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writePortalPortalHosts( CONFIG['work_dir'] )
		logIt( "doWork(): writePortalPortalHosts() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writePortalDmgrHosts( CONFIG['work_dir'] )
		logIt( "doWork(): writePortalDmgrHosts() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeGenericGenericHosts( CONFIG['work_dir'] )
		logIt( "doWork(): writeGenericGenericHosts() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeAutosysDate( CONFIG['work_dir'] )
		logIt( "doWork(): writeAutosysDate() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeAutosysTime( CONFIG['work_dir'] )
		logIt( "doWork(): writeAutosysTime() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeRunAfterJobName( CONFIG['work_dir'] )
		logIt( "doWork(): writeRunAfterJobName() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeDeveloperEmail( CONFIG['work_dir'] )
		logIt( "doWork(): writeDeveloperEmail() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		hostName	= socket.gethostname()
		myBin		= ""
		if( hostName == "dideploy11" ): myBin = "dev/"
		jilCommand = "/nfs/dist/dmp/amp/" + myBin + "bin/AMP_MASTER_deploy_application -jobid " + CONFIG['jobname'] + " -ampid " + CONFIG['ampid']
		rVal = myObject.writeAutosysInsertJil( CONFIG['work_dir'], hostName, CONFIG['jobname'], CONFIG['ampid'], jilCommand )
		logIt( "doWork(): writeAutosysInsertJil() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeAutosysUpdateJil( CONFIG['work_dir'], hostName, CONFIG['jobname'], CONFIG['ampid'], jilCommand )
		logIt( "doWork(): writeAutosysUpdateJil() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeIsPortalIncluded( CONFIG['work_dir'] )
		logIt( "doWork(): writeIsPortalIncluded() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		rVal = myObject.writeIsWas5Included( CONFIG['work_dir'] )
		logIt( "doWork(): writeIsWas5Included() returned " + str( rVal ) + "\n" )
		if( not rVal ): rc = 1
		logFilesWritten( myObject )
		myObject.closeMe()
		if( not rVal ): rc = 1
	else:
		logIt( "doWork(): Unable to create and AppUpdateProperties instance.\n" )
		rc = 1
	#Endif
	if( rc == 1 ): 
		msg = "FAILURE" 
	else: 
		msg = "SUCCESS"
	logIt( "doWork(): Completed with " + str( rc ) + ":" + msg + "\n" )

	cookieMsg = CONFIG['thisprogram'] + " Completed with " + msg
	if( rc == 1 ): 
		status = "failed" 
	else: 
		status = "ok"
	CONFIG['cookie'].writeStatus( host=socket.gethostname(), app=CONFIG['thisprogram'], status=status, msg=cookieMsg )
	CONFIG['cookie'].closeMe()

	return rc
#######################################################
#	Enddef
#######################################################

#######################################################
#	logFilesWritten()
#
#	DESCRIPTION:
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def logFilesWritten(myPuke):
	"""Log the written files to the log."""
	ar = myPuke.getWrittenFiles()
	for file in ar:
		logIt( "logWrittenFiles(): " + file + "\n" )
	#Endfor
#######################################################
#	Enddef
#######################################################

#######################################################
#	getThePukeOld()
#
#	DESCRIPTION:
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def getThePukeOld():
	"""Get the Puke from AMP/WDT"""
	rc = True
	if( False ):
		home = "/nfs/home4/dmpapp/appd4ec"
		testPuke = home + "/etc/testPUKE.xml"
		try:
			copyfile( testPuke, CONFIG['xml_file'] )
		except IOError:
			logIt( "getThePuke(): Unable to copy " + testPuke + " to " + CONFIG['xml_file'] + "\n" )
			return False
		#Endtry
	else:
		pipe		= None
		fqdn		= CONFIG['fqdn']
		userid		= CONFIG['userid']
		password	= CONFIG['password']
		ampid		= CONFIG['ampid']
		work_dir	= CONFIG['work_dir']
		jobname		= CONFIG['jobname']

		############################################################
		#	Open a pipe to wget command.
		############################################################
		wgetcmd		= r"/usr/bin/wget -O - -q --http-user=" + userid + " --http-passwd=" + password + " \"http://" + fqdn + "/AmpWeb/getChangeRequests.do?EVENT=exportDeploymentConfiguration&changeRequestId=" + ampid + '"'
		logIt( "getThePuke(): trying => " + str( wgetcmd ) + "\n" )
		try:
			pipe = Popen( wgetcmd, shell=True, stdout=PIPE ).stdout
		except IOError, inst:
			logIt( "getThePuke(): wget => " + str( inst.errno ) + ":" + str( inst.strerror ) + "\n" )
			rc = False
			return rc
		#Endtry

		###########################################################
		#	Open the jobname file.
		###########################################################
		FH		= None
		myFile	= CONFIG['work_dir'] + "/" + jobname + ".xml"
		logIt( "getThePuke(): Opening " + myFile + " for write.\n" )
		try:
			FH = open( myFile, "w" )
		except IOError, inst:
			logIt( "getThePuke(): Unable to open " + myFile + " => " + str( inst.errno ) + ":" + str( inst.strerror ) + "\n" )
			rc = False
			return rc
		#Endtry

		###########################################################
		#	Read the contents of the pipe and write it to the
		#	jobname .xml file.
		###########################################################
		buffer = pipe.read()
		while( buffer ):
			debug( "getThePuke(): \n" + str( buffer ) + "\n" )
			FH.write( buffer )
			buffer = pipe.read()
		#Endif
		pipe.close()
		FH.close()
	#Endif
	return True
#######################################################
#	Enddef
#######################################################

#######################################################
#	getThePuke()
#
#	DESCRIPTION:
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def getThePuke():
	"""Get the Puke from AMP/WDT"""
	rc = True
	if( False ):
		home = "/nfs/home4/dmpapp/appd4ec"
		testPuke = home + "/etc/testPUKE.xml"
		try:
			copyfile( testPuke, CONFIG['xml_file'] )
		except IOError:
			logIt( "getThePuke(): Unable to copy " + testPuke + " to " + CONFIG['xml_file'] + "\n" )
			return False
		#Endtry
	else:
		realm			= None
		fqdn			= CONFIG['fqdn']
		userid			= CONFIG['userid']
		password		= CONFIG['password']
		ampid			= CONFIG['ampid']
		work_dir		= CONFIG['work_dir']
		jobname			= CONFIG['jobname']
		top_level_url	= "http://" + fqdn + "/AmpWeb"
		url     		= top_level_url + "/getChangeRequests.do?EVENT=exportDeploymentConfiguration&changeRequestId=" + ampid

		############################################################
		#	Open a url to get the XML data.
		############################################################
		password_mgr	= urllib2.HTTPPasswordMgrWithDefaultRealm()
		password_mgr.add_password( realm, top_level_url, userid, password )
		auth_handler	= urllib2.HTTPBasicAuthHandler( password_mgr )
		opener			= urllib2.build_opener( auth_handler )
		try:
			handle	= opener.open( url )
		except HTTPError, inst:
			logIt( "getThePuke(): URLError => " + str( inst.code ) + ":" + str( inst.msg ) + "\n" )
			logIt( "getThePuke(): URLError:headers => " + str( inst.headers ) + "\n" )
			logIt( "getThePuke(): URLError:url => " + str( inst.geturl() ) + "\n" )
			rc = False
			return rc
		#Endtry

		###########################################################
		#	Open the jobname file.
		###########################################################
		FH		= None
		myFile	= CONFIG['work_dir'] + "/" + jobname + ".xml"
		logIt( "getThePuke(): Opening " + myFile + " for write.\n" )
		try:
			FH = open( myFile, "w" )
		except IOError, inst:
			logIt( "getThePuke(): Unable to open " + myFile + " => " + str( inst.errno ) + ":" + str( inst.strerror ) + "\n" )
			rc = False
			return rc
		#Endtry

		###########################################################
		#	Read the contents of the url handle and write it to the
		#	jobname .xml file.
		###########################################################
		buffer = handle.read()
		while( buffer ):
			debug( "getThePuke(): \n" + str( buffer ) + "\n" )
			FH.write( buffer )
			buffer = handle.read()
		#Endif
		handle.close()
		FH.close()
	#Endif
	return True
#######################################################
#	Enddef
#######################################################

#######################################################
#	mkDirs()
#
#	DESCRIPTION:
#
#	PARAMETERS:
#
#	RETURN:
#######################################################
def mkDirs():
	"""Make all the working directories."""
	#####################################################
	#	Make the update directory to work in.
	#####################################################
	cookie = CONFIG['cookie']
	if( not os.access( cookie.getEmailDir(), os.F_OK ) ):
		try:
			os.makedirs( cookie.getEmailDir(), 0777 )
		except OSError:
			logIt( "main.mkDirs(): Unable to make " + cookie.getEmailDir() + ".\n" )
			return False
		#Endtry
	#Endif
	#####################################################
	#	Make the update/admin directory to work in.
	#####################################################
	adminDir = cookie.getWorkDir() + "/admin" 
	if( not os.access( adminDir, os.F_OK ) ):
		try:
			os.makedirs( adminDir, 0777 )
		except OSError:
			logIt( "main.mkDirs(): Unable to make " + adminDir + ".\n" )
			return False
		#Endtry
	#Endif
	#####################################################
	#	Make the update/config directory to work in.
	#####################################################
	configDir = cookie.getWorkDir() + "/config" 
	if( not os.access( configDir, os.F_OK ) ):
		try:
			os.makedirs( configDir, 0777 )
		except OSError:
			logIt( "main.mkDirs(): Unable to make " + configDir + ".\n" )
			return False
		#Endtry
	#Endif
	return True
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
	sys.exit( rc )
#######################################################
#	Enddef
#######################################################

#########################################
#	End
#########################################
if __name__ == "__main__":
	main()
