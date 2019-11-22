#!/usr/bin/env jython
######################################################################################
##	ProcessExecutionManager.py
##
##	Python module for ProcessExecution attributes.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	01/25/2010	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
import random
import time
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.AdminClient import *
from pylib.Was.ConfigService import *
from pylib.Was.AttributeUtils import *
from pylib.Was.TemplateListManager import *
from pylib.Was.JDBCProviderManager import *
from java.lang import NullPointerException
from java.lang import NoClassDefFoundError
from javax.management import InstanceNotFoundException
from javax.management import MalformedObjectNameException
from javax.management import ObjectName
from javax.management import AttributeList
from javax.management import Attribute
from jarray import array
from java.lang import String
from java.lang import Object
import java.util.ArrayList
from java.util import ArrayList

import com.ibm.websphere.security.WebSphereRuntimePermission as WebSphereRuntimePermission
import com.ibm.websphere.security.auth.WSLoginFailedException as WSLoginFailedException
import com.ibm.ws.security.util.InvalidPasswordDecodingException as InvalidPasswordDecodingException
import com.ibm.websphere.management.exception.ConnectorException as ConnectorException

class ProcessExecutionManager( AttributeUtils ):
	"""
    ProcessExecutionManager class that contains ProcessExecution management methods.
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
				adminClient,
				configService,
				templateListManager,
				scope,
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               adminClient   - instance of the pylib.Was.AdminClient class.
               configService - instance of the pylib.Was.ConfigService class.
               templateListManager - instance of the pylib.Was.TemplateListManager class.
			   scope         - Something like one of:
                                  "Cell=ServicesA:Node=node_ServicesA_01:Server=as_was7test_01"
                                  "Cell=ServicesA:Node=node_ServicesA_01"
                                  "Node=node_ServicesA_01:Server=as_was7test_01"
                                  "Node=node_ServicesA_01"
                                  "Cell=ServicesA:Cluster=cl_was7test_a"
                                  "Cluster=cl_was7test_a"
               logger        - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		self.adminClient			= adminClient
		self.configService			= configService
		self.templateListManager	= templateListManager
		self.logger					= logger
		AttributeUtils.__init__( self, configService, scope, type='ProcessExecution', logger=self.logger )
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
				if re.search( 'attributes',  attr ): continue
				if re.search( '__doc__',  attr ): continue
				if re.search( '__module__',  attr ): continue
				if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
				if re.search( 'instance', str( getattr( self, attr ) ) ): continue
				if( debugOnly == True ):
					self.debug( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				else:
					self.logIt( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				#Endif
			except AttributeError, e:
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
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	__del__()
	#
	#	DESCRIPTION:
	#		Closes this instance.
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
	#	saveSession()
	#
	#	DESCRIPTION:
	#		Save the current WebSphere session.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def saveSession(self,overwriteOnConflict=False):
		"""Save the current WebSphere sesssion.
		   PARAMETERS:
		       overwriteOnConflict -- default is False
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".saveSession(): called.\n" )
		self.debug( __name__ + ".saveSession(): overwriteOnConflict=" + str( overwriteOnConflict ) + ".\n" )
		self.logIt( __name__ + ".saveSession(): Saving session=" + str( self.configService.session.toString() ) + ".\n" )
		self.configService.save( self.configService.session, overwriteOnConflict )
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	modifyProcessExecution()
	#
	#	DESCRIPTION:
	#		Modify the ProcessExecution attributes.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifyProcessExecution( 
							self, 
							processPriority=20,
							runInProcessGroup=0,
							runAsUser='',
							runAsGroup='',
							umask='022'
							):
		"""Modify the ProcessExecution attributes.
		   PARAMETERS:
		       processPriority   -- Operating system priority for the process. Only root users can change this value.
		       runInProcessGroup -- The process group attribute allows the assignment of a process to a specific 
                                    process group. This is useful for doing things such as processor partitioning. 
                                    The sysadmins can assign a process group to run on say 6 of 12 processors 
                                    and so on. The default of 0 tells it to not assign it to any specific group.
		       runAsUser         -- Runs the process as a specific user.
		       runAsGroup        -- Runs the process as a member of a specific group.
		       umask             -- The user mask that the process runs under (the file-mode permission mask).
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifyProcessExecution(): processPriority=" + str( processPriority ) + "\n" )
		self.debug( __name__ + ".modifyProcessExecution(): runInProcessGroup=" + str( runInProcessGroup ) + "\n" )
		self.debug( __name__ + ".modifyProcessExecution(): runAsUser=" + str( runAsUser ) + "\n" )
		self.debug( __name__ + ".modifyProcessExecution(): runAsGroup=" + str( runAsGroup ) + "\n" )
		self.debug( __name__ + ".modifyProcessExecution(): umask=" + str( umask ) + "\n" )

		rVal = True

		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:

			########################################################
			#	Do the scalar attributes first.
			########################################################
			self.debug( __name__ + ".modifyProcessExecution(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".modifyProcessExecution(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the ProcessExecution AttributeList
			########################################################
			processExecutionAttributeList	= self.configService.getAttributes( self.configService.session, configObject, None, True )

			self.debug( __name__ + ".modifyProcessExecution(): BEFORE processExecutionAttributeList=" + str( processExecutionAttributeList ) + "\n" )
			self.debug( __name__ + ".modifyProcessExecution(): BEFORE processExecutionAttributeList type=" + str( type( processExecutionAttributeList ) ) + "\n" )

			#######################################################
			#	Set the scalar ProcessExecution AttributeList values.
			#######################################################
			self.configService.configServiceHelper.setAttributeValue( processExecutionAttributeList, 'processPriority', int( processPriority ) )
			self.configService.configServiceHelper.setAttributeValue( processExecutionAttributeList, 'runInProcessGroup', int( runInProcessGroup ) )
			self.configService.configServiceHelper.setAttributeValue( processExecutionAttributeList, 'runAsUser', str( runAsUser ) )
			self.configService.configServiceHelper.setAttributeValue( processExecutionAttributeList, 'runAsGroup', str( runAsGroup ) )
			self.configService.configServiceHelper.setAttributeValue( processExecutionAttributeList, 'umask', str( umask ) )
			self.debug( __name__ + ".modifyProcessExecution(): AFTER processExecutionAttributeList=" + str( processExecutionAttributeList ) + "\n" )
			####################################################################
			#	Save the processExecutionAttributeList to the current session.
			####################################################################
			self.configService.setAttributes( self.configService.session, configObject, processExecutionAttributeList )
		#Endfor

		if rVal: self.refresh()
		return rVal
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
	myLogger	= MyLogger( LOGFILE="/tmp/ProcessExecutionManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/ProcessExecutionManager.log", STDOUT=True, DEBUG=False )
	#adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1" )
	adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1", cellName='cellA' )
	myLogger.logIt( "main(): Started...\n" )
	try:
		myclient	= adminObject.createSOAPDefault()
		results		= adminObject.getResults()
		#adminObject.logResults( results )
	except Exception, e:
		myLogger.logIt( "main(): " + str(e) + "\n" )
		myLogger.logIt( "main(): Unable to connect to the AdminClient().  Make sure that the WebSphere Server Manager is running.\n" )
		raise
	#Endtry
	cellName	= "ServicesA"
	nodeName	= "node_ServicesA_01"
	serverName	= "as_ServicesA_a01"
	clusterName	= "cl_ServicesA_a"
	jdbcProvider= "OracleJdbcDriverXA"
	dataSource	= "ForOracleXAJF"
	template	= "DataSoure_ora_6"

	#myscope			= "Node=" + nodeName + ":ServerIndex:ServerEntry=" + serverName
	#myscope			= "Node=" + nodeName + ":ServerIndex:ServerEntry=" + serverName
	#myscope			= "Cell=" + cellName + ":Node=" + nodeName + ":Server=" + serverName
	myscope				= "Node=" + nodeName + ":Server=" + serverName
	configService 		= ConfigService( adminClient=myclient, logger=myLogger )
	templateListManager	= TemplateListManager( configService, type="ProcessExecution", logger=myLogger )
	myProcessExecutionManager	= ProcessExecutionManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in myProcessExecutionManager.attributesList:
		myProcessExecutionManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myProcessExecutionManager.attributesList:
		myProcessExecutionManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myProcessExecutionManager.attributesList:
			myProcessExecutionManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	myProcessExecutionManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/ProcessExecution.tsv" )

	########################################################
	#	Make changes.
	########################################################
	rc = myProcessExecutionManager.modifyProcessExecution( 
							processPriority=20,
							runInProcessGroup=0,
							runAsUser='appd4ec',
							runAsGroup='dmpapp',
							umask='022'
							)

	if rc: myProcessExecutionManager.saveSession( False )

	#for mylist in myProcessExecutionManager.attributesList:
	#	myProcessExecutionManager.deepLogOfAttributes( mylist )
	##Endfor
	configService.closeMe()
	myProcessExecutionManager.closeMe()
	adminObject.closeMe()
	myLogger.logIt( "main(): Finished.\n" )
	##################################################################################
	#Enddef
	##################################################################################

######################################################################################
#   End
######################################################################################
if __name__ == "__main__":
	main()
