#!/usr/bin/env jython
######################################################################################
##	JDBCProviderManager.py
##
##	Python module replaces some of the functions in the 
##	/nfs/dist/dmp/amp/wdt/_resources.jacl 
##	file and makes JDBCProvider resource management object oriented.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	12/30/2009	Denis M. Putnam		Created.
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
from pylib.Was.TemplateListManager import *
from pylib.Was.AttributeUtils import *
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

class JDBCProviderManager( AttributeUtils ):
	"""
    JDBCProviderManager class that contains VirtualHost management methods.
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
		self.logger					= logger
		AttributeUtils.__init__( self, self.configService, scope, type='JDBCProvider', logger=self.logger )
		self.templateListManager	= templateListManager
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
				#if re.search( '__doc__',  attr ): continue
				#if re.search( '__module__',  attr ): continue
				#if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
				#if re.search( 'instance', str( getattr( self, attr ) ) ): continue
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
	#	addJDBCProvider()
	#
	#	DESCRIPTION:
	#		Add a JDBC provider.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def addJDBCProvider(self,jdbcName,templateId,classpath,implementationClass,nativepath="",xa=False,description="This provider was created by the pylib.Was.JDBCProviderManager."):
		"""Add a JDBC provider.
		   PARAMETERS:
		       jdbcName             -- name of the JDBC provider.  Something like 'Derby JDBC Provider (XA)'
		       templateId           -- name of the JDBC provider template.  Something like 'JDBCProvider_3'
			   classpath            -- java classpath for the JDBC provider.  Something like '${DERBY_JDBC_DRIVER_PATH}/derby.jar:...'
			                           must be delimited by ':'.
			   implementationClass  -- implementation class name.  Something like 'org.apache.derby.jdbc.EmbeddedXADataSource'
			   nativepath           -- native path for the JDBCProvider.
			                           must be delimited by ':'.
			   xa                   -- defaults to False.  Set to True if this an XA provider.
			   description          -- description text.
		   RETURN:
		       True if successful or the jdbcName exists, or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".addJDBCProvider(): called.\n" )
		self.debug( __name__ + ".addJDBCProvider(): jdbcName=" + str( jdbcName ) + ".\n" )
		self.debug( __name__ + ".addJDBCProvider(): templateId=" + str( templateId ) + ".\n" )
		self.debug( __name__ + ".addJDBCProvider(): classpath=" + str( classpath ) + ".\n" )
		self.debug( __name__ + ".addJDBCProvider(): implementationClass=" + str( implementationClass ) + ".\n" )
		self.debug( __name__ + ".addJDBCProvider(): nativepath=" + str( nativepath ) + ".\n" )
		self.debug( __name__ + ".addJDBCProvider(): xa=" + str( xa ) + ".\n" )
		self.debug( __name__ + ".addJDBCProvider(): description=" + str( description ) + ".\n" )

		#######################################################
		#	Check to see if the given jdbcName already exists.
		#######################################################
		myvalues = self.getAttributeValues( 'name' )
		for value in myvalues:
			if value == jdbcName:
				self.logIt( __name__ + ".addJDBCProvider(): JDBC Provider " + str( jdbcName ) + " already exists, so it will not be added." + ".\n" )
				return True
			#Endif
		#Endfor
		self.logIt( __name__ + ".addJDBCProvider(): JDBC Provider " + str( jdbcName ) + " doesn't exist, so it will be added." + ".\n" )
	
		######################################################
		#	Set up the attributes.
		######################################################
		nameAttr	= Attribute( 'name', jdbcName )
		desAttr		= Attribute( 'description', description )

		myclassList = java.util.ArrayList()
		myclassAR	= classpath.split( ':' )
		for mypath in myclassAR:
			myclassList.add( mypath )
		#Endfor
		classAttr	= Attribute( 'classpath', myclassList )

		implAttr	= Attribute( 'implementationClassName', implementationClass )

		mynativeList = java.util.ArrayList()
		mynativeAR	= nativepath.split( ':' )
		for mypath in mynativeAR:
			mynativeList.add( mypath )
		#Endfor
		nativeAttr	= Attribute( 'nativepath', mynativeList )

		xaAttr		= Attribute( 'xa', java.lang.Boolean( xa ) )

		myAttrList	= AttributeList()
		myAttrList.add( nameAttr )
		myAttrList.add( desAttr )
		myAttrList.add( implAttr )
		myAttrList.add( classAttr )
		myAttrList.add( nativeAttr )
		myAttrList.add( xaAttr )
		
		#######################################################
		#	Create the JDBCProvider.
		#######################################################
		rc = self.createConfigDataWithTemplate( templateId, 'JDBCProvider', myAttrList )
		
		return rc
		
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createJDBCProvider()
	#
	#	DESCRIPTION:
	#		Create a JDBC provider.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createJDBCProvider(self,jdbcName,templateId,classpath,implementationClass,nativepath="",xa=False,description="This provider was created by the pylib.Was.JDBCProviderManager."):
		"""Create a JDBC provider.
		   PARAMETERS:
		       jdbcName             -- name of the JDBC provider.  Something like 'Derby JDBC Provider (XA)'
		       templateId           -- name of the JDBC provider template.  Something like 'JDBCProvider_3'
			   classpath            -- java classpath for the JDBC provider.  Something like '${DERBY_JDBC_DRIVER_PATH}/derby.jar:...'
			                           must be delimited by ':'.
			   implementationClass  -- implementation class name.  Something like 'org.apache.derby.jdbc.EmbeddedXADataSource'
			   nativepath           -- native path for the JDBCProvider.
			                           must be delimited by ':'.
			   xa                   -- defaults to False.  Set to True if this an XA provider.
			   description          -- description text.
		   RETURN:
		       True if successful or the jdbcName exists, or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createJDBCProvider(): called.\n" )
		self.debug( __name__ + ".createJDBCProvider(): jdbcName=" + str( jdbcName ) + ".\n" )
		self.debug( __name__ + ".createJDBCProvider(): templateId=" + str( templateId ) + ".\n" )
		self.debug( __name__ + ".createJDBCProvider(): classpath=" + str( classpath ) + ".\n" )
		self.debug( __name__ + ".createJDBCProvider(): implementationClass=" + str( implementationClass ) + ".\n" )
		self.debug( __name__ + ".createJDBCProvider(): nativepath=" + str( nativepath ) + ".\n" )
		self.debug( __name__ + ".createJDBCProvider(): xa=" + str( xa ) + ".\n" )
		self.debug( __name__ + ".createJDBCProvider(): description=" + str( description ) + ".\n" )

		#######################################################
		#	Check to see if the given jdbcName already exists.
		#######################################################
		myvalues = self.getAttributeValues( 'name' )
		for value in myvalues:
			if value == jdbcName:
				self.logIt( __name__ + ".createJDBCProvider(): JDBC Provider " + str( jdbcName ) + " already exists, so it will be deleted and then added." + ".\n" )
				configObject = self.getConfigObjectByDisplayName( jdbcName )
				rc = self.deleteConfigData( configObject )
			#Endif
		#Endfor
		self.logIt( __name__ + ".createJDBCProvider(): JDBC Provider adding " + str( jdbcName ) + ".\n" )

		rc = self.addJDBCProvider( jdbcName, templateId, classpath, implementationClass, nativepath=nativepath, xa=xa, description=description )
		return rc
		
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
	myLogger	= MyLogger( LOGFILE="/tmp/JDBCProviderManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/JDBCProviderManager.log", STDOUT=True, DEBUG=False )
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
	serverName	= "as_was7test_01"
	#clusterName	= "cl_was7test_a"
	clusterName	= "cl_ServicesA_a"

	#myscope 				= "Cell=" + str( cellName ) + ":Cluster=" + str( clusterName )
	myscope					= "ServerCluster=" + str( clusterName )
	#myscope 				= "Cell=" + str( cellName )
	#myscope					= "ServerCluster=" + str( clusterName ) + ":JDBCProvider=" + "Derby JDBC Provider (XA)"
	configService			= ConfigService( adminClient=myclient, logger=myLogger )
	templateListManager		= TemplateListManager( configService, type="JDBCProvider", logger=myLogger )
	#myJDBCProviderManager	= JDBCProviderManager( adminObject, configService, templateListManager, scope="Cell=ServicesA", logger=myLogger)
	myJDBCProviderManager	= JDBCProviderManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	if not myJDBCProviderManager.error:

		for mylist in myJDBCProviderManager.attributesList:
			myJDBCProviderManager.deepLogOfAttributes( mylist )
		#Endfor
		for mylist in myJDBCProviderManager.attributesList:
			myJDBCProviderManager.deepPrintOfAttributes( mylist )
		#Endfor
		try:
			fileName = "/tmp/denis.txt"
			FH = open( fileName, "w" )
			for mylist in myJDBCProviderManager.attributesList:
				myJDBCProviderManager.deepWriteOfAttributes( mylist, FH )
			#Endfor
			FH.close()
		except Exception, e:
				myLogger.logIt( "main(): " + str( e ) + "\n" )
				raise
		#Endtry

		myJDBCProviderManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/JDBCProviders.tsv" )

		myTemplateObject = templateListManager.getTemplateObject( 'JDBCProvider_3' )
		myLogger.logIt( "main(): myTemplateObject=" + str(myTemplateObject) + "\n" )

		#myJDBCProviderManager.saveSession( False )
	else:
		myLogger.logIt( "main(): No JDBCProviders found for scope=" + str(myscope) + "\n" )
	#Endif

	templateListManager.logTemplatesList()
	#myConfigObject = myJDBCProviderManager.getConfigObjectByName( 'Derby JDBC Provider (XA)' )
	#myLogger.logIt( "main(): myConfigObject=" + str( myConfigObject ) + "\n" )
	#myJDBCProviderManager.deleteConfigData( myConfigObject )
	rc = myJDBCProviderManager.createJDBCProvider( 'Derby JDBC Provider (XA)', 'JDBCProvider_derbyNS_1', '${DERBY_JDBC_DRIVER_PATH}/derby.jar', 'org.apache.derby.jdbc.EmbeddedXADataSource', nativepath='', xa=True, description="Built-in Derby JDBC Provider (XA)" )

	if rc:
		rc = myJDBCProviderManager.createJDBCProvider( 'Denis JDBC Provider', 'JDBCProvider_derbyNS_1', '${DERBY_JDBC_DRIVER_PATH}/derby.jar', 'org.apache.derby.jdbc.EmbeddedXADataSource', nativepath='', xa=True, description="This is Denis' super duper JDBC provider." )
	#Endif

	if rc: myJDBCProviderManager.saveSession()

	configService.closeMe()
	myJDBCProviderManager.closeMe()
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
