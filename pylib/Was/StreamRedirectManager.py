#!/usr/bin/env jython
######################################################################################
##	StreamRedirectManager.py
##
##	Python module for StreamRedirectManager attributes.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	01/27/2010	Denis M. Putnam		Created.
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

class StreamRedirectManager( AttributeUtils ):
	"""
    StreamRedirectManager class that contains StreamRedirect methods.
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
               adminClient         - instance of the pylib.Was.AdminClient class.
               configService       - instance of the pylib.Was.ConfigService class.
               templateListManager - instance of the pylib.Was.TemplateListManager class.
			   scope               - Something like:
                                       "Node=node_ServicesA_01:Server=as_was7test_01"
               logger              - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		self.adminClient			= adminClient
		self.configService			= configService
		self.templateListManager	= templateListManager
		self.logger					= logger
		AttributeUtils.__init__( self, configService, scope, type='StreamRedirect', logger=self.logger )
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
	#	modifyStreamRedirect()
	#
	#	DESCRIPTION:
	#		Modify the StreamRedirect attributes.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifyStreamRedirect( 
							self, 
							currentFileName='${SERVER_LOG_ROOT}/SystemOut.log',
							fileName='${SERVER_LOG_ROOT}/SystemOut.log',
							rolloverType='SIZE',
							maxNumberOfBackupFiles=5,
							rolloverSize=1,
							baseHour=24,
							rolloverPeriod=24,
							formatWrites=True,
							messageFormatKind='BASIC',
							suppressWrites=False,
							suppressStackTrace=False
							):
		"""Modify the StreamRedirect attributes.
		   PARAMETERS:
		       currentFileName        -- The current name of the file that you wish to change.
		       fileName               -- Specify the name of the file to which the stream should be redirected. 
		                                 This will be the new name of the file.  If you don't wish to change it,
		                                 then make it the same name as the currentFileName.
		       rolloverType           -- Indicate what type of rollover algorithm is in effect.
		                                 Values are 'NONE', 'SIZE', 'TIME', or 'BOTH'.
		       maxNumberOfBackupFiles -- Number of archive files.  Range is 1 through 200.
		       rolloverSize           -- Specify the size in Megabytes for size-based rollover.
		       baseHour               -- Specify the hours at which time-based rollover starts. 
		       rolloverPeriod         -- Specify the time-based rollover period.
		       formatWrites           -- Specify whether writes should be formatted like Websphere log entry. 
		       messageFormatKind      -- The desired format for messages. Valid values include 'BASIC' and 'ADVANCED'. 
                                         Default is 'BASIC'.
		       suppressWrites         -- Specify whether writes to this stream should be suppressed.
		       suppressStackTrace     -- Specify if stack traces in the messages should be replaced by the exception 
                                         message only. Default is false. (no suppression) 
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifyStreamRedirect(): fileName=" + str( fileName ) + "\n" )
		self.debug( __name__ + ".modifyStreamRedirect(): rolloverType=" + str( rolloverType ) + "\n" )
		self.debug( __name__ + ".modifyStreamRedirect(): maxNumberOfBackupFiles=" + str( maxNumberOfBackupFiles ) + "\n" )
		self.debug( __name__ + ".modifyStreamRedirect(): rolloverSize=" + str( rolloverSize ) + "\n" )
		self.debug( __name__ + ".modifyStreamRedirect(): baseHour=" + str( baseHour ) + "\n" )
		self.debug( __name__ + ".modifyStreamRedirect(): rolloverPeriod=" + str( rolloverPeriod ) + "\n" )
		self.debug( __name__ + ".modifyStreamRedirect(): formatWrites=" + str( formatWrites ) + "\n" )
		self.debug( __name__ + ".modifyStreamRedirect(): messageFormatKind=" + str( messageFormatKind ) + "\n" )
		self.debug( __name__ + ".modifyStreamRedirect(): suppressWrites=" + str( suppressWrites ) + "\n" )
		self.debug( __name__ + ".modifyStreamRedirect(): suppressStackTrace=" + str( suppressStackTrace ) + "\n" )

		rVal = False

		############################################################
		#	For all our configuration Objects within the scope,
		#	find the matching fileName and modify the attributes.
		############################################################
		for configObject in self.configObjects:
			self.debug( __name__ + ".modifyStreamRedirect(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".modifyStreamRedirect(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the StreamRedirect AttributeList
			########################################################
			#pArgs = array( ['threadPools'], java.lang.String )
			pArgs = None
			propertyAttributeList	= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )
			myFileName	= self.configService.configServiceHelper.getAttributeValue( propertyAttributeList, 'fileName' )

			if myFileName != currentFileName: continue

			self.logIt( __name__ + ".modifyStreamRedirect(): Found " + str( currentFileName ) + "\n" )

			self.debug( __name__ + ".modifyStreamRedirect(): BEFORE propertyAttributeList=" + str( propertyAttributeList ) + "\n" )
			self.debug( __name__ + ".modifyStreamRedirect(): BEFORE propertyAttributeList type=" + str( type( propertyAttributeList ) ) + "\n" )
			#######################################################
			#	Set the StreamRedirect AttributeList values.
			#######################################################
			self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'fileName', str( fileName ) )
			self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'rolloverType', str( rolloverType ) )
			self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'maxNumberOfBackupFiles', int( maxNumberOfBackupFiles ) )
			self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'rolloverSize', int( rolloverSize ) )
			self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'baseHour', int( baseHour ) )
			self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'rolloverPeriod', int( rolloverPeriod ) )
			self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'formatWrites', java.lang.Boolean( formatWrites ) )
			self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'messageFormatKind', str( messageFormatKind ) )
			self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'suppressWrites', java.lang.Boolean( suppressWrites ) )
			self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'suppressStackTrace', java.lang.Boolean( suppressStackTrace ) )

			self.debug( __name__ + ".modifyStreamRedirect(): AFTER propertyAttributeList=" + str( propertyAttributeList ) + "\n" )

			####################################################################
			#	Save the StreamRedirect attributes to the current session.
			####################################################################
			self.configService.setAttributes( self.configService.session, configObject, propertyAttributeList )
			rVal = True
			break
		#Endfor

		if rVal: self.refresh()
		return rVal
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	testFunc()
	#
	#	DESCRIPTION:
	#		Do not use.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def testFunc( self ):
		"""Do not use.
		   PARAMETERS:
		   RETURN:
		       True if successful, or False.
		"""

		rVal = True

		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:

			self.debug( __name__ + ".testFunc(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".testFunc(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the classloaders AttributeList
			########################################################
			#pArgs = array( ['outputStreamRedirect'], java.lang.String )
			pArgs = None
			myAttributeList			= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )
			self.debug( __name__ + ".testFunc(): myAttributeList=" + str( myAttributeList ) + "\n" )
			self.debug( __name__ + ".testFunc(): myAttributeList type=" + str( type( myAttributeList ) ) + "\n" )

			for propAttr in myAttributeList:
				propName = propAttr.getName()
				propValue= propAttr.getValue()
				self.debug( __name__ + ".testFunc(): propName=" + str( propName ) + "\n" )
				#self.debug( __name__ + ".testFunc(): propName type=" + str( type( propName ) ) + "\n" )
				self.debug( __name__ + ".testFunc(): propValue=" + str( propValue ) + "\n" )
				#self.debug( __name__ + ".testFunc(): propValue type=" + str( type( propValue ) ) + "\n" )
			#Endfor
		#Endfor

		#if rVal: self.refresh()
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
	myLogger	= MyLogger( LOGFILE="/tmp/StreamRedirectManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/StreamRedirectManager.log", STDOUT=True, DEBUG=False )
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
	templateListManager	= TemplateListManager( configService, type="StreamRedirect", logger=myLogger )
	myStreamRedirectManager	= StreamRedirectManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in myStreamRedirectManager.attributesList:
		myStreamRedirectManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myStreamRedirectManager.attributesList:
		myStreamRedirectManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myStreamRedirectManager.attributesList:
			myStreamRedirectManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	myStreamRedirectManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/StreamRedirectManager.tsv" )

	myStreamRedirectManager.testFunc()

	rc = myStreamRedirectManager.modifyStreamRedirect( 
							currentFileName='${SERVER_LOG_ROOT}/SystemOut.log',
							fileName='${SERVER_LOG_ROOT}/SystemOut.log',
							rolloverType='BOTH',
							maxNumberOfBackupFiles=5,
							rolloverSize=1,
							baseHour=24,
							rolloverPeriod=24,
							formatWrites=True,
							messageFormatKind='BASIC',
							suppressWrites=False,
							suppressStackTrace=False
							)
	if rc: myStreamRedirectManager.saveSession( False )

	configService.closeMe()
	myStreamRedirectManager.closeMe()
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
