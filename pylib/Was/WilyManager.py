#!/usr/bin/env jython
######################################################################################
##	WilyManager.py
##
##	Python module for WilyManager attributes.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	01/28/2010	Denis M. Putnam		Created.
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

class WilyManager( AttributeUtils ):
	"""
    WilyManager class that contains WilyManager methods.
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
		AttributeUtils.__init__( self, configService, scope, type='CustomService', logger=self.logger )
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
	#	deleteCustomService()
	#
	#	DESCRIPTION:
	#		Delete the CustomService for the given display name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deleteCustomService( self, displayName='IntroscopeJMXPMIService' ):
		"""Delete the CustomService for the given display name.
		   PARAMETERS:
		       displayName -- The name of the service.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".deleteCustomService(): displayName=" + str( displayName ) + "\n" )

		rVal = False

		############################################################
		#	For all our configuration Objects within the scope,
		#	delete the configObject.
		############################################################
		for configObject in self.configObjects:
			self.debug( __name__ + ".deleteCustomService(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".deleteCustomService(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the CustomService AttributeList
			########################################################
			#pArgs = array( ['customServices'], java.lang.String )
			pArgs = None
			customServiceAttributeList	= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )

			self.debug( __name__ + ".deleteCustomService(): BEFORE customServiceAttributeList=" + str( customServiceAttributeList ) + "\n" )
			self.debug( __name__ + ".deleteCustomService(): BEFORE customServiceAttributeList type=" + str( type( customServiceAttributeList ) ) + "\n" )
			myDisplayName	= self.configService.configServiceHelper.getAttributeValue( customServiceAttributeList, 'displayName' )
			self.debug( __name__ + ".deleteCustomService(): myDisplayName=" + str( myDisplayName ) + "\n" )
			self.debug( __name__ + ".deleteCustomService(): myDisplayName type=" + str( type( myDisplayName ) ) + "\n" )

			if myDisplayName != displayName: continue
			self.configService.deleteConfigData( self.configService.session, configObject )

			rVal = True
			#break
		#Endfor

		if rVal: self.refresh()
		return rVal
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	isCustomServiceExists()
	#
	#	DESCRIPTION:
	#		Does the given CustomService exist.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def isCustomServiceExists( self, displayName ):
		"""Does the given CustomService exist.
		   PARAMETERS:
		       displayName -- display name of the CustomService.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".isCustomServiceExists(): displayName=" + str( displayName ) + "\n" )
		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:

			self.debug( __name__ + ".isCustomServiceExists(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".isCustomServiceExists(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the AttributeList
			########################################################
			#pArgs = array( ['customServices'], java.lang.String )
			#pArgs = array( ['services'], java.lang.String )
			pArgs = None
			myAttributeList	= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )
			self.debug( __name__ + ".isCustomServiceExists(): myAttributeList=" + str( myAttributeList ) + "\n" )
			self.debug( __name__ + ".isCustomServiceExists(): myAttributeList type=" + str( type( myAttributeList ) ) + "\n" )

			myDisplayName	= self.configService.configServiceHelper.getAttributeValue( myAttributeList, 'displayName' )
			self.debug( __name__ + ".isCustomServiceExists(): myDisplayName=" + str( myDisplayName ) + "\n" )
			self.debug( __name__ + ".isCustomServiceExists(): myDisplayName type=" + str( type( myDisplayName ) ) + "\n" )

			if myDisplayName == displayName: return True
			#Endif
		#Endfor

		self.logIt( __name__ + ".isCustomServiceExists(): " + str( displayName ) + " not found." + "\n" )
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createCustomService()
	#
	#	DESCRIPTION:
	#		Create the CustomService for the given display name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createCustomService( 
							self, 
							displayName='IntroscopeJMXPMIService',
							classname='com.wily.introscope.api.websphere.IntroscopeCustomService',
							classpath='/apps/wily/WebAppSupport.jar',
							enable=True,
							externalConfigURL='',
							description='Created by pylib.Was.WilyManager.'
							):
		"""Create the CustomService attributes for the given display name.
		   PARAMETERS:
		       displayName        -- The name of the service.
		       classname          -- The classname of the service implementation. The class must implement the 
                                     Services API of the product.
		       classpath          -- Classpath which is used to locate the classes/jars for this service. 
		       enable             -- Specifies whether the server will attempt to start the specified service. 
                                     Some kinds of services are always enabled and will disregard this property if set. 
		       externalConfigURL  -- The URL of a custom service configuration file. 
		       description        -- An optional description for the custom service.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".createCustomService(): displayName=" + str( displayName ) + "\n" )
		self.debug( __name__ + ".createCustomService(): classname=" + str( classname ) + "\n" )
		self.debug( __name__ + ".createCustomService(): classpath=" + str( classpath ) + "\n" )
		self.debug( __name__ + ".createCustomService(): externalConfigURL=" + str( externalConfigURL ) + "\n" )
		self.debug( __name__ + ".createCustomService(): description=" + str( description ) + "\n" )

		rVal = False

		if self.isCustomServiceExists( displayName ):
			self.logIt( __name__ + ".createCustomService(): name=" + str( displayName ) + " exists so it will deleted and then added." + "\n" )
			rVal = self.deleteCustomService( displayName=displayName )
			if rVal: self.refresh()
			if not rVal: return rVal
			description = 'Recreated by pylib.Was.WilyManager.'
		#Endif

		############################################################
		#	The rootObjectName is the configObject.  It should be
		#	of type 'Server'.
		############################################################
		configObject = self.rootObjectName

		########################################################
		#	Do the scalar attributes first.
		########################################################
		self.debug( __name__ + ".createCustomService(): configObject=" + str( configObject ) + "\n" )
		self.debug( __name__ + ".createCustomService(): configObject type=" + str( type( configObject ) ) + "\n" )

		########################################################
		#	Get the CustomService AttributeList
		########################################################
		pArgs = array( ['customServices'], java.lang.String )
		customServiceAttributeList	= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )

		self.debug( __name__ + ".createCustomService(): BEFORE customServiceAttributeList=" + "\n" )
		for item in str( customServiceAttributeList ).split( ',' ):
			self.debug( __name__ + ".createCustomService(): BEFORE item=" + str( item ) + "\n" )
		#Endfor
		self.debug( __name__ + ".createCustomService(): BEFORE customServiceAttributeList type=" + str( type( customServiceAttributeList ) ) + "\n" )

		#######################################################
		#	Set the myAttributeList values.
		#######################################################
		myAttributeList = AttributeList()
		self.configService.configServiceHelper.setAttributeValue( myAttributeList, 'enable', java.lang.Boolean( enable ) )
		self.configService.configServiceHelper.setAttributeValue( myAttributeList, 'displayName', str( displayName ) )
		self.configService.configServiceHelper.setAttributeValue( myAttributeList, 'classname', str( classname ) )
		self.configService.configServiceHelper.setAttributeValue( myAttributeList, 'classpath', str( classpath ) )
		self.configService.configServiceHelper.setAttributeValue( myAttributeList, 'externalConfigURL', str( externalConfigURL ) )
		self.configService.configServiceHelper.setAttributeValue( myAttributeList, 'description', str( description ) )
		self.debug( __name__ + ".createCustomService(): AFTER myAttributeList=" + "\n" )
		for item in str( customServiceAttributeList ).split( ',' ):
			self.debug( __name__ + ".createCustomService(): AFTER item=" + str( item ) + "\n" )
		#Endfor

		#######################################################
		#	Create the customServices.CustomService attribute.
		#######################################################
		customServiceObject	= self.configService.createConfigData( 
																self.configService.session, 
																configObject, 
																'customServices', 
																'CustomService', 
																myAttributeList 
																)


		self.debug( __name__ + ".createCustomService(): customServiceObject=" + str( customServiceObject ) + "\n" )
		self.debug( __name__ + ".createCustomService(): customServiceObject type=" + str( type( customServiceObject ) ) + "\n" )
		rVal = True

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
		self.debug( __name__ + ".testFunc(): Called" + "\n" )

		rVal = True

		############################################################
		#	Show as much as possible.
		############################################################
		for configObject in self.configObjects:

			self.debug( __name__ + ".testFunc(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".testFunc(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the AttributeList
			########################################################
			#pArgs = array( ['customServices'], java.lang.String )
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
	myLogger	= MyLogger( LOGFILE="/tmp/WilyManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/WilyManager.log", STDOUT=True, DEBUG=False )
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
	templateListManager	= TemplateListManager( configService, type="CustomService", logger=myLogger )
	myWilyManager	= WilyManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in myWilyManager.attributesList:
		myWilyManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myWilyManager.attributesList:
		myWilyManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myWilyManager.attributesList:
			myWilyManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	myWilyManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/WilyManager.tsv" )

	myWilyManager.testFunc()

	########################################################
	#	Make changes.
	########################################################
	rc = myWilyManager.createCustomService( 
							displayName='IntroscopeJMXPMIService',
							classname='com.wily.introscope.api.websphere.IntroscopeCustomService',
							classpath='/apps/wily/WebAppSupport.jar',
							enable=True,
							externalConfigURL='',
							description='Created by pylib.Was.WilyManager.'
							)
	myLogger.logIt( "main(): rc=" + str( rc ) + "\n" )
	myWilyManager.testFunc()
	if rc: rc = myWilyManager.createCustomService( 
							displayName='IntroscopeJMXPMIService',
							classname='com.wily.introscope.api.websphere.IntroscopeCustomService',
							classpath='/apps/wily/WebAppSupport.jar',
							enable=True,
							externalConfigURL='',
							description='Created by pylib.Was.WilyManager.'
							)
	myLogger.logIt( "main(): rc=" + str( rc ) + "\n" )
	myWilyManager.testFunc()
	if rc: myWilyManager.saveSession( False )

	configService.closeMe()
	myWilyManager.closeMe()
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
