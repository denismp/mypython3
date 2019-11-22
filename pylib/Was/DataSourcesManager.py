#!/usr/bin/env jython
######################################################################################
##	DataSourcesManager.py
##
##	Python module replaces some of the functions in the 
##	/nfs/dist/dmp/amp/wdt/_resources.jacl 
##	file and makes DataSources resource management object oriented.
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

class DataSourcesManager( AttributeUtils ):
	"""
    DataSourcesManager class that contains DataSource management methods.
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
		AttributeUtils.__init__( self, configService, scope, type='DataSource', logger=self.logger )
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
	#	createMappingModule()
	#
	#	DESCRIPTION:
	#		Create the MappingModule.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createMappingModule(self, myparent, authDataAlias, mappingConfigAlias):
		"""Create the MappingModule.
		   PARAMETERS:
			   myparent           -- javax.management.ObjectName instance of a 'DataSource' type.
		       authDataAlias      -- something like 'node_ServicesA_00/DenisAlias'
			   mappingConfigAlias -- something like 'DefaultPrincipalMapping'
		   RETURN:
		       True if successful or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createMappingModule(): called.\n" )
		self.debug( __name__ + ".createMappingModule(): myparent=" + str( myparent ) + ".\n" )
		self.debug( __name__ + ".createMappingModule(): authDataAlias=" + str( authDataAlias ) + ".\n" )
		self.debug( __name__ + ".createMappingModule(): mappingConfigAlias=" + str( mappingConfigAlias ) + ".\n" )

		attributeList = AttributeList()

		self.configService.configServiceHelper.setAttributeValue( attributeList, 'mappingConfigAlias', mappingConfigAlias )	
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'authDataAlias', authDataAlias )	

		try:
			self.configService.createConfigData( self.configService.session, myparent, 'mapping', 'MappingModule', attributeList )
			self.refresh()
		except com.ibm.websphere.management.exception.ConfigServiceException, e:
			self.logIt( __name__ + ".createMappingModule(): Unable to create the MappingModule for " + str( mappingConfigAlias ) + ":" + str( e ) + "\n" )
			return False
		except com.ibm.websphere.management.exception.ConnectorException, ce:
			self.logIt( __name__ + ".createMappingModule(): Unable to create the MappingModule for " + str( mappingConfigAlias ) + ":" + str( ce ) + "\n" )
			return False
		#Endtry
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createJ2EEResourceProperty()
	#
	#	DESCRIPTION:
	#		Create the J2EEResourceProperty.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createJ2EEResourceProperty(
									self, 
									myparent, 
									dsname,
									name, 
									value,
									jtype='java.lang.String', 
									required=False, 
									description="created by pylib.Was.DataSourcesManager"
									):
		"""Create the J2EEResourceProperty.
		   PARAMETERS:
		       myparent       -- javax.management.ObjectName instance of a 'DataSource' type.
			   dsname         -- Something like 'ForOracleXAJF'
		       name           -- string containing the name of the property. Something like "MyCustomProperty".
		       value          -- the value for the property.  
		       jtype          -- string containing the java type of the property. Something like 'java.lang.String'
		                         or one of the other java.lang.<Type> class.
		       required       -- either True or False.
		       description    -- optional comment.  Somthing like ''.
		   RETURN:
		       True if successful or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createJ2EEResourceProperty(): called.\n" )
		self.debug( __name__ + ".createJ2EEResourceProperty(): myparent=" + str( myparent ) + ".\n" )
		self.debug( __name__ + ".createJ2EEResourceProperty(): dsname=" + str( dsname ) + ".\n" )
		self.debug( __name__ + ".createJ2EEResourceProperty(): name=" + str( name ) + ".\n" )
		self.debug( __name__ + ".createJ2EEResourceProperty(): jtype=" + str( jtype ) + ".\n" )
		self.debug( __name__ + ".createJ2EEResourceProperty(): value=" + str( value ) + ".\n" )
		self.debug( __name__ + ".createJ2EEResourceProperty(): value type=" + str( type( value ) ) + ".\n" )
		self.debug( __name__ + ".createJ2EEResourceProperty(): required=" + str( required ) + ".\n" )
		self.debug( __name__ + ".createJ2EEResourceProperty(): description=" + str( description ) + ".\n" )

		attributeList = AttributeList()

		self.configService.configServiceHelper.setAttributeValue( attributeList, 'name', str( name ) )	
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'type', str( jtype ) )	
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'value', str( value ) )	
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'description', description )	
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'required', java.lang.Boolean( required ) )	

		myargs					= array( ['propertySet'], java.lang.String )
		propertySetAttributes	= self.configService.getAttributes( self.configService.session, myparent, myargs, False )
		the_parent				= self.configService.configServiceHelper.getAttributeValue( propertySetAttributes, 'propertySet' )
		try:
			self.configService.createConfigData( self.configService.session, the_parent, 'resourceProperties', 'J2EEResourceProperty', attributeList )
			self.refresh()
		except com.ibm.websphere.management.exception.ConfigServiceException, e:
			self.logIt( __name__ + ".createJ2EEResourceProperty(): Unable to create the J2EEResourceProperty for " + str( dsname ) + ":" + str( e ) + "\n" )
			return False
		except com.ibm.websphere.management.exception.ConnectorException, ce:
			self.logIt( __name__ + ".createJ2EEResourceProperty(): Unable to create the J2EEResourceProperty for " + str( dsname ) + ":" + str( ce ) + "\n" )
			return False
		#Endtry
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createUrlJ2EEResourceProperty()
	#
	#	DESCRIPTION:
	#		Create the URL J2EEResourceProperty.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createUrlJ2EEResourceProperty(self, myparent, dsname, url, description="created by pylib.Was.DataSourcesManager"):
		"""Create the URL J2EEResourceProperty.
		   PARAMETERS:
			   myparent       -- javax.management.ObjectName instance of a 'DataSource' type.
			   dsname         -- Something like 'ForOracleXAJF'
		       url            -- string containing the url.  Somthing like 'jdbc:oracle:thin:@dedb11.mydomain.com:1521:INT9ITST'.
		       description    -- optional comment.  Somthing like ''.
		   RETURN:
		       True if successful or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createUrlJ2EEResourceProperty(): called.\n" )
		self.debug( __name__ + ".createUrlJ2EEResourceProperty(): myparent=" + str( myparent ) + ".\n" )
		self.debug( __name__ + ".createUrlJ2EEResourceProperty(): url=" + str( url ) + ".\n" )
		self.debug( __name__ + ".createUrlJ2EEResourceProperty(): description=" + str( description ) + ".\n" )

		rc = self.createJ2EEResourceProperty(
									myparent, 
									dsname,
									'URL', 
									url,
									jtype='java.lang.String', 
									required=True, 
									description="created by pylib.Was.DataSourcesManager"
									)
		if not rc:
			self.logIt( __name__ + ".createUrlJ2EEResourceProperty(): Failed to create J2EEResourceProperty\n" )
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createCMPConnectorFactory()
	#
	#	DESCRIPTION:
	#		Create the CMPConnectorFactory
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createCMPConnectorFactory(
									self, 
									myparent, 
									dsname,
									authMechanismPreference='BASIC_PASSWORD',
									authDataAlias='',
									xaRecoveryAuthAlias='',
									mappingConfigAlias='DefaultPrincipalMapping',
									transactionResourceRegistration='dynamic',
									inactiveConnectionSupport=True
									):
		"""Create the CMPConnectoryFactory.
		   PARAMETERS:
			   myparent                        -- javax.management.ObjectName instance of a 'DataSource' type.
			   dsname                          -- Something like 'ForOracleXAJF'
			   authMechanismPreference         -- Something like 'BASIC_PASSWORD' or 'KERBEROS'
			   authDataAlias                   -- Something like 'node_ServicesA_00/DenisAlias'
			   xaRecoveryAuthAlias             -- Something like 'node_ServicesA_00/DenisAlias'
			   mappingConfigAlias              -- Something like 'DefaultPrincipalMapping'
			   transactionResourceRegistration -- either 'static' or 'dynamic'.  NOT USED.
			   inactiveConnectionSupport       -- either True or False.  NOT USED.
		   RETURN:
		       True if successful or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createCMPConnectorFactory(): called.\n" )
		self.debug( __name__ + ".createCMPConnectorFactory(): myparent=" + str( myparent ) + ".\n" )
		self.debug( __name__ + ".createCMPConnectorFactory(): dsname=" + str( dsname ) + ".\n" )
		self.debug( __name__ + ".createCMPConnectorFactory(): authMechanismPreference=" + str( authMechanismPreference ) + ".\n" )
		self.debug( __name__ + ".createCMPConnectorFactory(): authDataAlias=" + str( authDataAlias ) + ".\n" )
		self.debug( __name__ + ".createCMPConnectorFactory(): xaRecoveryAuthAlias=" + str( xaRecoveryAuthAlias ) + ".\n" )
		self.debug( __name__ + ".createCMPConnectorFactory(): mappingConfigAlias=" + str( mappingConfigAlias ) + ".\n" )
		self.debug( __name__ + ".createCMPConnectorFactory(): transactionResourceRegistration=" + str( transactionResourceRegistration ) + ".\n" )
		self.debug( __name__ + ".createCMPConnectorFactory(): inactiveConnectionSupport=" + str( inactiveConnectionSupport ) + ".\n" )

		####################################################
		#	Set up the TransactionResourceRegistration
		####################################################
		transAttributeList = AttributeList()
		self.configService.configServiceHelper.setAttributeValue( transAttributeList, 'name', 'TransactionResourceRegistration'  )	
		self.configService.configServiceHelper.setAttributeValue( transAttributeList, 'type', 'java.lang.String'  )	
		self.configService.configServiceHelper.setAttributeValue( transAttributeList, 'value', transactionResourceRegistration  )	
		self.configService.configServiceHelper.setAttributeValue( transAttributeList, 'description', 'Type of transaction resource registration (enlistment). Valid values are either static (immediate) or dynamic (deferred).'  )	

		####################################################
		#	Set up the InactiveConnectionSupport
		####################################################
		inactiveList = AttributeList()
		self.configService.configServiceHelper.setAttributeValue( inactiveList, 'name', 'InactiveConnectionSupport'  )	
		self.configService.configServiceHelper.setAttributeValue( inactiveList, 'type', 'java.lang.Boolean'  )	
		self.configService.configServiceHelper.setAttributeValue( inactiveList, 'value', java.lang.Boolean( inactiveConnectionSupport ) )	
		self.configService.configServiceHelper.setAttributeValue( inactiveList, 'description', 'Specify whether connection handles support implicit reactivation. (Smart Handle support). Value may be true or false.'  )	

		resourcePropertiesArray = java.util.ArrayList()
		resourcePropertiesArray.add( transAttributeList )
		resourcePropertiesArray.add( inactiveList )
		resourcePropertiesList = AttributeList()
		self.configService.configServiceHelper.setAttributeValue( resourcePropertiesList, 'resourceProperties', resourcePropertiesArray  )	

		####################################################
		#	Set up the mapping.
		####################################################
		mappingAliasList = AttributeList()
		self.configService.configServiceHelper.setAttributeValue( mappingAliasList, 'authDataAlias', authDataAlias  )	
		self.configService.configServiceHelper.setAttributeValue( mappingAliasList, 'mappingConfigAlias', mappingConfigAlias  )	
		#mappingList = AttributeList()
		#self.configService.configServiceHelper.setAttributeValue( mappingList, 'mapping', mappingAliasList )	

		####################################################
		#	Add all the above to the allAttributesList.
		####################################################
		allAttributesList = AttributeList()
		self.configService.configServiceHelper.setAttributeValue( allAttributesList, 'name', str( dsname ) + "_CF" )	
		self.configService.configServiceHelper.setAttributeValue( allAttributesList, 'authMechanismPreference', authMechanismPreference  )	
		self.configService.configServiceHelper.setAttributeValue( allAttributesList, 'authDataAlias', authDataAlias )	
		self.configService.configServiceHelper.setAttributeValue( allAttributesList, 'xaRecoveryAuthAlias', xaRecoveryAuthAlias )	
		self.configService.configServiceHelper.setAttributeValue( allAttributesList, 'cmpDatasource', myparent )	
		self.configService.configServiceHelper.setAttributeValue( allAttributesList, 'mapping', mappingAliasList )	
		###############################
		#	Below doesn't work.
		###############################
		#self.configService.configServiceHelper.setAttributeValue( allAttributesList, 'propertySet', resourcePropertiesList )	

		self.debug( __name__ + ".createCMPConnectorFactory(): allAttributesList=" + str(  allAttributesList ) + "\n" )

		myargs			= array( ['relationalResourceAdapter'], java.lang.String )
		configAttributes= self.configService.getAttributes( self.configService.session, myparent, myargs, False )
		#configAttributes= self.configService.getAttributes( self.configService.session, myparent, None, False )
		self.debug( __name__ + ".createCMPConnectorFactory(): configAttributes=" + str(  configAttributes ) + "\n" )
		the_parent		= self.configService.configServiceHelper.getAttributeValue( configAttributes, 'relationalResourceAdapter' )
		self.debug( __name__ + ".createCMPConnectorFactory(): the_parent=" + str(  the_parent ) + "\n" )
		#rc				= self.createConfigData( 'relationalResourceAdapter', 'CMPConnectorFactory', allAttributesList, myparent=the_parent )

		try:
			self.configService.createConfigData( self.configService.session, the_parent, 'CMPConnectorFactory', 'CMPConnectorFactory', allAttributesList )
			self.refresh()
		except com.ibm.websphere.management.exception.ConfigServiceException, e:
			self.logIt( __name__ + ".createCMPConnectorFactory(): Unable to create the CMPConnectorFactory for " + str( dsname ) + ":" + str( e ) + "\n" )
			return False
		except com.ibm.websphere.management.exception.ConnectorException, ce:
			self.logIt( __name__ + ".createCMPConnectorFactory(): Unable to create the CMPConnectorFactory for " + str( dsname ) + ":" + str( ce ) + "\n" )
			return False
		#Endtry
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createConnectionPool()
	#
	#	DESCRIPTION:
	#		Create the ConnectionPool
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createConnectionPool(
								self, 
								myparent, 
								dsname,
								connectionTimeout=180,
								maxConnections=10,
								minConnections=1,
								reapTime=180,
								unusedTimeout=1800,
								agedTimeout=0,
								purgePolicy='EntirePool',
								numberOfSharedPoolPartitions=0,
								numberOfUnsharedPoolPartitions=0,
								numberOfFreePoolPartitions=0,
								freePoolDistributionTableSize=0,
								surgeThreshold=0,
								surgeCreationInterval=-1,
								testConnection=False,
								testConnectionInterval=0,
								stuckTimerTime=0,
								stuckTime=0,
								stuckThreshold=0
								):
		"""Create the ConnectionPool.
		   PARAMETERS:
			   myparent                      -- javax.management.ObjectName instance of a 'DataSource' type.
			   dsname                        -- Something like 'ForOracleXAJF'
			   connectionTimeout             -- Connection timeout is the interval, in seconds, after which a connection request 
                                                times out and a ConnectionWaitTimeoutException is thrown. The wait may be necessary 
                                                if the maximum value of connections to a particular connection pool has been 
                                                reached (Max Connections) . This value has no meaning if Max Connections is set 
                                                to 0 (infinite number of ManagedConnections). If Connection Timeout is set to 0 
                                                the Pool Manager waits until a connection can be allocated 
                                                (which happens when the number of connections falls below Max Connections). 
			   maxConnections                -- The maximum number of managed connections that can be created by a particular 
                                                ManagedConnectionFactory. After this number is reached, no new connections are 
                                                created and either the requester waits for the Connection Timeout or the 
                                                ResourceAllocationException is thrown. If Maximum Connections is set to 0 (zero), 
                                                the number of connections can grow indefinitely. Maximum Connections must be 
                                                larger than or equal to Minimum Connections.
			   minConnections                -- The minimum number of managed connections to maintain. If this number is 
                                                reached, the garbage collector will not discard any managed connections. 
                                                Note, if the actual number of connections is lower than the value specified 
                                                by the minimum connections settings, no attempt will be made to increase the 
                                                number of connections to the minimum. Minimum Connections must be less than 
                                                or equal to Maximum Connections.
			   reapTime                      -- Number of seconds between runs of the garbage collector. The garbage 
                                                collector discards all connections that have been unused for the value 
                                                specified by the Unused Timeout.

                                                To disable the garbage collector, set the reap time to 0 (zero) or set the 
                                                Unused Timeout to 0 (zero). 
			   unusedTimeout                 -- Interval, in seconds, after which an unused connection is discarded by the 
                                                pool maintenance thread.
			   agedTimeout                   -- Interval, in seconds, after which an unused, aged connection is discarded 
                                                (regardless of recent usage activity) by the pool maintenance thread.
			   purgePolicy                   -- either 'EntirePool' or 'FailingConnectionOnly'.  Whenever a fatal connection 
                                                error signal is received by the Connection Pool Manager, the Connection 
                                                Pool Manager needs to either remove just the failing connection or to remove 
                                                all of the connections in the pool. This Purge Policy setting will determine 
                                                the action of the Connection Pool Manager.
			   numberOfSharedPoolPartions    -- The number of buckets or partitions that are created in each of the shared pools.
			   numberOfUnsharedPoolPartions  -- The number of buckets or partitions that are created in each of the unshared pools.
			   numberOfFreePoolPartitions    -- The number of buckets or partitions that are created in each of the free pools.
			   freePoolDistributionTableSize -- If there are many incoming requests with varying credentials, this value can 
                                                help with the distribution of finding a free pool for a connection for that user. 
                                                Larger values are more common for installations that have many different 
                                                credentials accessing the resource. Smaller values (0) should be used if the 
                                                same credentials apply to all incoming requests for the resource. 0=Random Distribution.
			   surgeThreshold                -- Once the number of connections in the pool exceeds this threshold, The rate 
                                                at which connections are created will be throttled/limited based on the 
                                                surgeCreationInterval setting. Once the threshold has been reached, the surge 
                                                creation interval will be applied until the number of connections in the pool 
                                                drops below the threshold again. Must be less than the max connections setting 
                                                for this pool and greater than the min connections setting A value of -1 
                                                disables surge protection.
			   surgeCreationInterval         -- The period of time to wait before connections are created again once the surge 
                                                threshold has been reached.
			   testConnection                -- True or False.
			   testConnectionInterval        -- interval of the test connection retry thread.
			   stuckTimerTime                -- Frequency of stuck time thread.
			   stuckTime                     -- Connection stuck time.
			   stuckThreshold                -- Number of connections threshold.
		   RETURN:
		       True if successful or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createConnectionPool(): called.\n" )
		self.debug( __name__ + ".createConnectionPool(): myparent=" + str( myparent ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): dsname=" + str( dsname ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): connectionTimeout=" + str( connectionTimeout ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): maxConnections=" + str( maxConnections ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): minConnections=" + str( minConnections ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): reapTime=" + str( reapTime ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): unusedTimeout=" + str( unusedTimeout ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): agedTimeout=" + str( agedTimeout ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): purgePolicy=" + str( purgePolicy ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): numberOfSharedPoolPartitions=" + str( numberOfSharedPoolPartitions ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): numberOfUnsharedPoolPartitions=" + str( numberOfUnsharedPoolPartitions ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): numberOfFreePoolPartitions=" + str( numberOfFreePoolPartitions ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): freePoolDistributionTableSize=" + str( freePoolDistributionTableSize ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): surgeThreshold=" + str( surgeThreshold ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): surgeCreationInterval=" + str( surgeCreationInterval ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): testConnection=" + str( testConnection ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): testConnectionInterval=" + str( testConnectionInterval ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): stuckTimerTime=" + str( stuckTimerTime ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): stuckTime=" + str( stuckTime ) + ".\n" )
		self.debug( __name__ + ".createConnectionPool(): stuckThreshold=" + str( stuckThreshold ) + ".\n" )

		####################################################
		#	Add all the above to the connectionPoolAttributeList.
		####################################################
		connectionPoolAttributeList = AttributeList()
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'connectionTimeout', java.lang.Long( connectionTimeout ) )
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'maxConnections', int( maxConnections ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'minConnections', int( minConnections ) )
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'reapTime', java.lang.Long( reapTime ) )
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'unusedTimeout', java.lang.Long( unusedTimeout ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'agedTimeout', java.lang.Long( agedTimeout ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'purgePolicy', str( purgePolicy ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'numberOfSharedPoolPartitions', int( numberOfSharedPoolPartitions ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'numberOfUnsharedPoolPartitions', int( numberOfUnsharedPoolPartitions ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'numberOfFreePoolPartitions', int( numberOfFreePoolPartitions ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'freePoolDistributionTableSize', int( freePoolDistributionTableSize ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'surgeThreshold', int( surgeThreshold ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'surgeCreationInterval', int (surgeCreationInterval ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'testConnection', java.lang.Boolean( testConnection ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'testConnectionInterval', int( testConnectionInterval ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'stuckTimerTime', int( stuckTimerTime ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'stuckTime', int( stuckTime ) )	
		self.configService.configServiceHelper.setAttributeValue( connectionPoolAttributeList, 'stuckThreshold', int( stuckThreshold ) )	

		self.debug( __name__ + ".createConnectionPool(): connectionPoolAttributeList=" + str( connectionPoolAttributeList ) + "\n" )

		the_parent = myparent

		try:
			self.configService.createConfigData( self.configService.session, the_parent, 'connectionPool', 'ConnectionPool', connectionPoolAttributeList )
			self.refresh()
		except com.ibm.websphere.management.exception.ConfigServiceException, e:
			self.logIt( __name__ + ".createConnectionPool(): Unable to create the ConnectionPool for " + str( dsname ) + ":" + str( e ) + "\n" )
			return False
		except com.ibm.websphere.management.exception.ConnectorException, ce:
			self.logIt( __name__ + ".createConnectionPool(): Unable to create the ConnectionPool for " + str( dsname ) + ":" + str( ce ) + "\n" )
			return False
		#Endtry
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	addDataSource()
	#
	#	DESCRIPTION:
	#		Add a DataSource to websphere.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def addDataSource(
						self,
						providerObject,
						dataSourceName,
						templateId,
						jndiName,
						providerType,
						authDataAlias,
						authMechanismPreference,
						xaRecoveryAuthAlias,
						datasourceHelperClassname,
						category='user_defined',
						statementCacheSize='10',
						manageCachedHandles=False,
						logMissingTransactionContext=False,
						diagnoseConnectionUsage=False,
						description="This DataSource was created by the pylib.Was.DataSourcesManager."
						):
		"""Add a DataSource to websphere.
		   PARAMETERS:
			   providerObject                 -- javax.management.ObjectName instance of the JDBC provider. Something like 'OracleJdbcDriverXA'.
		       dataSourceName                 -- name of the DataSource.  Something like 'ForOracleXAJF'
		       templateId                     -- name of the DataSoure template.  Something like 'DataSource_ora_6'
			   jndiName                       -- DataSource jndiName.  Something like 'jdbc/ForOracleXAJF'
			   providerType                   -- Something like 'Oracle JDBC Driver (XA)'
			   authDataAlias                  -- Something like 'node_ServicesA_00/DenisAlias'
			   authMechanismPreference        -- Something like 'BASIC_PASSWORD'
			   xaRecoveryAuthAlias            -- Something like 'node_ServicesA_00/DenisAlias'
			   datasourceHelperClassname      -- Something like 'com.ibm.websphere.rsadapter.Oracle10gDataStoreHelper'
			   category                       -- Something like 'default' or None
			   statementCacheSize             -- Something like '10'
			   manageCachedHandles            -- True or False.
			   logMissingTransactionContext   -- True or False.
			   diagnoseConnectionUsage        -- True or False.
			   description                    -- description text.
		   RETURN:
		       True if successful or the dataSourceName exists, or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".addDataSource(): called.\n" )
		self.debug( __name__ + ".addDataSource(): providerObject=" + str( providerObject ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): dataSourceName=" + str( dataSourceName ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): templateId=" + str( templateId ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): jndiName=" + str( jndiName ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): providerType=" + str( providerType ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): authDataAlias=" + str( authDataAlias ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): authMechanismPreference=" + str( authMechanismPreference ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): xaRecoveryAuthAlias=" + str( xaRecoveryAuthAlias ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): datasourceHelperClassname=" + str( datasourceHelperClassname ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): category=" + str( category ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): statementCacheSize=" + str( statementCacheSize ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): manageCachedHandles=" + str( manageCachedHandles ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): logMissingTransactionContext=" + str( logMissingTransactionContext ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): diagnoseConnectionUsage=" + str( diagnoseConnectionUsage ) + ".\n" )
		self.debug( __name__ + ".addDataSource(): description=" + str( description ) + ".\n" )

		#######################################################
		#	Check to see if the given dataSourceName already exists.
		#######################################################
		if self.isDataSourceExist( dataSourceName ):
			self.logIt( __name__ + ".addDataSource(): DataSource " + str( dataSourceName ) + " already exists, so it will not be added." + ".\n" )
			return True
		#Endif

		self.logIt( __name__ + ".addDataSource(): DataSource " + str( dataSourceName ) + " doesn't exist, so it will be added." + ".\n" )
	
		######################################################
		#	Set up the attributes.
		######################################################
		nameAttr					= Attribute( 'name', 						dataSourceName )
		desAttr						= Attribute( 'description', 				description )
		jndiAttr					= Attribute( 'jndiName', 					jndiName )	
		providerTypeAttr			= Attribute( 'providerType', 				providerType )	
		authDataAliasAttr			= Attribute( 'authDataAlias', 				authDataAlias )	
		authMechanismPreference		= Attribute( 'authMechanismPreference', 	authMechanismPreference )	
		xaRecoveryAuthAlias			= Attribute( 'xaRecoveryAuthAlias', 		xaRecoveryAuthAlias )	
		datasourceHelperClassname	= Attribute( 'datasourceHelperClassname',	datasourceHelperClassname )	
		manageCachedHandles			= Attribute( 'manageCachedHandles', 		manageCachedHandles )	
		logMissingTransactionContext= Attribute( 'logMissingTransactionContext',logMissingTransactionContext )	
		diagnoseConnectionUsage		= Attribute( 'diagnoseConnectionUsage',		diagnoseConnectionUsage )	
		category					= Attribute( 'category', 					category )	
		statementCacheSize			= Attribute( 'statementCacheSize', 			int( statementCacheSize ) )	

		######################################################
		#	Build the AttribtueList.
		######################################################
		myAttrList	= AttributeList()

		myAttrList.add( nameAttr )
		myAttrList.add( desAttr )
		myAttrList.add( jndiAttr )
		myAttrList.add( providerTypeAttr )
		myAttrList.add( authDataAliasAttr )
		myAttrList.add( authMechanismPreference )
		myAttrList.add( xaRecoveryAuthAlias )
		myAttrList.add( datasourceHelperClassname )
		myAttrList.add( manageCachedHandles )
		myAttrList.add( logMissingTransactionContext )
		myAttrList.add( diagnoseConnectionUsage )
		myAttrList.add( category )
		myAttrList.add( statementCacheSize )

		#######################################################
		#	Create the DataSource.
		#######################################################
		rc = self.createConfigDataWithTemplate( templateId, 'DataSource', myAttrList, myparent=providerObject )
		
		return rc
		
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	isDataSourceExist()
	#
	#	DESCRIPTION:
	#		Does the DataSource exist.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def isDataSourceExist( self, dsname):
		"""Does the DataSource exist.
		   PARAMETERS:
		       dsname  -- name of the DataSource.  Something like 'ForOracleXAJF'
		   RETURN:
		       True if successful, or False.
		"""
		#######################################################
		#	Check to see if the given DataSource exists.
		#######################################################
		myvalues = self.getAttributeValues( 'name' )
		for value in myvalues:
			if value == dsname:
				return True
		#Endfor
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	deleteDataSource()
	#
	#	DESCRIPTION:
	#		Delete the DataSource by the given name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deleteDataSource( self, dsname):
		"""Delete the DataSource by the given name.
		   PARAMETERS:
		       dsname  -- name of the DataSource.  Something like 'ForOracleXAJF'
		   RETURN:
		       True if successful, or False.
		"""
		#######################################################
		#	Delete the datasource
		#######################################################
		rVal = True
		myvalues = self.getAttributeValues( 'name' )
		for value in myvalues:
			if value == dsname:
				self.logIt( __name__ + ".deleteDataSource(): DataSource " + str( dsname ) + " exists, so it will be deleted." + ".\n" )
				configObject = self.getConfigObjectByDisplayName( dsname )
				rc = self.deleteConfigData( configObject )
				if not rc: rVal = False
		#Endfor
		if rVal: self.refresh()
		return rVal
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createDataSource()
	#
	#	DESCRIPTION:
	#		Create a DataSource.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createDataSource(
						self,
						providerObject,
						dataSourceName,
						templateId,
						jndiName,
						providerType,
						authDataAlias,
						authMechanismPreference,
						xaRecoveryAuthAlias,
						datasourceHelperClassname,
						category='user_defined',
						statementCacheSize='10',
						manageCachedHandles=False,
						logMissingTransactionContext=False,
						diagnoseConnectionUsage=False,
						description="This DataSource was created by the pylib.Was.DataSourcesManager."
						):
		"""Create a DataSource.
		   PARAMETERS:
			   providerObject                 -- javax.management.ObjectName instance of the JDBC provider. Something like 'OracleJdbcDriverXA'.
		       dataSourceName                 -- name of the DataSource.  Something like 'ForOracleXAJF'
		       templateId                     -- name of the DataSoure template.  Something like 'DataSource_ora_6'
			   jndiName                       -- DataSource jndiName.  Something like 'jdbc/ForOracleXAJF'
			   providerType                   -- Something like 'Oracle JDBC Driver (XA)'
			   authDataAlias                  -- Something like 'node_ServicesA_00/DenisAlias'
			   authMechanismPreference        -- Something like 'BASIC_PASSWORD'
			   xaRecoveryAuthAlias            -- Something like 'node_ServicesA_00/DenisAlias'
			   datasourceHelperClassname      -- Something like 'com.ibm.websphere.rsadapter.Oracle10gDataStoreHelper'
			   category                       -- Something like 'default' or None
			   statementCacheSize             -- Something like '10'
			   manageCachedHandles            -- True or False.
			   logMissingTransactionContext   -- True or False.
			   diagnoseConnectionUsage        -- True or False.
			   description                    -- description text.
		   RETURN:
		       True if successful or the dataSourceName exists, or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createDataSource(): called.\n" )
		self.debug( __name__ + ".createDataSource(): providerObject=" + str( providerObject ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): dataSourceName=" + str( dataSourceName ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): templateId=" + str( templateId ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): jndiName=" + str( jndiName ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): providerType=" + str( providerType ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): authDataAlias=" + str( authDataAlias ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): authMechanismPreference=" + str( authMechanismPreference ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): xaRecoveryAuthAlias=" + str( xaRecoveryAuthAlias ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): datasourceHelperClassname=" + str( datasourceHelperClassname ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): category=" + str( category ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): statementCacheSize=" + str( statementCacheSize ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): manageCachedHandles=" + str( manageCachedHandles ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): logMissingTransactionContext=" + str( logMissingTransactionContext ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): diagnoseConnectionUsage=" + str( diagnoseConnectionUsage ) + ".\n" )
		self.debug( __name__ + ".createDataSource(): description=" + str( description ) + ".\n" )

		############################################################
		#	Check to see if the given dataSourceName already exists.
		############################################################
		if self.isDataSourceExist( dataSourceName ):
			self.logIt( __name__ + ".createDataSource(): DataSource " + str( dataSourceName ) + " already exists, so it will be deleted and then added." + ".\n" )
			self.deleteDataSource( dataSourceName )
		#Endif
		self.logIt( __name__ + ".createDataSource(): DataSource adding " + str( dataSourceName ) + ".\n" )

		rc = self.addDataSource( 
								providerObject,
								dataSourceName, 
								templateId, 
								jndiName, 
								providerType,
								authDataAlias,
								authMechanismPreference,
								xaRecoveryAuthAlias,
								datasourceHelperClassname,
								category,
								statementCacheSize,
								manageCachedHandles,
								logMissingTransactionContext,
								diagnoseConnectionUsage,
								description=description 
								)
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
	myLogger	= MyLogger( LOGFILE="/tmp/DataSourcesManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/DataSourcesManager.log", STDOUT=True, DEBUG=False )
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

	myscope	= "ServerCluster=" + clusterName + ":JDBCProvider=" + jdbcProvider + ":DataSource=" + dataSource
	#myscope	= "ServerCluster=" + clusterName + ":DataSource=" + dataSource
	#myscope	= "ServerCluster=" + clusterName 
	#myscope	= "Cell=" + cellName 
	#myscope		= "ServerCluster=" + clusterName + ":JDBCProvider=" + jdbcProvider
	configService 			= ConfigService( adminClient=myclient, logger=myLogger )
	templateListManager		= TemplateListManager( configService, type="DataSource", logger=myLogger )
	#myDataSourcesManager	= DataSourcesManager( adminObject, configService, templateListManager, scope="Cell=ServicesA", logger=myLogger)
	myDataSourcesManager	= DataSourcesManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in myDataSourcesManager.attributesList:
		myDataSourcesManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myDataSourcesManager.attributesList:
		myDataSourcesManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myDataSourcesManager.attributesList:
			myDataSourcesManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	myDataSourcesManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/DataSources.tsv" )

	jdbcScope	= "ServerCluster=" + clusterName + ":JDBCProvider=" + jdbcProvider
	myJDBCProviderManager	= JDBCProviderManager( adminObject, configService, templateListManager, scope=jdbcScope, logger=myLogger)
	jdbcConfigObject		= myJDBCProviderManager.getConfigObjectByDisplayName( 'OracleJdbcDriverXA' )
	myLogger.logIt( "main(): jdbcConfigObject=" + str( jdbcConfigObject ) + "\n" )

	########################################################
	#	Set up customProperties
	########################################################

	########################################################
	#	Create the data source.
	########################################################
	rc = myDataSourcesManager.createDataSource( 
											jdbcConfigObject, 										# JDBCProvider
											'ForOracleXAJF', 										# DataSourceName
											'DataSource_ora_6', 									# Template to use.
											'jdbc/ForOracleXAJF', 									# jndiName
											'Oracle JDBC Driver (XA)', 								# providerType
											'node_ServicesA_00/DenisAlias', 						# authDataAlias
											'BASIC_PASSWORD', 										# authMechanismPreference
											'node_ServicesA_00/DenisAlias', 						# xaRecoveryAuthAlias
											'com.ibm.websphere.rsadapter.Oracle10gDataStoreHelper', # datasourceHelperClassname
											category='denis_category', 
											statementCacheSize='10', 
											manageCachedHandles=False, 
											logMissingTransactionContext=False, 
											diagnoseConnectionUsage=False 
											)

	myparent = myDataSourcesManager.myLastConfiguredObject
	mappingConfigAlias	= 'DefaultPrincipalMapping'
	authDataAlias		= 'node_ServicesA_00/DenisAlias'
	dsname = 'ForOracleXAJF'
	if rc:
		#################################################
		#	Now do the mapping.
		#################################################
		rc = myDataSourcesManager.createMappingModule( myparent, authDataAlias, mappingConfigAlias )
		if not rc:
			myLogger.logIt( "main(): Unable to create the MappingModule for " + str( mappingConfigAlias ) + ".\n" )
		else:
			########################################################################
			#	Create the J2EEResourceProperty to create the
			#	name = URL, type = java.lang.String, description = '', 
			#	value = 'jdbc:oracle:thin:@dedb11.mydomain.com:1521:INT9ITST',
			#	required = True
			########################################################################
			url = 'jdbc:oracle:thin:@dedb11.mydomain.com:1521:INT9ITST'
			rc = myDataSourcesManager.createUrlJ2EEResourceProperty( myparent, dsname, url )
			if not rc:
				myLogger.logIt( "main(): Unable to create the J2EEResourceProperty for " + str( url ) + ".\n" )
			#Endif
		#Endif
	#Endif
	if rc:
		################################################
		#	ConnectionPool example.
		################################################
		rc = myDataSourcesManager.createCMPConnectorFactory(
									myparent, 
									dsname,
									authMechanismPreference='BASIC_PASSWORD',
									authDataAlias='node_ServicesA_00/DenisAlias',
									xaRecoveryAuthAlias='node_ServicesA_00/DenisAlias',
									mappingConfigAlias='DefaultPrincipalMapping',
									transactionResourceRegistration='dynamic',
									inactiveConnectionSupport=True
									)
		if not rc:
			myLogger.logIt( "main(): Unable to create the CMPConnectorFactory for " + str( dsname ) + ".\n" )
	#Endif
	if rc:
		################################################
		#	ConnectionPool example.
		################################################
		rc = myDataSourcesManager.createConnectionPool(
								myparent, 
								dsname,
								connectionTimeout=180,
								maxConnections=19,
								minConnections=1,
								reapTime=180,
								unusedTimeout=1800,
								agedTimeout=0,
								purgePolicy='EntirePool',
								numberOfSharedPoolPartitions=0,
								numberOfUnsharedPoolPartitions=0,
								numberOfFreePoolPartitions=0,
								freePoolDistributionTableSize=0,
								surgeThreshold=0,
								surgeCreationInterval=-1,
								testConnection=False,
								testConnectionInterval=0,
								stuckTimerTime=0,
								stuckTime=0,
								stuckThreshold=0
								)
		if not rc:
			myLogger.logIt( "main(): Unable to create the ConnectionPool for " + str( dsname ) + ".\n" )
		else:
			myLogger.logIt( "main(): CREATED the ConnectionPool for " + str( dsname ) + ".\n" )
	#Endif
	if rc:
		################################################
		#	Custom DataSource property example.
		################################################
		name = "CustomDenisProperty"
		value = '9'
		rc = myDataSourcesManager.createJ2EEResourceProperty(
								myparent, 
								dsname,
								name, 
								value,
								jtype='java.lang.Integer', 
								required=True, 
								description="created by pylib.Was.DataSourcesManager"
								)
		if not rc:
			myLogger.logIt( "main(): Unable to create the J2EEResourceProperty for " + str( dsname ) + ".\n" )
		else:
			myLogger.logIt( "main(): CREATED the J2EEResourceProperty for " + str( dsname ) + ".\n" )
		#Endif
	#Endif

	if rc: myDataSourcesManager.saveSession( False )

	configService.closeMe()
	myDataSourcesManager.closeMe()
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
