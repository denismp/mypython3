#!/usr/bin/env jython
######################################################################################
##	ThreadPoolManager.py
##
##	Python module for ThreadPoolManager attributes.
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

class ThreadPoolManager( AttributeUtils ):
	"""
    ThreadPoolManager class that contains ThreadPoolManager methods.
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
		AttributeUtils.__init__( self, configService, scope, type='ThreadPoolManager', logger=self.logger )
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
	#	modifyThreadPool()
	#
	#	DESCRIPTION:
	#		Modify the threadPool attributes for the given threadPool name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifyThreadPool( 
							self, 
							name='WebContainer',
							minimumSize=50,
							maximumSize=50,
							inactivityTimeout=6000,
							isGrowable=True,
							description='Modified by pylib.Was.ThreadPoolManager.'
							):
		"""Modify the threadPool attributes for the given threadPool name.
		   PARAMETERS:
		       name               -- ThreadPool name.  Allows the thread pool to be given a name so that it can 
                                     be referenced in other places in the configuration. Not used for thread pool 
                                     instances contained directly under MessageListenerService, WebContainer, 
                                     ObjectRequestBroker. 
		       minimumSize        -- The minimum number of threads to allow in the pool.
		       maximumSize        -- The maximum number of threads to allow in the pool.
		       inactivityTimeout  -- The period of time in milliseconds after which a thread should be reclaimed due to inactivity.
		       isGrowable         -- Allows the number of threads to increase beyond the maximum size configured for the thread pool.
		       description        -- The description of the thread pool.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifyThreadPool(): name=" + str( name ) + "\n" )
		self.debug( __name__ + ".modifyThreadPool(): minimumSize=" + str( minimumSize ) + "\n" )
		self.debug( __name__ + ".modifyThreadPool(): maximumSize=" + str( maximumSize ) + "\n" )
		self.debug( __name__ + ".modifyThreadPool(): inactivityTimeout=" + str( inactivityTimeout ) + "\n" )
		self.debug( __name__ + ".modifyThreadPool(): isGrowable=" + str( isGrowable ) + "\n" )
		self.debug( __name__ + ".modifyThreadPool(): description=" + str( description ) + "\n" )

		rVal = False

		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:
			self.debug( __name__ + ".modifyThreadPool(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".modifyThreadPool(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the threadPools AttributeList
			########################################################
			pArgs = array( ['threadPools'], java.lang.String )
			threadPoolsAttributeList	= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )

			#######################################################
			#	Go through each object in the list.
			#	Each myObject should be an Attribute() who's value
			#	is an ArrayList of AttributeList's.
			#########################################################
			for myObject in threadPoolsAttributeList:
				self.debug( __name__ + ".modifyThreadPool(): myObject=" + str( myObject ) + "\n" )
				self.debug( __name__ + ".modifyThreadPool(): myObject type=" + str( type( myObject ) ) + "\n" )

				#########################################################
				#	Get the list of the threadPools objects.
				#########################################################
				threadPoolConfigObjects = myObject.getValue()
				self.debug( __name__ + ".modifyThreadPool(): threadPoolConfigObjects=" + str( threadPoolConfigObjects ) + "\n" )
				self.debug( __name__ + ".modifyThreadPool(): threadPoolConfigObjects type=" + str( type( threadPoolConfigObjects ) ) + "\n" )
				########################################################
				#	Go through the list of threadPools objects to
				#	find the match on the name and then modify it.
				########################################################
				if not isinstance( threadPoolConfigObjects, java.util.ArrayList ): break
				for threadPoolConfigObject in threadPoolConfigObjects:
					self.debug( __name__ + ".modifyThreadPool(): threadPoolConfigObject=" + str( threadPoolConfigObject ) + "\n" )
					self.debug( __name__ + ".modifyThreadPool(): threadPoolConfigObject type=" + str( type( threadPoolConfigObject ) ) + "\n" )
					propertyAttributeList	= self.configService.getAttributes( self.configService.session, threadPoolConfigObject, None, False )
					threadName				= self.configService.configServiceHelper.getAttributeValue( propertyAttributeList, 'name' )

					###########################################################
					#	If the name does not match, then continue to the top
					#	of the loop.
					###########################################################
					if threadName != name: continue

					self.debug( __name__ + ".modifyThreadPool(): BEFORE propertyAttributeList=" + str( propertyAttributeList ) + "\n" )
					self.debug( __name__ + ".modifyThreadPool(): BEFORE propertyAttributeList type=" + str( type( propertyAttributeList ) ) + "\n" )
					#######################################################
					#	Set the threadPools AttributeList values.
					#######################################################
					#self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'name', str( name ) )
					self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'minimumSize', int( minimumSize ) )
					self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'maximumSize', int( maximumSize ) )
					self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'inactivityTimeout', int( inactivityTimeout ) )
					self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'isGrowable', java.lang.Boolean( isGrowable ) )
					self.configService.configServiceHelper.setAttributeValue( propertyAttributeList, 'description', str( description ) )

					self.debug( __name__ + ".modifyThreadPool(): AFTER propertyAttributeList=" + str( propertyAttributeList ) + "\n" )

					####################################################################
					#	Save the threadPools attributes to the treadPoolConfigObject
					#	and the current session.
					####################################################################
					self.configService.setAttributes( self.configService.session, threadPoolConfigObject, propertyAttributeList )
					rVal = True
					break
				#Endfor
			#Endfor
		#Endfor

		if rVal: self.refresh()
		return rVal
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	deleteThreadPool()
	#
	#	DESCRIPTION:
	#		Delete the threadPool for the given threadPool name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deleteThreadPool( self, name='DCSChannel' ):
		"""Delete the threadPool for the given threadPool name.
		   PARAMETERS:
		       name               -- ThreadPool name.  Allows the thread pool to be given a name so that it can 
                                     be referenced in other places in the configuration. Not used for thread pool 
                                     instances contained directly under MessageListenerService, WebContainer, 
                                     ObjectRequestBroker. 
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".deleteThreadPool(): name=" + str( name ) + "\n" )

		rVal = False

		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:
			self.debug( __name__ + ".deleteThreadPool(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".deleteThreadPool(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the threadPools AttributeList
			########################################################
			pArgs = array( ['threadPools'], java.lang.String )
			threadPoolsAttributeList	= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )

			#######################################################
			#	Go through each object in the list.
			#	Each myObject should be an Attribute() who's value
			#	is an ArrayList of AttributeList's.
			#########################################################
			for myObject in threadPoolsAttributeList:
				self.debug( __name__ + ".deleteThreadPool(): myObject=" + str( myObject ) + "\n" )
				self.debug( __name__ + ".deleteThreadPool(): myObject type=" + str( type( myObject ) ) + "\n" )

				#########################################################
				#	Get the list of the threadPools objects.
				#########################################################
				threadPoolConfigObjects = myObject.getValue()
				self.debug( __name__ + ".deleteThreadPool(): threadPoolConfigObjects=" + str( threadPoolConfigObjects ) + "\n" )
				self.debug( __name__ + ".deleteThreadPool(): threadPoolConfigObjects type=" + str( type( threadPoolConfigObjects ) ) + "\n" )
				########################################################
				#	Go through the list of threadPools objects to
				#	find the match on the name and then modify it.
				########################################################
				if not isinstance( threadPoolConfigObjects, java.util.ArrayList ): break
				for threadPoolConfigObject in threadPoolConfigObjects:
					self.debug( __name__ + ".deleteThreadPool(): threadPoolConfigObject=" + str( threadPoolConfigObject ) + "\n" )
					self.debug( __name__ + ".deleteThreadPool(): threadPoolConfigObject type=" + str( type( threadPoolConfigObject ) ) + "\n" )
					propertyAttributeList	= self.configService.getAttributes( self.configService.session, threadPoolConfigObject, None, False )
					threadName				= self.configService.configServiceHelper.getAttributeValue( propertyAttributeList, 'name' )

					###########################################################
					#	If the name does not match, then continue to the top
					#	of the loop.
					###########################################################
					if threadName != name: continue

					self.configService.deleteConfigData( self.configService.session, threadPoolConfigObject )
					self.logIt( __name__ + ".deleteThreadPool(): Deleted =" + str( name ) + "\n" )
					self.logIt( __name__ + ".deleteThreadPool(): threadPoolConfigObject=" + str( threadPoolConfigObject ) + "\n" )
					rVal = True
					break
				#Endfor
			#Endfor
		#Endfor

		if rVal: self.refresh()
		return rVal
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createThreadPool()
	#
	#	DESCRIPTION:
	#		Create the threadPool attributes for the given threadPool name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createThreadPool( 
							self, 
							name='DCSChannel',
							minimumSize=7,
							maximumSize=40,
							inactivityTimeout=5000,
							isGrowable=False,
							description='Created by pylib.Was.ThreadPoolManager.'
							):
		"""Create the threadPool attributes for the given threadPool name.
		   PARAMETERS:
		       name               -- ThreadPool name.  Allows the thread pool to be given a name so that it can 
                                     be referenced in other places in the configuration. Not used for thread pool 
                                     instances contained directly under MessageListenerService, WebContainer, 
                                     ObjectRequestBroker. 
		       minimumSize        -- The minimum number of threads to allow in the pool.
		       maximumSize        -- The maximum number of threads to allow in the pool.
		       inactivityTimeout  -- The period of time in milliseconds after which a thread should be reclaimed due to inactivity.
		       isGrowable         -- Allows the number of threads to increase beyond the maximum size configured for the thread pool.
		       description        -- The description of the thread pool.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".createThreadPool(): name=" + str( name ) + "\n" )
		self.debug( __name__ + ".createThreadPool(): minimumSize=" + str( minimumSize ) + "\n" )
		self.debug( __name__ + ".createThreadPool(): maximumSize=" + str( maximumSize ) + "\n" )
		self.debug( __name__ + ".createThreadPool(): inactivityTimeout=" + str( inactivityTimeout ) + "\n" )
		self.debug( __name__ + ".createThreadPool(): isGrowable=" + str( isGrowable ) + "\n" )
		self.debug( __name__ + ".createThreadPool(): description=" + str( description ) + "\n" )

		rVal = False

		if self.isThreadPoolExists( name ):
			self.logIt( __name__ + ".createThreadPool(): name=" + str( name ) + " exists so it will modified." + "\n" )
			rVal = self.modifyThreadPool( 
									name=name, 
									minimumSize=minimumSize, 
									maximumSize=maximumSize, 
									inactivityTimeout=inactivityTimeout, 
									isGrowable=isGrowable, 
									description='Modified by pylib.Was.ThreadPoolManager.' 
									)
			if rVal: self.refresh()
			return rVal
		#Endif

		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:
			self.debug( __name__ + ".createThreadPool(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".createThreadPool(): configObject type=" + str( type( configObject ) ) + "\n" )

			threadPoolsAttributeList = AttributeList()
			#######################################################
			#	Set the threadPools AttributeList values.
			#######################################################
			self.configService.configServiceHelper.setAttributeValue( threadPoolsAttributeList, 'name', str( name ) )
			self.configService.configServiceHelper.setAttributeValue( threadPoolsAttributeList, 'minimumSize', int( minimumSize ) )
			self.configService.configServiceHelper.setAttributeValue( threadPoolsAttributeList, 'maximumSize', int( maximumSize ) )
			self.configService.configServiceHelper.setAttributeValue( threadPoolsAttributeList, 'inactivityTimeout', int( inactivityTimeout ) )
			self.configService.configServiceHelper.setAttributeValue( threadPoolsAttributeList, 'isGrowable', java.lang.Boolean( isGrowable ) )
			self.configService.configServiceHelper.setAttributeValue( threadPoolsAttributeList, 'description', str( description ) )
			self.debug( __name__ + ".createThreadPool(): threadPoolsAttributeList=" + str( threadPoolsAttributeList ) + "\n" )
			self.debug( __name__ + ".createThreadPool(): threadPoolsAttributeList type=" + str( type( threadPoolsAttributeList ) ) + "\n" )

			######################################################
			#	Create the threadPools in the ThreadPool.
			######################################################
			threadPoolManagerObject	= self.configService.createConfigData( self.configService.session, configObject, 'threadPools', 'ThreadPoolManager', threadPoolsAttributeList )

			self.debug( __name__ + ".createThreadPool(): threadPoolManagerObject=" + str( threadPoolManagerObject ) + "\n" )
			self.debug( __name__ + ".createThreadPool(): threadPoolManagerObject type=" + str( type( threadPoolManagerObject ) ) + "\n" )
			rVal = True
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
			pArgs = array( ['threadPools'], java.lang.String )
			myAttributeList			= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )
			self.debug( __name__ + ".testFunc(): myAttributeList=" + str( myAttributeList ) + "\n" )
			self.debug( __name__ + ".testFunc(): myAttributeList type=" + str( type( myAttributeList ) ) + "\n" )

			myArrayList	= self.configService.configServiceHelper.getAttributeValue( myAttributeList, 'threadPools' )
			self.debug( __name__ + ".testFunc(): myArrayList=" + str( myArrayList ) + "\n" )
			self.debug( __name__ + ".testFunc(): myArrayList type=" + str( type( myArrayList ) ) + "\n" )

			for myObject in myArrayList:
				self.debug( __name__ + ".testFunc(): myObject=" + str( myObject ) + "\n" )
				self.debug( __name__ + ".testFunc(): myObject type=" + str( type( myObject ) ) + "\n" )
				propertyAttributeList	= self.configService.getAttributes( self.configService.session, myObject, None, False )
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

	##################################################################################
	#	isThreadPoolExists()
	#
	#	DESCRIPTION:
	#		Does the given threadPool exist.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def isThreadPoolExists( self, threadPoolName ):
		"""Does the given threadPool exist.
		   PARAMETERS:
		       threadPoolName -- name of the threadPool.
		   RETURN:
		       True if successful, or False.
		"""
		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:

			self.debug( __name__ + ".isThreadPoolExists(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".isThreadPoolExists(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the threadPools AttributeList
			########################################################
			pArgs = array( ['threadPools'], java.lang.String )
			myAttributeList			= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )
			self.debug( __name__ + ".isThreadPoolExists(): myAttributeList=" + str( myAttributeList ) + "\n" )
			self.debug( __name__ + ".isThreadPoolExists(): myAttributeList type=" + str( type( myAttributeList ) ) + "\n" )

			myArrayList	= self.configService.configServiceHelper.getAttributeValue( myAttributeList, 'threadPools' )
			self.debug( __name__ + ".isThreadPoolExists(): myArrayList=" + str( myArrayList ) + "\n" )
			self.debug( __name__ + ".isThreadPoolExists(): myArrayList type=" + str( type( myArrayList ) ) + "\n" )

			for myObject in myArrayList:
				self.debug( __name__ + ".isThreadPoolExists(): myObject=" + str( myObject ) + "\n" )
				self.debug( __name__ + ".isThreadPoolExists(): myObject type=" + str( type( myObject ) ) + "\n" )
				propertyAttributeList	= self.configService.getAttributes( self.configService.session, myObject, None, False )
				for propAttr in propertyAttributeList:
					propName = propAttr.getName()
					propValue= propAttr.getValue()
					self.debug( __name__ + ".isThreadPoolExists(): propName=" + str( propName ) + "\n" )
					#self.debug( __name__ + ".isThreadPoolExists(): propName type=" + str( type( propName ) ) + "\n" )
					self.debug( __name__ + ".isThreadPoolExists(): propValue=" + str( propValue ) + "\n" )
					#self.debug( __name__ + ".isThreadPoolExists(): propValue type=" + str( type( propValue ) ) + "\n" )
					if propName == 'name' and propValue == threadPoolName:
						self.logIt( __name__ + ".isThreadPoolExists(): Found " + str( propValue ) + "\n" )
						return True
					#Endif
				#Endfor
			#Endfor
		#Endfor

		self.logIt( __name__ + ".isThreadPoolExists(): " + str( threadPoolName ) + " not found." + "\n" )
		return False
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
	myLogger	= MyLogger( LOGFILE="/tmp/ThreadPoolManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/ThreadPoolManager.log", STDOUT=True, DEBUG=False )
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
	templateListManager	= TemplateListManager( configService, type="ThreadPoolManager", logger=myLogger )
	myThreadPoolManager	= ThreadPoolManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in myThreadPoolManager.attributesList:
		myThreadPoolManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myThreadPoolManager.attributesList:
		myThreadPoolManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myThreadPoolManager.attributesList:
			myThreadPoolManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	myThreadPoolManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/ThreadPoolManager.tsv" )

	myThreadPoolManager.testFunc()


	########################################################
	#	Make changes.
	########################################################
	rc =  myThreadPoolManager.modifyThreadPool( 
							name='WebContainer',
							minimumSize=50,
							maximumSize=50,
							inactivityTimeout=6000,
							isGrowable=True,
							description='Modified by pylib.Was.ThreadPoolManager.'
							)
	if rc: rc = myThreadPoolManager.createThreadPool( 
							name='DCSChannel',
							minimumSize=7,
							maximumSize=40,
							inactivityTimeout=5000,
							isGrowable=False,
							description='Created by pylib.Was.ThreadPoolManager.'
							)

	myThreadPoolManager.isThreadPoolExists( 'DCSChannel' )
	if rc: rc = myThreadPoolManager.deleteThreadPool( name='DCSChannel' )
	myThreadPoolManager.isThreadPoolExists( 'DCSChannel' )
	if rc: myThreadPoolManager.saveSession( False )

	configService.closeMe()
	myThreadPoolManager.closeMe()
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
