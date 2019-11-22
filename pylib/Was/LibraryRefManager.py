#!/usr/bin/env jython
######################################################################################
##	LibraryRefManager.py
##
##	Python module replaces some of the functions in the 
##	/nfs/dist/dmp/amp/wdt/*.jacl 
##	file and makes JavaProcessDef Property resource management object oriented.
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

class LibraryRefManager( AttributeUtils ):
	"""
    LibraryRefManager class that contains LibraryRef environment management methods.
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
			   scope         - Something like: "Node=node_ServicesA_01:Server=as_servicesA_a01"
               logger        - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		self.adminClient			= adminClient
		self.configService			= configService
		self.templateListManager	= templateListManager
		self.logger					= logger
		AttributeUtils.__init__( self, configService, scope, type='ApplicationServer', logger=self.logger )
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
	#	deleteClassLoaders()
	#
	#	DESCRIPTION:
	#		Delete the ClassLoader's.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deleteClassLoaders( self ):
		"""Delete the ClassLoader's.
		   PARAMETERS:
		   RETURN:
		       True if successful or False.
		       Failure occurs if there are no configObjects meaning the scope was
		       not defined properly.
		"""
		rVal = False

		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:

			self.debug( __name__ + ".deleteClassLoaders(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".deleteClassLoaders(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the classloaders attribute list.
			########################################################
			pArgs			= array( ['classloaders'], java.lang.String )
			myAttributeList	= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )

			########################################################
			#	Get the classloaders ArrayList from myAttributeList.
			########################################################
			classLoadersAttributeList	= self.configService.configServiceHelper.getAttributeValue( myAttributeList, 'classloaders' )

			#######################################################
			#	The classLoadersAttributeList contains the 
			#	javax.management.ObjectName instances of the
			#	environment Property objects.
			#######################################################
			for envObject in classLoadersAttributeList:
				self.debug( __name__ + ".deleteClassLoaders(): envObject=" + str( envObject ) + "\n" )
				self.debug( __name__ + ".deleteClassLoaders(): envObject type=" + str( type( envObject ) ) + "\n" )

				self.configService.deleteConfigData( self.configService.session, envObject )
				self.logIt( __name__ + ".deleteClassLoaders(): Deleted " + str( envObject ) + "\n" )
				rVal = True
			#Endfor
		#Endfor

		self.debug( __name__ + ".deleteClassLoaders(): rVal=" + str( rVal ) + "\n" )
		return rVal

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	addLibraryRef()
	#
	#	DESCRIPTION:
	#		Add the LibraryRef to ClassLoader.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def addLibraryRef( 
						self, 
						classLoaderObject,
						libraryName, 
						sharedClassloader=True
						):
		"""Add the LibraryRef to the ClassLoader.
		   PARAMETERS:
		       classLoaderObject    -- The javax.management.Object typically obtained from the call to addClassloader() method.
		       libraryName          -- Name of the library.
			   sharedClassloader    -- Specifies whether the classloader for the library will be shared. For IBM internal use only.
		   RETURN:
		       True if successful or False.
		"""
		self.debug( __name__ + ".addLibraryRef(): classLoaderObject=" + str( classLoaderObject ) + "\n" )
		self.debug( __name__ + ".addLibraryRef(): classLoaderObject type=" + str( type( classLoaderObject ) ) + "\n" )
		self.debug( __name__ + ".addLibraryRef(): libraryName=" + str( libraryName ) + "\n" )
		self.debug( __name__ + ".addLibraryRef(): sharedClassloader=" + str( sharedClassloader ) + "\n" )

		rVal = False

		if classLoaderObject is None:
			self.logIt( __name__ + ".addLibraryRef(): classLoaderObject is None."  + "\n" )
			return False
		#Endif

		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:

			self.debug( __name__ + ".addLibraryRef(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".addLibraryRef(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Create the LibraryRef AttributeList.
			########################################################
			libraryRefAttributeList = AttributeList()
			self.configService.configServiceHelper.setAttributeValue( libraryRefAttributeList, 'libraryName', str( libraryName ) )
			self.configService.configServiceHelper.setAttributeValue( libraryRefAttributeList, 'sharedClassloader', java.lang.Boolean( sharedClassloader ) )
			#libraryArrayList = ArrayList()
			#libraryArrayList.add( libraryRefAttributeList )
			libraryRefObject = self.configService.createConfigData( self.configService.session, classLoaderObject, 'libraries', 'LibraryRef', libraryRefAttributeList )

			self.debug( __name__ + ".addLibraryRef(): libraryRefObject=" + str( libraryRefObject ) + "\n" )
			self.debug( __name__ + ".addLibraryRef(): libraryRefObject type=" + str( type( libraryRefObject ) ) + "\n" )

			rVal = True
		#Endfor

		return rVal

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createClassloader()
	#
	#	DESCRIPTION:
	#		Create the Classloader in the Application Server configuration object.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createClassloader( self, mode='PARENT_FIRST' ):
		"""Create the Classloader in the Application Server configuration object.
		   PARAMETERS:
		       mode -- Specifies whether classes are loaded via the parent classloader before this one.
		   RETURN:
		       The javax.management.ObjectName to the Classloader type configuration object.
		"""
		self.debug( __name__ + ".createClassloader(): mode=" + str( mode ) + "\n" )

		###########################################################
		#	Delete all existing Classloader's.
		###########################################################
		rc = self.deleteClassLoaders()
		if not rc:
			self.logIt( __name__ + ".createClassloader(): deleteClassLoaders() did not find any configuration objects for " + str( self.configObjects ) + "\n" )
			self.logIt( __name__ + ".createClassloader(): Adding a Classloader is not possible." + "\n" )
			return None
		#Endif

		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		classLoaderObject = None
		for configObject in self.configObjects:

			self.debug( __name__ + ".createClassloader(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".createClassloader(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Create the Classloader with the mode only.
			########################################################
			classLoaderAttributeList = AttributeList()
			self.configService.configServiceHelper.setAttributeValue( classLoaderAttributeList, 'mode', str( mode ) )

			classLoaderObject = self.configService.createConfigData( self.configService.session, configObject, 'classloaders', 'Classloader', classLoaderAttributeList )
			self.debug( __name__ + ".createClassloader(): classLoaderObject=" + str( classLoaderObject ) + "\n" )
			self.debug( __name__ + ".createClassloader(): classLoaderObject type=" + str( type( classLoaderObject ) ) + "\n" )
		#Endfor

		return classLoaderObject

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
			pArgs = array( ['classloaders'], java.lang.String )
			myAttributeList			= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )
			self.debug( __name__ + ".testFunc(): myAttributeList=" + str( myAttributeList ) + "\n" )
			self.debug( __name__ + ".testFunc(): myAttributeList type=" + str( type( myAttributeList ) ) + "\n" )

			myArrayList	= self.configService.configServiceHelper.getAttributeValue( myAttributeList, 'classloaders' )
			self.debug( __name__ + ".testFunc(): myArrayList=" + str( myArrayList ) + "\n" )
			self.debug( __name__ + ".testFunc(): myArrayList type=" + str( type( myArrayList ) ) + "\n" )

			for envObject in myArrayList:
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

			#self.debug( __name__ + ".testFunc(): BEFORE myAttributeList=" + str( myAttributeList ) + "\n" )
			#self.debug( __name__ + ".testFunc(): BEFORE myAttributeList type=" + str( type( myAttributeList ) ) + "\n" )
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
	myLogger	= MyLogger( LOGFILE="/tmp/LibraryRefManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/LibraryRefManager.log", STDOUT=True, DEBUG=False )
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
	templateListManager	= TemplateListManager( configService, type="ApplicationServer", logger=myLogger )
	myLibraryRefManager	= LibraryRefManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in myLibraryRefManager.attributesList:
		myLibraryRefManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myLibraryRefManager.attributesList:
		myLibraryRefManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myLibraryRefManager.attributesList:
			myLibraryRefManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	myLibraryRefManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/LibraryRef.tsv" )

	myLibraryRefManager.testFunc()
	classLoaderObject = myLibraryRefManager.createClassloader( mode='PARENT_FIRST' )
	rc = myLibraryRefManager.addLibraryRef( 
						classLoaderObject,
						'denisLibrary', 
						sharedClassloader=True
						)
	if rc: rc = myLibraryRefManager.addLibraryRef( 
						classLoaderObject,
						'denisLibrary2', 
						sharedClassloader=True
						)
	myLibraryRefManager.testFunc()

	if rc: myLibraryRefManager.saveSession( False )

	configService.closeMe()
	myLibraryRefManager.closeMe()
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
