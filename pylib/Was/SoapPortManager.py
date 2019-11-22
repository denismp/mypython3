#!/usr/bin/env jython
######################################################################################
##	SoapPortManager.py
##
##	Python module for SoapPortManager attributes.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	02/02/2010	Denis M. Putnam		Created.
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

class SoapPortManager( AttributeUtils ):
	"""
    SoapPortManager class that contains SOAP_CONNECTOR_ADDRESS methods for the NameServer.
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
		AttributeUtils.__init__( self, configService, scope, type='SOAPConnector', logger=self.logger )
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
	#	modifySoapConnectorAddress()
	#
	#	DESCRIPTION:
	#		Modify the SOAP_CONNECTOR_ADDRESS attributes.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifySoapConnectorAddress( 
							self, 
							hostName='dilabvirt31-v5',
							port='8886'
							):
		"""Modify the SOAP_CONNECTOR_ADDRESS attributes.
		   PARAMETERS:
		       hostName -- The host name for the SOAP_CONNECTOR_ADDRESS.
		       port     -- The port for the SOAP_CONNECTOR_ADDRESS.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifySoapConnectorAddress(): hostName=" + str( hostName ) + "\n" )
		self.debug( __name__ + ".modifySoapConnectorAddress(): port=" + str( port ) + "\n" )

		rVal = False

		############################################################
		#	For all our configuration Objects within the scope,
		#	find the matching fileName and modify the attributes.
		############################################################
		for configObject in self.configObjects:
			self.debug( __name__ + ".modifySoapConnectorAddress(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".modifySoapConnectorAddress(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the AttributeList
			########################################################
			pArgs 						= array( ['SOAP_CONNECTOR_ADDRESS'], java.lang.String )
			propertyAttributeList		= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )
			soapConnectorObjectName		= self.configService.configServiceHelper.getAttributeValue( propertyAttributeList, 'SOAP_CONNECTOR_ADDRESS' )
			soapConnectorAttributeList	= self.configService.getAttributes( self.configService.session, soapConnectorObjectName, None, False )

			self.debug( __name__ + ".modifySoapConnectorAddress(): BEFORE soapConnectorAttributeList=" + str( soapConnectorAttributeList ) + "\n" )
			self.debug( __name__ + ".modifySoapConnectorAddress(): BEFORE soapConnectorAttributeList type=" + str( type( soapConnectorAttributeList ) ) + "\n" )
			#######################################################
			#	Set the AttributeList values.
			#######################################################
			self.configService.configServiceHelper.setAttributeValue( soapConnectorAttributeList, 'host', str( hostName ) )
			self.configService.configServiceHelper.setAttributeValue( soapConnectorAttributeList, 'port', int( port ) )

			self.debug( __name__ + ".modifySoapConnectorAddress(): AFTER soapConnectorAttributeList=" + str( soapConnectorAttributeList ) + "\n" )

			####################################################################
			#	Save the attributes to the current session.
			####################################################################
			self.configService.setAttributes( self.configService.session, soapConnectorObjectName, soapConnectorAttributeList )
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
		#	Display as much as possible.
		############################################################
		for configObject in self.configObjects:

			self.debug( __name__ + ".testFunc(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".testFunc(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the classloaders AttributeList
			########################################################
			pArgs = array( ['SOAP_CONNECTOR_ADDRESS'], java.lang.String )
			#pArgs = None
			myAttributeList			= self.configService.getAttributes( self.configService.session, configObject, pArgs, True )
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
	myLogger	= MyLogger( LOGFILE="/tmp/SoapPortManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/SoapPortManager.log", STDOUT=True, DEBUG=False )
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
	templateListManager	= TemplateListManager( configService, type="SOAPConnector", logger=myLogger )
	mySoapPortManager	= SoapPortManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in mySoapPortManager.attributesList:
		mySoapPortManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in mySoapPortManager.attributesList:
		mySoapPortManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in mySoapPortManager.attributesList:
			mySoapPortManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	mySoapPortManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/SoapPortManager.tsv" )

	mySoapPortManager.testFunc()

	rc = mySoapPortManager.modifySoapConnectorAddress( 
							hostName='dilabvirt31-v5',
							port='8887'
							)

	mySoapPortManager.testFunc()
	rc = mySoapPortManager.modifySoapConnectorAddress( 
							hostName='dilabvirt31-v5',
							port='8886'
							)

	mySoapPortManager.testFunc()
	if rc: mySoapPortManager.saveSession( False )

	configService.closeMe()
	mySoapPortManager.closeMe()
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
