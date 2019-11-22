#!/usr/bin/env jython
######################################################################################
##	JavaProcessDefEnvManager.py
##
##	Python module replaces some of the functions in the 
##	/nfs/dist/dmp/amp/wdt/*.jacl 
##	file and makes JavaProcessDef Property resource management object oriented.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	01/18/2010	Denis M. Putnam		Created.
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

class JavaProcessDefEnvManager( AttributeUtils ):
	"""
    JavaProcessDefEnvManager class that contains JavaProcessDef environment management methods.
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

		self.adminClient		= adminClient
		self.configService		= configService
		self.templateListManager	= templateListManager
		self.logger				= logger
		AttributeUtils.__init__( self, configService, scope, type='JavaProcessDef', logger=self.logger )
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
	#	isExistsJavaProcessDefEnvProperty()
	#
	#	DESCRIPTION:
	#		Does the JavaProcessDef environment Property exists?
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def isExistsJavaProcessDefEnvProperty( self, pname ):
		"""Does the JavaProcessDef environment Property exists?
		   PARAMETERS:
		       pname -- name of the JavaProcessDef environment Property name.
		   RETURN:
		       True if found, or False.
		"""
		self.debug( __name__ + ".isExistsJavaProcessDefEnvProperty(): pname=" + str( pname ) + "\n" )

		rVal = False

		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:

			self.debug( __name__ + ".isExistsJavaProcessDefEnvProperty(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".isExistsJavaProcessDefEnvProperty(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the JavaProcessDef enironment attribute list.
			########################################################
			pArgs			= array( ['environment'], java.lang.String )
			myAttributeList	= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )

			########################################################
			#	The environement ArrayList from myAttributeList.
			########################################################
			environmentArrayList	= self.configService.configServiceHelper.getAttributeValue( myAttributeList, 'environment' )

			#######################################################
			#	The environmentArrayList contains the 
			#	javax.management.ObjectName instances of the
			#	environment Property objects.
			#######################################################
			for envObject in environmentArrayList:
				self.debug( __name__ + ".isExistsJavaProcessDefEnvProperty(): envObject=" + str( envObject ) + "\n" )
				self.debug( __name__ + ".isExistsJavaProcessDefEnvProperty(): envObject type=" + str( type( envObject ) ) + "\n" )

				#######################################################
				#	Get the Property attributes from the envObject.
				#######################################################
				propertyAttributeList	= self.configService.getAttributes( self.configService.session, envObject, None, False )

				######################################################
				#	For each property attribute, check to see if
				#	we find a name that matches the name=value
				#	attribute.
				######################################################
				for propAttr in propertyAttributeList:
					propName = propAttr.getName()
					propValue= propAttr.getValue()
					if propName == 'name' and propValue == pname:
						self.debug( __name__ + ".isExistsJavaProcessDefEnvProperty(): Found " + str( propValue ) + "\n" )
						return True
					#Endfor
				#Endfor
			#Endfor
		#Endfor

		return rVal

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	deleteJavaProcessDefEnvProperty()
	#
	#	DESCRIPTION:
	#		Delete the JavaProcessDef environment Property by name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deleteJavaProcessDefEnvProperty( self, pname ):
		"""Delete the JavaProcessDef environment Property by name.
		   Warning: This method will delete all the properties that match the given
		   name.
		   PARAMETERS:
		       pname -- name of the JavaProcessDef environment Property name.
		   RETURN:
		       True if deleted or False.
		"""
		self.debug( __name__ + ".deleteJavaProcessDefEnvProperty(): pname=" + str( pname ) + "\n" )

		rVal = False

		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:

			self.debug( __name__ + ".deleteJavaProcessDefEnvProperty(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".deleteJavaProcessDefEnvProperty(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the JavaProcessDef enironment attribute list.
			########################################################
			pArgs			= array( ['environment'], java.lang.String )
			myAttributeList	= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )

			########################################################
			#	The environement ArrayList from myAttributeList.
			########################################################
			environmentArrayList	= self.configService.configServiceHelper.getAttributeValue( myAttributeList, 'environment' )

			#######################################################
			#	The environmentArrayList contains the 
			#	javax.management.ObjectName instances of the
			#	environment Property objects.
			#######################################################
			for envObject in environmentArrayList:
				self.debug( __name__ + ".deleteJavaProcessDefEnvProperty(): envObject=" + str( envObject ) + "\n" )
				self.debug( __name__ + ".deleteJavaProcessDefEnvProperty(): envObject type=" + str( type( envObject ) ) + "\n" )

				#######################################################
				#	Get the Property attributes from the envObject.
				#######################################################
				propertyAttributeList	= self.configService.getAttributes( self.configService.session, envObject, None, False )

				######################################################
				#	For each property attribute, check to see if
				#	we find a name that matches the name=value
				#	attribute.  If so, delete the config object.
				######################################################
				for propAttr in propertyAttributeList:
					propName = propAttr.getName()
					propValue= propAttr.getValue()
					if propName == 'name' and propValue == pname:
						self.debug( __name__ + ".deleteJavaProcessDefEnvProperty(): Found " + str( propValue ) + "\n" )
						self.configService.deleteConfigData( self.configService.session, envObject )
						self.logIt( __name__ + ".deleteJavaProcessDefEnvProperty(): Deleted " + str( propValue ) + ":" + str( envObject ) + "\n" )
						rVal = True
					#Endfor
				#Endfor
			#Endfor
		#Endfor

		self.debug( __name__ + ".deleteJavaProcessDefEnvProperty(): rVal=" + str( rVal ) + "\n" )
		return rVal

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	addJavaProcessDefEnvProperty()
	#
	#	DESCRIPTION:
	#		Add the JavaProcessDef environment Property by name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def addJavaProcessDefEnvProperty( 
										self, 
										pname, 
										value, 
										description="created by pylib.Was.JavaProcessDefEnv",
										required=False,
										validationExpression='' 
										):
		"""Add the JavaProcessDef environment Property by name.
		   PARAMETERS:
		       pname                -- The name of the property.
		       value                -- The value for the property. 
			   description          -- An optional description for this property value.
			   required             -- An optional attribute which specifies whether this property is required to have a value. 
			   validationExpression -- The console or other tools may use this value to validate the contents of the value of this property.
		   RETURN:
		       True if successful or False.
		"""
		self.debug( __name__ + ".addJavaProcessDefEnvProperty(): pname=" + str( pname ) + "\n" )
		self.debug( __name__ + ".addJavaProcessDefEnvProperty(): value=" + str( value ) + "\n" )
		self.debug( __name__ + ".addJavaProcessDefEnvProperty(): description=" + str( description ) + "\n" )
		self.debug( __name__ + ".addJavaProcessDefEnvProperty(): required=" + str( required ) + "\n" )
		self.debug( __name__ + ".addJavaProcessDefEnvProperty(): validationExpression=" + str( validationExpression ) + "\n" )

		rVal = False

		if self.isExistsJavaProcessDefEnvProperty( pname ):
			self.debug( __name__ + ".addJavaProcessDefEnvProperty(): pname=" + str( pname ) + " exists.  Property was not created." + "\n" )
			return False
		else:
			############################################################
			#	For all our configuration Objects within the scope,
			#	modify the attributes.  Hopefully there is only one
			#	configuration Object.  This depends on how the request
			#	was scoped.
			############################################################
			for configObject in self.configObjects:

				self.debug( __name__ + ".addJavaProcessDefEnvProperty(): configObject=" + str( configObject ) + "\n" )
				self.debug( __name__ + ".addJavaProcessDefEnvProperty(): configObject type=" + str( type( configObject ) ) + "\n" )

				########################################################
				#	Get the JavaProcessDef environment attribute list.
				########################################################
				pArgs						= array( ['environment'], java.lang.String )
				environmentAttributeList	= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )
				environmentArrayList		= self.configService.configServiceHelper.getAttributeValue( environmentAttributeList, 'environment' )
				self.debug( __name__ + ".addJavaProcessDefEnvProperty(): environmentArrayList=" + str( environmentArrayList ) + "\n" )
				self.debug( __name__ + ".addJavaProcessDefEnvProperty(): environmentArrayList type=" + str( type( environmentArrayList ) ) + "\n" )

				######################################################################
				#	Show what is in the environmentArrayList.  This
				#	should be an java.lang.ArrayList of javax.management.ObjectName's
				#	of the type 'Property', if any.
				######################################################################
				for item in environmentArrayList:
					self.debug( __name__ + ".addJavaProcessDefEnvProperty(): item=" + str( item ) + "\n" )
					self.debug( __name__ + ".addJavaProcessDefEnvProperty(): item type=" + str( type( item ) ) + "\n" )
				#Endfor

				#################################################
				#	Create the property AttributeList.
				#################################################
				propertyAttributeList	= AttributeList()
				self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'name', str( pname ) )
				self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'value', value )
				self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'description', str( description ) )
				self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'required', java.lang.Boolean( required) )
				self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'validationExpression', str( validationExpression ) )
				self.debug( __name__ + ".addJavaProcessDefEnvProperty(): propertyAttributeList=" + str( propertyAttributeList ) + "\n" )

				##################################################
				#	Create a ConfigId Object of 'Property' type.
				##################################################
				myConfigId		= self.configService.configServiceHelper.convertObjectNameToConfigDataId( configObject )
				propertyObject	= self.configService.configServiceHelper.createObjectName( myConfigId, 'Property' )
				self.debug( __name__ + ".addJavaProcessDefEnvProperty(): propertyObject=" + str( propertyObject ) + "\n" )

				#################################################
				#	Now create an environment attribute of type
				#	Property.
				#################################################
				propertyObject	= self.configService.createConfigData( self.configService.session, configObject, 'environment', 'Property', propertyAttributeList )

				################################################
				#	Now retrieve the new property attributes
				#	from current session.
				################################################
				propertyAttributeList = self.configService.getAttributes( self.configService.session, propertyObject, None, False )

				self.debug( __name__ + ".addJavaProcessDefEnvProperty(): propertyAttributeList=" + str( propertyAttributeList ) + "\n" )
				self.debug( __name__ + ".addJavaProcessDefEnvProperty(): propertyAttributeList type=" + str( type( propertyAttributeList ) ) + "\n" )
				####################################################
				##	Create the a new JavaProcessDef config object.
				####################################################
				##javaProcessDefObject = self.configService.createConfigData( self.configService.session, configObject, 'environment', 'JavaProcessDef', propertyAttributeList )

				##self.debug( __name__ + ".addJavaProcessDefEnvProperty(): javaProcessDefObject=" + str( javaProcessDefObject ) + "\n" )
				##self.debug( __name__ + ".addJavaProcessDefEnvProperty(): javaProcessDefObject type=" + str( type( javaProcessDefObject ) ) + "\n" )

				rVal = True
			#Endfor
		#Endif

		return rVal

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createJavaProcessDefEnvProperty()
	#
	#	DESCRIPTION:
	#		Create the JavaProcessDef environment Property by name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createJavaProcessDefEnvProperty( 
										self, 
										pname, 
										value, 
										description="created by pylib.Was.JavaProcessDefEnv",
										required=False,
										validationExpression='' 
										):
		"""Create the JavaProcessDef environment Property by name.
		   Warning: This method will delete all the properties that match the given
		   name.
		   PARAMETERS:
		       pname                -- The name of the property.
		       value                -- The value for the property. 
			   description          -- An optional description for this property value.
			   required             -- An optional attribute which specifies whether this property is required to have a value. 
			   validationExpression -- The console or other tools may use this value to validate the contents of the value of this property.
		   RETURN:
		       True if successful or False.
		"""
		self.debug( __name__ + ".createJavaProcessDefEnvProperty(): pname=" + str( pname ) + "\n" )
		self.debug( __name__ + ".createJavaProcessDefEnvProperty(): value=" + str( value ) + "\n" )
		self.debug( __name__ + ".createJavaProcessDefEnvProperty(): description=" + str( description ) + "\n" )
		self.debug( __name__ + ".createJavaProcessDefEnvProperty(): required=" + str( required ) + "\n" )
		self.debug( __name__ + ".createJavaProcessDefEnvProperty(): validationExpression=" + str( validationExpression ) + "\n" )

		rVal = True

		if self.isExistsJavaProcessDefEnvProperty( pname ):
			self.debug( __name__ + ".createJavaProcessDefEnvProperty(): pname=" + str( pname ) + " exists.  It will be deleted and then added." + "\n" )
			rVal = self.deleteJavaProcessDefEnvProperty( pname )
		#Endif

		if rVal: rVal = self.addJavaProcessDefEnvProperty( pname, value, description, required, validationExpression )

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

			########################################################
			#	Do the scalar attributes first.
			########################################################
			self.debug( __name__ + ".testFunc(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".testFunc(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the environment AttributeList
			########################################################
			pArgs = array( ['environment'], java.lang.String )
			myAttributeList			= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )
			self.debug( __name__ + ".testFunc(): myAttributeList=" + str( myAttributeList ) + "\n" )
			self.debug( __name__ + ".testFunc(): myAttributeList type=" + str( type( myAttributeList ) ) + "\n" )

			environmentArrayList	= self.configService.configServiceHelper.getAttributeValue( myAttributeList, 'environment' )
			self.debug( __name__ + ".testFunc(): environmentArrayList=" + str( environmentArrayList ) + "\n" )
			self.debug( __name__ + ".testFunc(): environmentArrayList type=" + str( type( environmentArrayList ) ) + "\n" )

			for envObject in environmentArrayList:
				self.debug( __name__ + ".testFunc(): envObject=" + str( envObject ) + "\n" )
				self.debug( __name__ + ".testFunc(): envObject type=" + str( type( envObject ) ) + "\n" )
				propertyAttributeList	= self.configService.getAttributes( self.configService.session, envObject, None, False )
				for propAttr in propertyAttributeList:
					propName = propAttr.getName()
					propValue= propAttr.getValue()
					self.debug( __name__ + ".testFunc(): propName=" + str( propName ) + "\n" )
					#self.debug( __name__ + ".testFunc(): propName type=" + str( type( propName ) ) + "\n" )
					self.debug( __name__ + ".testFunc(): propValue=" + str( propValue ) + "\n" )
					#self.debug( __name__ + ".testFunc(): propValue type=" + str( type( propValue ) ) + "\n" )
				#Endfor
			#Endfor

			self.debug( __name__ + ".testFunc(): BEFORE myAttributeList=" + str( myAttributeList ) + "\n" )
			self.debug( __name__ + ".testFunc(): BEFORE myAttributeList type=" + str( type( myAttributeList ) ) + "\n" )
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
	myLogger	= MyLogger( LOGFILE="/tmp/JavaProcessDefEnvManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/JavaProcessDefEnvManager.log", STDOUT=True, DEBUG=False )
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

	myscope				= "Node=" + nodeName + ":Server=" + serverName
	#myscope			= "Node=" + nodeName + ":ServerIndex:ServerEntry=" + serverName
	configService 		= ConfigService( adminClient=myclient, logger=myLogger )
	templateListManager	= TemplateListManager( configService, type="JavaProcessDef", logger=myLogger )
	myJavaProcessDefEnvManager	= JavaProcessDefEnvManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in myJavaProcessDefEnvManager.attributesList:
		myJavaProcessDefEnvManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myJavaProcessDefEnvManager.attributesList:
		myJavaProcessDefEnvManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myJavaProcessDefEnvManager.attributesList:
			myJavaProcessDefEnvManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	myJavaProcessDefEnvManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/JavaProcessDefEnv.tsv" )

	########################################################
	#	Create the JavaProcessDef enviroment Property
	########################################################
	propertyName	= "DENIS_PROPERTY"
	propertyValue	= 'denisvalue'
	#rc = myJavaProcessDefEnvManager.createJavaProcessDefEnv(
	#					properyName,
	#					propertyValue,
	#					required=False
	#					)
	#myJavaProcessDefEnvManager.isExistsJavaProcessDefEnvProperty( 'DENIS_PROPERTY' )
	#myJavaProcessDefEnvManager.testFunc()
	#myJavaProcessDefEnvManager.deleteJavaProcessDefEnvProperty( 'DENIS_PROPERTY' )
	#myJavaProcessDefEnvManager.addJavaProcessDefEnvProperty( 'DENIS_PROPERTY', 'value3', description="created by pylib.Was.JavaProcessDefEnv",required=False,validationExpression='' )
	rc = myJavaProcessDefEnvManager.createJavaProcessDefEnvProperty( 'DENIS_PROPERTY', 'value1', description="created by pylib.Was.JavaProcessDefEnv",required=False,validationExpression='' )

	if rc: rc = myJavaProcessDefEnvManager.createJavaProcessDefEnvProperty( 'DENIS_PROPERTY2', 'value2', description="created by pylib.Was.JavaProcessDefEnv",required=False,validationExpression='' )
	if rc: rc = myJavaProcessDefEnvManager.createJavaProcessDefEnvProperty( 'DENIS_PROPERTY2', 'value2', description="created by pylib.Was.JavaProcessDefEnv",required=False,validationExpression='' )
	if rc: myJavaProcessDefEnvManager.saveSession( False )

	configService.closeMe()
	myJavaProcessDefEnvManager.closeMe()
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
