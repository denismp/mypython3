#!/usr/bin/env jython
######################################################################################
##	SessionManager.py
##
##	Python module for the SessionManage attrbributes.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	01/19/2010	Denis M. Putnam		Created.
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

class SessionManager( AttributeUtils ):
	"""
    SessionManager class that contains SessionManager management methods.
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
		AttributeUtils.__init__( self, configService, scope, type='SessionManager', logger=self.logger )
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
	#	modifyDefaultCookieSettings()
	#
	#	DESCRIPTION:
	#		Modify the defaultCookieSettings attributes.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifyDefaultCookieSettings( 
							self, 
							sessionManagerConfigObject,
							sessionManagerAttributeList,
							name='JSESSIONID',
							domain='',
							maximumAge=-1,
							path='/',
							secure=False
							):
		"""Modify the defaultCookieSettings attributes.
		   PARAMETERS:
			   sessionManagerConfigObject   -- javax.management.ObjectName instance of the SessionManager.
			   sessionManagerAttributeList  -- javax.management.AttributeList instance of the SessionManager.
			   name                         -- must be 'JSESSIONID' according to WebSphere documentation.
			   domain                       -- Defaults to ''
			   maximumAge                   -- Defaults to -1
			   path                         -- Defaults to '/'
			   secure                       -- Defaults to False.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifyDefaultCookieSettings(): sessionManagerConfigObject=" + str( sessionManagerConfigObject ) + "\n" )
		self.debug( __name__ + ".modifyDefaultCookieSettings(): sessionManagerAttributeList=" + str( sessionManagerAttributeList ) + "\n" )
		self.debug( __name__ + ".modifyDefaultCookieSettings(): name=" + str( name ) + "\n" )
		self.debug( __name__ + ".modifyDefaultCookieSettings(): domain=" + str( domain ) + "\n" )
		self.debug( __name__ + ".modifyDefaultCookieSettings(): maximumAge=" + str( maximumAge ) + "\n" )
		self.debug( __name__ + ".modifyDefaultCookieSettings(): path=" + str( path ) + "\n" )
		self.debug( __name__ + ".modifyDefaultCookieSettings(): secure=" + str( secure ) + "\n" )

		####################################################################
		#	Do the defaultCookieSettings.
		####################################################################
		myargs	= array( ['defaultCookieSettings'], java.lang.String )
		defaultCookieSettings	= self.configService.getAttributes( self.configService.session, sessionManagerConfigObject, myargs, False )
		defaultCookieSettingsObject = None
		for cAttr in defaultCookieSettings:
			cName = cAttr.getName()
			cValue= cAttr.getValue()
			############################################################################
			#	If the name of the attribute is defaultCookieSettings, then capture
			#	the value because it is the ObjectName instance the we need.
			############################################################################
			if cName == 'defaultCookieSettings':
				defaultCookieSettingsObject = cAttr.getValue()
			self.debug( __name__ + ".modifyDefaultCookieSettings(): cAttr.getName()=" + str( cName ) + "\n" )
			self.debug( __name__ + ".modifyDefaultCookieSettings(): cAttr.getValue()=" + str( cValue ) + "\n" )
		#Endfor
		if defaultCookieSettingsObject is None:
			self.logIt( __name__ + ".modifyDefaultCookieSettings(): Unable to obtain defaultCookieSettingsObject" + "\n" )
			return False
		#Endif

		#####################################################################
		#	Now get the attributes list for the defaultCookieSettingsObject.
		#####################################################################
		cookieAttrs	= self.configService.getAttributes( self.configService.session, defaultCookieSettingsObject, None, False )

		#####################################################################
		#	Set the attributes to the parameters that were passed in.
		#####################################################################
		self.debug( __name__ + ".modifyDefaultCookieSettings(): BEFORE cookieAttrs=" + str( cookieAttrs ) + "\n" )
		self.debug( __name__ + ".modifyDefaultCookieSettings(): BEFORE cookieAttrs type=" + str( type( cookieAttrs ) ) + "\n" )
		self.debug( __name__ + ".modifyDefaultCookieSettings(): cookieAttrs=" + str( cookieAttrs ) + "\n" )
		self.debug( __name__ + ".modifyDefaultCookieSettings(): cookieAttrs type=" + str( type( cookieAttrs ) ) + "\n" )
		self.configService.configServiceHelper.setAttributeValue( cookieAttrs, 'name', str( name ) )
		self.configService.configServiceHelper.setAttributeValue( cookieAttrs, 'domain', str( domain ) )
		self.configService.configServiceHelper.setAttributeValue( cookieAttrs, 'maximumAge', int( maximumAge ) )
		self.configService.configServiceHelper.setAttributeValue( cookieAttrs, 'path', str( path ) )
		self.configService.configServiceHelper.setAttributeValue( cookieAttrs, 'secure', java.lang.Boolean( secure ) )
		self.debug( __name__ + ".modifyDefaultCookieSettings(): AFTER cookieAttrs=" + str( cookieAttrs ) + "\n" )

		####################################################################
		#	Save the cookieAttrs to the current session.
		####################################################################
		self.configService.setAttributes( self.configService.session, defaultCookieSettingsObject, cookieAttrs )

		####################################################################
		#	Go back and get the defaultCookieSettingsObject attributes from
		#	the session that we just saved them to.
		####################################################################
		cookieAttrs = self.configService.getAttributes( self.configService.session, defaultCookieSettingsObject, None, False )

		####################################################################
		#	Now add the defaultCookieSettings attributes to the
		#	SessionManager attributes.
		####################################################################
		self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'defaultCookieSettings', cookieAttrs )

		self.configService.setAttributes( self.configService.session, sessionManagerConfigObject, sessionManagerAttributeList )
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	modifyInvalidationSchedule()
	#
	#	DESCRIPTION:
	#		Modify the invalidationSchedule attributes.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifyInvalidationSchedule( 
							self, 
							tuningParamsConfigObject,
							tuningParamsAttributeList,
							firstHour=14,
							secondHour=2
							):
		"""Modify the invalidationSchedule attributes.
		   PARAMETERS:
			   tuningParamsConfigObject     -- javax.management.ObjectName instance of the InvalidationSchedule.
			   tuningParamsAttributeList    -- javax.management.AttributeList instance of the InvalidationSchedule.
			   firstHour                    -- Defaults to 14.
			   secondHour                   -- Defaults to 2.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifyInvalidationSchedule(): tuningParamsConfigObject=" + str( tuningParamsConfigObject ) + "\n" )
		self.debug( __name__ + ".modifyInvalidationSchedule(): tuningParamsAttributeList=" + str( tuningParamsAttributeList ) + "\n" )
		self.debug( __name__ + ".modifyInvalidationSchedule(): firstHour=" + str( firstHour ) + "\n" )
		self.debug( __name__ + ".modifyInvalidationSchedule(): secondHour=" + str( secondHour ) + "\n" )

		####################################################################
		#	Do the tuningParamSettings.
		####################################################################
		myargs	= array( ['invalidationSchedule'], java.lang.String )
		invalidationScheduleAttributes	= self.configService.getAttributes( self.configService.session, tuningParamsConfigObject, myargs, False )
		invalidationScheduleObject = None
		for myAttr in invalidationScheduleAttributes:
			myName = myAttr.getName()
			myValue= myAttr.getValue()
			############################################################################
			#	If the name of the attribute is invalidationSchedule, then capture
			#	the value because it is the ObjectName instance the we need.
			############################################################################
			if myName == 'invalidationSchedule':
				invalidationScheduleObject = myAttr.getValue()
			self.debug( __name__ + ".modifyInvalidationSchedule(): myAttr.getName()=" + str( myName ) + "\n" )
			self.debug( __name__ + ".modifyInvalidationSchedule(): myAttr.getValue()=" + str( myValue ) + "\n" )
		#Endfor
		if invalidationScheduleObject is None:
			self.logIt( __name__ + ".modifyInvalidationSchedule(): Unable to obtain invalidationScheduleObject" + "\n" )
			return False
		#Endif
		self.debug( __name__ + ".modifyInvalidationSchedule(): invalidationScheduleObject=" + str( invalidationScheduleObject ) + "\n" )
		self.debug( __name__ + ".modifyInvalidationSchedule(): invalidationScheduleObject type=" + str( type( invalidationScheduleObject ) ) + "\n" )

		#####################################################################
		#	Now get the attributes list for the invalidationScheduleObject.
		#####################################################################
		attributeList	= self.configService.getAttributes( self.configService.session, invalidationScheduleObject, None, False )

		#####################################################################
		#	Set the attributes to the parameters that were passed in.
		#####################################################################
		self.debug( __name__ + ".modifyInvalidationSchedule(): BEFORE attributeList=" + str( attributeList ) + "\n" )
		self.debug( __name__ + ".modifyInvalidationSchedule(): BEFORE attributeList type=" + str( type( attributeList ) ) + "\n" )
		self.debug( __name__ + ".modifyInvalidationSchedule(): attributeList=" + str( attributeList ) + "\n" )
		self.debug( __name__ + ".modifyInvalidationSchedule(): attributeList type=" + str( type( attributeList ) ) + "\n" )
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'firstHour', int( firstHour ) )
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'secondHour', int( secondHour ) )
		self.debug( __name__ + ".modifyInvalidationSchedule(): AFTER attributeList=" + str( attributeList ) + "\n" )

		####################################################################
		#	Save the attributeList to the current session.
		####################################################################
		self.configService.setAttributes( self.configService.session, invalidationScheduleObject, attributeList )

		####################################################################
		#	Go back and get the invalidationScheduleObject attributes from
		#	the session that we just saved them to.
		####################################################################
		attributeList = self.configService.getAttributes( self.configService.session, invalidationScheduleObject, None, False )

		####################################################################
		#	Now add the invalidationSchedule attributes to the
		#	SessionManager attributes.
		####################################################################
		self.configService.configServiceHelper.setAttributeValue( tuningParamsAttributeList, 'invalidationSchedule', attributeList )

		self.configService.setAttributes( self.configService.session, tuningParamsConfigObject, tuningParamsAttributeList )
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	modifyTuningParams()
	#
	#	DESCRIPTION:
	#		Modify the tuningParams attributes.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifyTuningParams( 
							self, 
							sessionManagerConfigObject,
							sessionManagerAttributeList,
							allowOverflow=True,
							invalidationTimeout=30,
							maxInMemorySessionCount=1000,
							scheduleInvalidation=False,
							usingMultiRowSchema=False,
							writeContents='ONLY_UPDATED_ATTRIBUTES',
							writeFrequency='TIME_BASED_WRITE',
							writeInterval=10,
							firstHour=14,
							secondHour=2
							):
		"""Modify the tuningParams attributes.
		   PARAMETERS:
			   sessionManagerConfigObject   -- javax.management.ObjectName instance of the SessionManager.
			   sessionManagerAttributeList  -- javax.management.AttributeList instance of the SessionManager.
			   allowOverflow                -- Defaults to True.
			   invalidationTimeout          -- Defaults to 30.
			   maxInMemorySessionCount      -- Defaults to 1000.
			   scheduleInvalidation         -- Defaults to False.
			   usingMultiRowSchema          -- Defaults to False.
			   writeContents                -- Defaults to 'ONLY_UPDATED_ATTRIBUTES'.
			   writeFrequency               -- Defaults to 'TIME_BASED_WRITE'.
			   writeInterval                -- Defaults to 10.
			   firstHour                    -- Defaults to 14.
			   secondHour                   -- Defaults to 2.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifyTuningParams(): sessionManagerConfigObject=" + str( sessionManagerConfigObject ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): sessionManagerAttributeList=" + str( sessionManagerAttributeList ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): allowOverflow=" + str( allowOverflow ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): invalidationTimeout=" + str( invalidationTimeout ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): maxInMemorySessionCount=" + str( maxInMemorySessionCount ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): scheduleInvalidation=" + str( scheduleInvalidation ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): usingMultiRowSchema=" + str( usingMultiRowSchema ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): writeContents=" + str( writeContents ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): writeFrequency=" + str( writeFrequency ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): writeInterval=" + str( writeInterval ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): firstHour=" + str( firstHour ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): secondHour=" + str( secondHour ) + "\n" )

		####################################################################
		#	Do the tuningParamSettings.
		####################################################################
		myargs	= array( ['tuningParams'], java.lang.String )
		tuningParamSettings	= self.configService.getAttributes( self.configService.session, sessionManagerConfigObject, myargs, False )
		tuningParamObject = None
		for myAttr in tuningParamSettings:
			myName = myAttr.getName()
			myValue= myAttr.getValue()
			############################################################################
			#	If the name of the attribute is tuningParams, then capture
			#	the value because it is the ObjectName instance the we need.
			############################################################################
			if myName == 'tuningParams':
				tuningParamObject = myAttr.getValue()
			self.debug( __name__ + ".modifyTuningParams(): myAttr.getName()=" + str( myName ) + "\n" )
			self.debug( __name__ + ".modifyTuningParams(): myAttr.getValue()=" + str( myValue ) + "\n" )
		#Endfor
		if tuningParamObject is None:
			self.logIt( __name__ + ".modifyTuningParams(): Unable to obtain tuningParamObject" + "\n" )
			return False
		#Endif

		#####################################################################
		#	Now get the attributes list for the tuningParamObject.
		#####################################################################
		attributeList	= self.configService.getAttributes( self.configService.session, tuningParamObject, None, True )

		#####################################################################
		#	Set the attributes to the parameters that were passed in.
		#####################################################################
		self.debug( __name__ + ".modifyTuningParams(): BEFORE attributeList=" + str( attributeList ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): BEFORE attributeList type=" + str( type( attributeList ) ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): attributeList=" + str( attributeList ) + "\n" )
		self.debug( __name__ + ".modifyTuningParams(): attributeList type=" + str( type( attributeList ) ) + "\n" )
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'allowOverflow', java.lang.Boolean( allowOverflow ) )
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'invalidationTimeout', int( invalidationTimeout ) )
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'maxInMemorySessionCount', int( maxInMemorySessionCount ) )
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'scheduleInvalidation', java.lang.Boolean( scheduleInvalidation ) )
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'usingMultiRowSchema', java.lang.Boolean( usingMultiRowSchema ) )
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'writeContents', str( writeContents ) )
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'writeFrequency', str( writeFrequency ) )
		self.configService.configServiceHelper.setAttributeValue( attributeList, 'writeInterval', int( writeInterval ) )
		self.debug( __name__ + ".modifyTuningParams(): AFTER attributeList=" + str( attributeList ) + "\n" )

		####################################################################
		#	Save the attributeList to the current session.
		####################################################################
		self.configService.setAttributes( self.configService.session, tuningParamObject, attributeList )

		####################################################################
		#	Go back and get the tuningParamObject attributes from
		#	the session that we just saved them to.
		####################################################################
		attributeList = self.configService.getAttributes( self.configService.session, tuningParamObject, None, True )

		####################################################
		#	Do the invalidationSchedule.
		####################################################
		self.modifyInvalidationSchedule( 
							tuningParamObject,
							attributeList,
							firstHour=14,
							secondHour=2
							)

		###################################################
		#	Get the attributes again.
		###################################################
		attributeList = self.configService.getAttributes( self.configService.session, tuningParamObject, None, True )

		####################################################################
		#	Now add the tuningParams attributes to the
		#	SessionManager attributes.
		####################################################################
		self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'tuningParams', attributeList )

		self.configService.setAttributes( self.configService.session, sessionManagerConfigObject, sessionManagerAttributeList )
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	modifySessionDatabasePersistence()
	#
	#	DESCRIPTION:
	#		Modify the sessionDatabasePersistence attributes.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifySessionDatabasePersistence( 
							self, 
							sessionManagerConfigObject,
							sessionManagerAttributeList,
							datasourceJNDIName='jdbc/Sessions',
							db2RowSize='ROW_SIZE_4KB',
							userId='db2admin',
							password='db2admin',
							tableSpaceName=''
							):
		"""Modify the sessionDatabasePersistence attributes.
		   PARAMETERS:
			   sessionManagerConfigObject      -- javax.management.ObjectName instance of the SessionManager.
			   sessionManagerAttributeList     -- javax.management.AttributeList instance of the SessionManager.
			   datasourceJNDIName              -- datasource JNDIName.  Something like 'jdbc/Sessions' or None.
			   db2RowSize                      -- Something like 'ROW_SIZE_4KB', 'ROW_SIZE_32KB', 'ROW_SIZE_16KB', 'ROW_SIZE_8KB'.
			   userId                          -- user id.
			   password                        -- password.
			   tableSpaceName                  -- table space name to persist to.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifySessionDatabasePersistence(): sessionManagerConfigObject=" + str( sessionManagerConfigObject ) + "\n" )
		self.debug( __name__ + ".modifySessionDatabasePersistence(): sessionManagerAttributeList=" + str( sessionManagerAttributeList ) + "\n" )
		self.debug( __name__ + ".modifySessionDatabasePersistence(): datasourceJNDIName=" + str( datasourceJNDIName ) + "\n" )
		self.debug( __name__ + ".modifySessionDatabasePersistence(): db2RowSize=" + str( db2RowSize ) + "\n" )
		self.debug( __name__ + ".modifySessionDatabasePersistence(): userId=" + str( userId ) + "\n" )
		self.debug( __name__ + ".modifySessionDatabasePersistence(): password=" + str( password ) + "\n" )
		self.debug( __name__ + ".modifySessionDatabasePersistence(): tableSpaceName=" + str( tableSpaceName ) + "\n" )

		###########################################################################
		#	Get the attributes for the sessionDatabasePersistence.
		#	The AttributeList for sessionDatabasePersistence has a 
		#	javax.management.ObjectName that we need to get a hold of.
		###########################################################################
		myargs	= array( ['sessionDatabasePersistence'], java.lang.String )
		sessionDbAttrs	= self.configService.getAttributes( self.configService.session, sessionManagerConfigObject, myargs, False )
		sessionDbPersistenceObject = None
		for dbAttr in sessionDbAttrs:
			dbName = dbAttr.getName()
			dbValue= dbAttr.getValue()
			############################################################################
			#	If the name of the attribute is sessionDatabasePersistence, then capture
			#	the value because it is the ObjectName instance the we need.
			############################################################################
			if dbName == 'sessionDatabasePersistence':
				sessionDbPersistenceObject = dbAttr.getValue()
			self.debug( __name__ + ".modifySessionDatabasePersistence(): dbAttr.getName()=" + str( dbName ) + "\n" )
			self.debug( __name__ + ".modifySessionDatabasePersistence(): dbAttr.getValue()=" + str( dbValue ) + "\n" )
		#Endfor
		if sessionDbPersistenceObject is None:
			self.logIt( __name__ + ".modifySessionDatabasePersistence(): Unable to obtain sessionDbPersistenceObject" + "\n" )
			return False
		#Endif

		#####################################################################
		#	Now get the attributes list for the sessionDbPersistenceObject.
		#####################################################################
		dbAttrs = self.configService.getAttributes( self.configService.session, sessionDbPersistenceObject, None, False )

		#####################################################################
		#	Set the attributes to the parameters that were passed in.
		#####################################################################
		self.debug( __name__ + ".modifySessionDatabasePersistence(): BEFORE dbAttrs=" + str( dbAttrs ) + "\n" )
		self.debug( __name__ + ".modifySessionDatabasePersistence(): BEFORE dbAttrs type=" + str( type( dbAttrs ) ) + "\n" )
		self.debug( __name__ + ".modifySessionDatabasePersistence(): dbAttrs=" + str( dbAttrs ) + "\n" )
		self.debug( __name__ + ".modifySessionDatabasePersistence(): dbAttrs type=" + str( type( dbAttrs ) ) + "\n" )
		self.configService.configServiceHelper.setAttributeValue( dbAttrs, 'datasourceJNDIName', str( datasourceJNDIName ) )
		self.configService.configServiceHelper.setAttributeValue( dbAttrs, 'db2RowSize', str( db2RowSize ) )
		self.configService.configServiceHelper.setAttributeValue( dbAttrs, 'userId', str( userId ) )
		self.configService.configServiceHelper.setAttributeValue( dbAttrs, 'password', str( password ) )
		self.configService.configServiceHelper.setAttributeValue( dbAttrs, 'tableSpaceName', str( tableSpaceName ) )
		self.debug( __name__ + ".modifySessionDatabasePersistence(): AFTER dbAttrs=" + str( dbAttrs ) + "\n" )

		####################################################################
		#	Save the dbAttrs to the current session.
		####################################################################
		self.configService.setAttributes( self.configService.session, sessionDbPersistenceObject, dbAttrs )

		####################################################################
		#	Go back and get the sessionDbPersistenceObject attributes from
		#	the session that we just saved them to.
		####################################################################
		dbAttrs = self.configService.getAttributes( self.configService.session, sessionDbPersistenceObject, None, False )

		####################################################################
		#	Now add the sessionDatabasePersistence attributes to the
		#	SessionManager attributes.
		####################################################################
		self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'sessionDatabasePersistence', dbAttrs )
		
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	modifySessionManager()
	#
	#	DESCRIPTION:
	#		Modify the SessionManager attributes.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifySessionManager( 
							self, 
							enable=True,
							enableUrlRewriting=False,
							enableCookies=True,
							enableSSLTracking=False,
							enableProtocolSwitchRewriting=False,
							sessionPersistenceMode='NONE',
							enableSecurityIntegration=False,
							allowSerializedSessionAccess=False,
							maxWaitTime=5,
							accessSessionOnTimeout=True,
							datasourceJNDIName='jdbc/Sessions',
							db2RowSize='ROW_SIZE_4KB',
							userId='db2admin',
							password='db2admin',
							tableSpaceName='',
							name='JSESSIONID',
							domain='',
							maximumAge=-1,
							path='/',
							secure=False,
							allowOverflow=True,
							invalidationTimeout=30,
							maxInMemorySessionCount=1000,
							scheduleInvalidation=False,
							usingMultiRowSchema=False,
							writeContents='ONLY_UPDATED_ATTRIBUTES',
							writeFrequency='TIME_BASED_WRITE',
							writeInterval=10,
							firstHour=14,
							secondHour=2
							):
		"""Modify the SessionManager attributes.
		   PARAMETERS:
		       enable                          -- enable session management. True or False.
		       enableUrlRewriting              -- enable URL rewriting. True or False.
		       enableCookies                   -- enable cookies. True or False.
		       enableSSLTracking               -- enable SSL ID tracking. True or False.
		       enableProtocolSwitchRewriting   -- enable. True or False.
		       sessionPersistenceMode          -- defaults to 'NONE', 'DATABASE', or 'DATA_REPLICATION'.
		       enableSecurityIntegration       -- enable. True or False.
		       allowSerializedSessionAccess    -- enable. True or False.
		       maxWaitTime                     -- default is 5 seconds.
		       accessSessionOnTimeout          -- enable. True or False.
		       name                            -- DefaultCookie - Must be 'JSESSIONID'.
		       domain                          -- DefaultCookie - Default is ''.
		       maximumAge                      -- DefaultCookie - Default is -1.
		       path                            -- DefaultCookie - Default is '/'.
		       secure                          -- DefaultCookie - Default is False.
			   datasourceJNDIName              -- SessionDatabasePersistence - datasource JNDIName.  Something like 'jdbc/Sessions' or None.
			   db2RowSize                      -- SessionDatabasePersistence - Something like 'ROW_SIZE_4KB', 'ROW_SIZE_32KB', 'ROW_SIZE_16KB', 'ROW_SIZE_8KB'.
			   userId                          -- SessionDatabasePersistence - user id.
			   password                        -- SessionDatabasePersistence - password.
			   tableSpaceName                  -- SessionDatabasePersistence - table space name to persist to.
			   allowOverflow                   -- TuningParams - Default is True.
			   invalidationTimeout             -- TuningParams - Default is 30.
			   maxInMemorySessionCount         -- TuningParams - Default is 1000.
			   scheduleInvalidation            -- TuningParams - Default is False.
			   usingMultiRowSchema             -- TuningParams - Default is False.
			   writeContents                   -- TuningParams - Default is 'ONLY_UPDATED_ATTRIBUTES'.
			   writeFrequency                  -- TuningParams - Default is 'TIME_BASED_WRITE'.
			   writeInterval                   -- TuningParams - Default is 10.
			   firstHour                       -- InvalidationSchedule - Default is 14.
			   secondHour                      -- InvalidationSchedule - Default is 2.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifySessionManager(): enable=" + str( enable ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): enableUrlRewriting=" + str( enableUrlRewriting ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): enableCookies=" + str( enableCookies ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): enableSSLTracking=" + str( enableSSLTracking ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): enableProtocolSwitchRewriting=" + str( enableProtocolSwitchRewriting ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): sessionPersistenceMode=" + str( sessionPersistenceMode ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): enableSecurityIntegration=" + str( enableSecurityIntegration ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): allowSerializedSessionAccess=" + str( allowSerializedSessionAccess ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): maxWaitTime=" + str( maxWaitTime ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): accessSessionOnTimeout=" + str( accessSessionOnTimeout ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): name=" + str( name ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): domain=" + str( domain ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): maximumAge=" + str( maximumAge ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): path=" + str( path ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): secure=" + str( secure ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): datasourceJNDIName=" + str( datasourceJNDIName ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): db2RowSize=" + str( db2RowSize ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): userId=" + str( userId ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): password=" + str( password ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): tableSpaceName=" + str( tableSpaceName ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): allowOverflow=" + str( allowOverflow ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): invalidationTimeout=" + str( invalidationTimeout ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): maxInMemorySessionCount=" + str( maxInMemorySessionCount ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): scheduleInvalidation=" + str( scheduleInvalidation ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): usingMultiRowSchema=" + str( usingMultiRowSchema ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): writeContents=" + str( writeContents ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): writeFrequency=" + str( writeFrequency ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): writeInterval=" + str( writeInterval ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): firstHour=" + str( firstHour ) + "\n" )
		self.debug( __name__ + ".modifySessionManager(): secondHour=" + str( secondHour ) + "\n" )

		rVal = True
		if datasourceJNDIName is None or datasourceJNDIName == '':
			self.debug( __name__ + ".modifySessionManager(): datasourceJNDIName is invalid=" + str( datasourceJNDIName ) + "\n" )
			return False
		#Endif

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
			self.debug( __name__ + ".modifySessionManager(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".modifySessionManager(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the SessionManager AttributeList
			########################################################
			sessionManagerAttributeList	= self.configService.getAttributes( self.configService.session, configObject, None, True )

			self.debug( __name__ + ".modifySessionManager(): BEFORE sessionManagerAttributeList=" + str( sessionManagerAttributeList ) + "\n" )
			self.debug( __name__ + ".modifySessionManager(): BEFORE sessionManagerAttributeList type=" + str( type( sessionManagerAttributeList ) ) + "\n" )

			#######################################################
			#	Set the scalar SessionManager AttributeList values.
			#######################################################
			self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'enable', java.lang.Boolean( enable ) )
			self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'enableUrlRewriting', java.lang.Boolean( enableUrlRewriting ) )
			self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'enableCookies', java.lang.Boolean( enableCookies ) )
			self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'enableSSLTracking', java.lang.Boolean( enableSSLTracking ) )
			self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'enableProtocolSwitchRewriting', java.lang.Boolean( enableProtocolSwitchRewriting ) )
			self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'sessionPersistenceMode', str( sessionPersistenceMode ) )
			self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'enableSecurityIntegration', java.lang.Boolean( enableSecurityIntegration ) )
			self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'allowSerializedSessionAccess', java.lang.Boolean( allowSerializedSessionAccess ) )
			self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'maxWaitTime', int( maxWaitTime ) )
			self.configService.configServiceHelper.setAttributeValue( sessionManagerAttributeList, 'accessSessionOnTimeout', java.lang.Boolean( accessSessionOnTimeout ) )
			self.debug( __name__ + ".modifySessionManager(): AFTER sessionManagerAttributeList=" + str( sessionManagerAttributeList ) + "\n" )

			##################################################
			#	Do the SessionDatabasePersistence attributes.
			##################################################
			self.modifySessionDatabasePersistence( 
							configObject,
							sessionManagerAttributeList,
							datasourceJNDIName=datasourceJNDIName,
							db2RowSize=db2RowSize,
							userId=userId,
							password=password,
							tableSpaceName=tableSpaceName
							)

			##################################################
			#	Do the DefaultCookieSettings attributes.
			##################################################
			self.modifyDefaultCookieSettings( 
							configObject,
							sessionManagerAttributeList,
							name='JSESSIONID',
							domain='',
							maximumAge=-1,
							path='/',
							secure=False
							)

			##################################################
			#	Do the TuningParams attributes.
			##################################################
			self.modifyTuningParams( 
							configObject,
							sessionManagerAttributeList,
							allowOverflow=True,
							invalidationTimeout=30,
							maxInMemorySessionCount=1000,
							scheduleInvalidation=False,
							usingMultiRowSchema=False,
							writeContents='ONLY_UPDATED_ATTRIBUTES',
							writeFrequency='TIME_BASED_WRITE',
							writeInterval=10,
							firstHour=14,
							secondHour=2
							)
			####################################################################
			#	Save the sessionManagerAttributeList to the current session.
			####################################################################
			self.configService.setAttributes( self.configService.session, configObject, sessionManagerAttributeList )
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
	myLogger	= MyLogger( LOGFILE="/tmp/SessionManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/SessionManager.log", STDOUT=True, DEBUG=False )
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
	templateListManager	= TemplateListManager( configService, type="SessionManager", logger=myLogger )
	mySessionManager	= SessionManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in mySessionManager.attributesList:
		mySessionManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in mySessionManager.attributesList:
		mySessionManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in mySessionManager.attributesList:
			mySessionManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	mySessionManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/Sessions.tsv" )

	########################################################
	#	Create the data source.
	########################################################
	rc = mySessionManager.modifySessionManager(
							enable=True,
							enableUrlRewriting=True,
							enableCookies=True,
							enableSSLTracking=True,
							enableProtocolSwitchRewriting=True,
							sessionPersistenceMode='DATABASE',
							enableSecurityIntegration=True,
							allowSerializedSessionAccess=True,
							maxWaitTime=9,
							accessSessionOnTimeout=True,
							datasourceJNDIName='jdbc/Sessions',
							db2RowSize='ROW_SIZE_4KB',
							userId='db2admin',
							password='db2admin',
							tableSpaceName='DENIS_SPACE'
							)

	if rc: mySessionManager.saveSession( False )

	for mylist in mySessionManager.attributesList:
		mySessionManager.deepLogOfAttributes( mylist )
	#Endfor
	configService.closeMe()
	mySessionManager.closeMe()
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
