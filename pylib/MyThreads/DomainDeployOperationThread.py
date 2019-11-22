#!/usr/bin/env python
######################################################################################
##	DomainDeployOperationThread.py
##
##	Python module performs the following steps in a thread
##           1. Stop all runnable processes.
##           2. Make new files active.
##           3. Configure the MNE as a whole (not the WAS install).  Not the Web Servers (yet).
##           4. Configure and install the WAS app. (May involve more threading.)
##           5. Run postconfigs on all machines except web servers. (May involve more threading.)
##           6. Start the NON-WAS components.  (May involve more threading.)
##           7. Run the WAS POST SCRIPT.  (May involve more threading.)
##           8. Configure the Web Servers - start to finish.  (May involve more threading.)
##           9. Be sure all deployments went OK.  (May involve more threading.)
##           10. Perform WAS restarts.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	02/12/2010	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
import time
import random
from threading import Thread
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.DeploymentTasks.ConfigureMNE import *
from pylib.DeploymentTasks.ConfigureWAS import *
from pylib.DeploymentTasks.ConfigWebServers import *
from pylib.DeploymentTasks.MakeNewFilesActive import *
from pylib.DeploymentTasks.PostConfig import *
from pylib.DeploymentTasks.RunWasPost import *
from pylib.DeploymentTasks.StopAllRunnableProcesses import *

random.seed( time.localtime() )

class DomainDeployOperationThread( Thread ):
	"""
    DomainDeployOperationThread class extends the Thread class to perform the following steps in a thread.
    1. Stop all runnable processes.
    2. Make new files active.
    3. Configure the MNE as a whole (not the WAS install).  Not the Web Servers (yet).
    4. Configure and install the WAS app. (May involve more threading.)
    5. Run postconfigs on all machines except web servers. (May involve more threading.)
    6. Start the NON-WAS components.  (May involve more threading.)
    7. Run the WAS POST SCRIPT.  (May involve more threading.)
    8. Configure the Web Servers - start to finish.  (May involve more threading.)
    9. Be sure all deployments went OK.  (May involve more threading.)
    10. Perform WAS restarts.
	"""

	##################################################################################
	#	__init__()
	#
	#	DESCRIPTION:
	#		Class initializer.
	#
	#	PARAMETERS:
	#		See below.
	#
	#	RETURN:
	#		An instance of this class
	##################################################################################
	def __init__(
				self, 
				jobid,
				ampid,
				domain,
				statusFile,
				statusFilesHome,
				mne,
				processDict,
				hostDict,
				threadName=None,
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               jobid           - AutoSys jobid
               ampid           - AmpID
               domain          - domain.
               statusFile	   - File to store the results of the thread.
               statusFilesHome - Home directory for all the status files.
               mne	           - Mneumonic.
               processDict	   - The list of processes to stop.
               hostDict	       - The list of hosts to activate files on with their respective cleanFlag's.
               threadName      - Optional thread name.
               logger          - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		Thread.__init__(self, name=threadName)	# Initialize the super.
		self.logger		= logger
		self.domain		= domain
		self.statusFile	= statusFile
		self.statusFilesHome	= statusFilesHome
		self.mne		= mne
		self.jobid		= jobid
		self.ampid		= ampid
		self.processDict= processDict
		self.hostDict	= hostDict
		self.threadName = threadName
		self.status		= True
		self.message	= "\n"
		self.logMySelf()
		self.validate()

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	validate()
	#
	#	DESCRIPTION:
	#		Validate the parameters and calculated values.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		True for valid.
	##################################################################################
	def validate(self):
		"""Validate the parameters and calculated values.
           PARAMETERS:

           RETURN:
               True for valid or False.
		"""
		rVal = False
		#return rVal
		return True

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	logMySelf()
	#
	#	DESCRIPTION:
	#		Log myself.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def logMySelf(self, debugOnly=True):
		"""Log myself.
        PARMETERS:
            debugOnly is either True or False.  A value of True will only log if the
            logger's debug flag is set.
        """

		myAttrs = dir( self )
		for attr in myAttrs:
			try:
				if re.search( '__doc__',  attr ): continue
				if re.search( '__module__',  attr ): continue
				if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
				if re.search( 'instance', str( getattr( self, attr ) ) ): continue
				if( debugOnly == True ):
					self.debug( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				else:
					self.logIt( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				#Endif
			except AttributeError as e:
				continue
			#Endtry
		#Endfor
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	logIt()
	#
	#	DESCRIPTION:
	#		Write a message to the log and possibly stdout.
	#
	#	PARAMETERS:
	#		msg - what you want to log.
	#
	#	RETURN:
	##################################################################################
	def logIt(self, msg):
		"""Write a message to the log and possibly stdout."""

		if( self.logger ): self.logger.logIt( msg )

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	debug()
	#
	#	DESCRIPTION:
	#		Write a message to the log and possibly stdout.
	#
	#	PARAMETERS:
	#		msg - what you want to log.
	#
	#	RETURN:
	#################################################################################
	def debug(self, msg):
		"""Write a message to the log and possibly stdout."""

		if( self.logger ): self.logger.debug( msg )

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	closeMe()
	#
	#	DESCRIPTION:
	#		Closes this instance.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def closeMe(self):
		"""Closes this instance."""
		self.debug( __name__ + ".closeMe(): called.\n" )
		#Endif
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	__del__()
	#
	#	DESCRIPTION:
	#		Really closes this instance.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def __del__(self):
		"""Closes this instance."""
		#self.logIt( __name__ + ".__del__(): called.\n" )
		self.closeMe()
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	run()
	#
	#	DESCRIPTION:
	#		Override the Thread run() method with what we want to do.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def run(self):
		"""Override the Thread run() method with what we want to do.
           This method performs the following steps for a single domain in a main thread that starts other threads:
           1. Stop all runnable processes.
           2. Make new files active.
           3. Configure the MNE as a whole (not the WAS install).  Not the Web Servers (yet).
           4. Configure and install the WAS app. (May involve more threading.)
           5. Run postconfigs on all machines except web servers. (May involve more threading.)
           6. Start the NON-WAS components.  (May involve more threading.)
           7. Run the WAS POST SCRIPT.  (May involve more threading.)
           8. Configure the Web Servers - start to finish.  (May involve more threading.)
           9. Be sure all deployments went OK.  (May involve more threading.)
           10. Perform WAS restarts.
           PARAMETERS:

           RETURN:
		"""
		self.debug( __name__ + ".run(): self.jobid=" + str( self.jobid ) + "\n" )
		self.debug( __name__ + ".run(): self.ampid=" + str( self.ampid ) + "\n" )
		self.debug( __name__ + ".run(): self.domain=" + str( self.domain ) + "\n" )
		self.debug( __name__ + ".run(): self.threadName=" + str( self.threadName ) + "\n" )
		self.debug( __name__ + ".run(): self.processDict=" + str( self.processDict ) + "\n" )
		self.debug( __name__ + ".run(): self.hostDict=" + str( self.hostDict ) + "\n" )
		self.debug( __name__ + ".run(): self.mne=" + str( self.mne ) + "\n" )
		self.debug( __name__ + ".run(): self.statusFile=" + str( self.statusFile ) + "\n" )
		self.debug( __name__ + ".run(): self.statusFilesHome=" + str( self.statusFilesHome ) + "\n" )

		stopRunnableProcesses = StopAllRunnableProcesses( 
														self.jobid, 
														self.ampid, 
														self.domain, 
														self.mne, 
														'/tmp/stop_all_runnable_processes.' + str( self.domain ), 
														self.processDict, 
														logger=self.logger 
														)
		self.logIt( __name__ + ".run(): stopRunnableProcesses=" + str( stopRunnableProcesses ) + "\n" )
		stopRunnableProcesses.stopProcesses()
		self.appendMsg( __name__ + ".run(): " + str( stopRunnableProcesses.message ) + '\n' )
		stopRunnableProcesses.closeMe()

		makeNewFilesActive = MakeNewFilesActive( 
														self.jobid, 
														self.ampid, 
														self.domain, 
														self.mne, 
														self.statusFilesHome, 
														self.hostDict, 
														logger=self.logger 
														)
		self.logIt( __name__ + ".run(): makeNewFilesActive=" + str( makeNewFilesActive ) + "\n" )
		makeNewFilesActive.makeFilesActive()
		self.appendMsg( __name__ + ".run(): " + str( makeNewFilesActive.message ) + '\n' )
		makeNewFilesActive.closeMe()

		configureMNE = ConfigureMNE( 
														self.jobid, 
														self.ampid, 
														self.domain, 
														self.mne, 
														self.statusFilesHome, 
														self.processDict, 
														logger=self.logger 
														)
		self.logIt( __name__ + ".run(): configureMNE=" + str( configureMNE ) + "\n" )
		configureMNE.configureMNE()
		self.appendMsg( __name__ + ".run(): " + str( configureMNE.message ) + '\n' )
		configureMNE.closeMe()

		self.status = True
		self.appendMsg( __name__ + ".run(): DEPLOY Completed successfully for " + str( self.threadName ) + "\n" )

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	appendMsg()
	#
	#	DESCRIPTION:
	#		Append the given message to the message buffer.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def appendMsg(self,msg):
		"""Append the given message to the message buffer.
           PARAMETERS:
               msg -- string to append to the message buffer.

           RETURN:
		"""
		self.message += str( msg )

	##################################################################################
	#Enddef
	##################################################################################

######################################################################################
#Endclass
######################################################################################

#########################################################################
#	For testing.
#########################################################################
def main():
	myLogger	= MyLogger( LOGFILE="/tmp/DomainDeployOperationThread.log", STDOUT=True, DEBUG=True )
	mne			= 'DMP'
	statusFile	= '/tmp/deploy_DOMAIN_components.MYDOMAIN'
	statusFilesHome	= '/tmp'
	jobid		= 'SomeAutoSysJobId'
	ampid		= 'SomeAmpId'

	threadList = []
	for mythread in range( 0, 3 ):
		processDict	= dict()
		processDict[ 'host1' ] = [ 'comp' + str( mythread + 1 ), 'comp' + str( mythread + 2 ), 'comp' + str( mythread + 3 ) ]
		processDict[ 'host2' ] = [ 'comp' + str( mythread + 1 ), 'comp' + str( mythread + 2 ), 'comp' + str( mythread + 3 ) ]
		processDict[ 'host3' ] = [ 'comp' + str( mythread + 1 ), 'comp' + str( mythread + 2 ), 'comp' + str( mythread + 3 ) ]
		hostDict	= dict()
		hostDict[ 'host1' ] = [ False ]
		hostDict[ 'host2' ] = [ False ]
		hostDict[ 'host3' ] = [ False ]
		current = DomainDeployOperationThread( 
											jobid,
											ampid,
											'MYDOMAIN' + str( mythread ),
											statusFile + str( mythread ),
											statusFilesHome,
											mne,
											processDict,
											hostDict,
											threadName='MAIN_MYDOMAIN' + str( mythread ), 
											logger=myLogger 
											)
		threadList.append( current )
		current.start()
	#Endfor

	################################
	#	Join on all the threads.
	################################
	for mythread in threadList:
		mythread.join()
		myLogger.logIt( "main(): " + str(mythread) + "\n" )
		myLogger.logIt( "main(): " + str( mythread.message ) + '\n' )
		mythread.closeMe()
	#Endfor
	
	##################################################################################
	#Enddef
	##################################################################################

######################################################################################
#   End
######################################################################################
if __name__ == "__main__":
	main()

