#!/usr/bin/env jython
######################################################################################
##	AppManager.py
##
##	Python module deals with WAS AppManagement.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	11/30/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
import time
import random
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.AdminClient import *
from pylib.Was.WasData import *
from pylib.Was.WasObject import *
from pylib.Was.AdminClient import *
from pylib.Was.ConfigService import *
from pylib.Was.AttributeUtils import *
from java.lang import NullPointerException
from java.lang import NoClassDefFoundError
from java.util import Locale
from java.util import Hashtable
from java.util import Properties
from java.util import Enumeration
from java.lang import String
from java.lang import Boolean
from javax.management import InstanceNotFoundException
from javax.management import MalformedObjectNameException
from javax.management import ObjectName
from com.ibm.websphere.management.application import AppManagement
from com.ibm.websphere.management.application import AppConstants
from com.ibm.websphere.management.application import AppManagementProxy
from com.ibm.websphere.management import Session
from javax.management import NotificationFilterSupport
from com.ibm.websphere.management.exception import AdminException
from com.ibm.websphere.management.configservice import ConfigServiceHelper
from com.ibm.websphere.management.application.client import AppDeploymentController
from com.ibm.websphere.management.application.client import AppDeploymentTask
from com.ibm.websphere.management.application import AppNotification

import com.ibm.websphere.security.WebSphereRuntimePermission as WebSphereRuntimePermission
import com.ibm.websphere.security.auth.WSLoginFailedException as WSLoginFailedException
import com.ibm.ws.security.util.InvalidPasswordDecodingException as InvalidPasswordDecodingException
import com.ibm.websphere.management.exception.ConnectorException as ConnectorException

class AppManager( AttributeUtils ):
	"""AppManager class that contains AppManagement methods."""

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
				scope,
				configService,
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               adminClient - instance of the pylib.Was.AdminClient class.
			   configService - ConfigService instance.
               logger      - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		self.adminClient		= adminClient
		self.logger				= logger
		self.proxy				= AppManagementProxy.getJMXProxyForClient( adminClient.connection )
		self.configService		= configService
		#self.logger.debug( __name__ + ".__init__(): configService type=" + str( type( self.configService ) ) + "\n" )
		#self.logger.debug( __name__ + ".__init__(): scope=" + str( scope  ) + "\n" )
		AttributeUtils.__init__( self, self.configService, scope, type='Server', logger=self.logger ) # This guy sets up the session.
		self.status				= None
		self.message			= None
		self.props				= None
		self.appName			= None
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
	#	checkIfAppServerExists()
	#
	#	DESCRIPTION:
	#		Checks if the app server exists in the dmgr.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def checkIfAppServerExists(self,nodeName,serverName):
		"""Checks if the app server exists in the dmgr.
           PARAMETERS:
              nodeName    -- node name.
              serverName  -- server name.

           RETURN:
              True if the server exists.
		"""
		myWas = WasData( logger=self.logger )
		myWas.queryWAS( self.adminClient, query="WebSphere:*,Node=" + str( nodeName ) + ",server=" + str( serverName ) )
		for server in myWas.objectNames:
			if server == serverName: return True
		#Endfor
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	checkIfAppExists()
	#
	#	DESCRIPTION:
	#		Checks if an application with the given name exists in the dmgr.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def checkIfAppExists(self,appName,prefs=None):
		"""Checks if an application with the given name exists in the dmgr.
           PARAMETERS:
              appName    -- java.lang.String containing the app name.
              prefs      -- java.util.Hashtable containing the preferences.

           RETURN:
              True if the app exists.
		"""
		rc = None
		if prefs is None:
			prefs = Hashtable()
			prefs.put( AppConstants.APPDEPL_LOCALE, Locale.getDefault() )
		#Endif
		if self.configService is not None:
			rc = self.proxy.checkIfAppExists( appName, prefs, self.configService.session.toString() )
		else:
			rc = self.proxy.checkIfAppExists( appName, prefs, None )
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	stopApplication()
	#
	#	DESCRIPTION:
	#		Stop an application.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def stopApplication(self,appName):
		"""Stop an application.
           PARAMETERS:
              appName      -- java.lang.String containing the app name.

           RETURN:
              True if successful or False
		"""
		rc = True
		prefs = Hashtable()
		prefs.put( AppConstants.APPDEPL_LOCALE, Locale.getDefault() )

		###############################################
		#	If the application exists, then stop it.
		###############################################
		if self.checkIfAppExists(appName,prefs):

			#################################################################################
			#	Stop the application.
			#################################################################################
			if self.configService is not None:
				self.status = self.proxy.stopApplication( appName, prefs, self.configService.session.toString() )
			else:
				self.status = self.proxy.stopApplication( appName, prefs, None )

			if self.status == AppNotification.STATUS_FAILED: 
				rc = False
				self.message = "Unable to stop " + str( appName )
			else:
				self.message = str( appName ) + " is stopped."
			#Endif
		else:
			self.status = AppNotification.STATUS_FAILED
			self.message = str( appName ) + " does not exist."
		#Endif
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	startApplication()
	#
	#	DESCRIPTION:
	#		Start an application.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def startApplication(self,appName):
		"""Start an application.
           PARAMETERS:
              appName      -- java.lang.String containing the app name.

           RETURN:
              True if successful or False
		"""
		rc = True
		prefs = Hashtable()
		prefs.put( AppConstants.APPDEPL_LOCALE, Locale.getDefault() )

		###############################################
		#	If the application exists, then stop it.
		###############################################
		if self.checkIfAppExists( appName, prefs ):

			#################################################################################
			#	Start the application.
			#################################################################################
			if self.configService is not None:
				self.status = self.proxy.startApplication( appName, prefs, self.configService.session.toString() )
			else:
				self.status = self.proxy.startApplication( appName, prefs, None )

			if self.status == AppNotification.STATUS_FAILED: 
				rc = False
				self.message = "Unable to start " + str( appName )
			else:
				self.message = str( appName ) + " is started."
			#Endif
		else:
			rc = False
		#Endif
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	writeTaskData()
	#
	#	DESCRIPTION:
	#		Write the task data.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def writeTaskData(self,data,filename):
		"""Log task data.  Not used.
           PARAMETERS:
              data -- java.lang.String[][]

           RETURN:
		"""
		#print type( data )
		if data is not None:
			FH = open( filename, "a+" )
			for i in range( len( data ) ):
				ostr = ""
				for j in range( len( data[i] ) ):
					ostr += str( data[i][j] ) + ","
				#Endfor
				ostr += "\n"
				FH.write( ostr )
			#Endfor
			FH.close()
		#Endif
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	modifyTaskData()
	#
	#	DESCRIPTION:
	#		Modify the task data for AppController
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def modifyTaskData(self,data,cell=None, node=None, server=None, cluster=None):
		"""Modify the task data for the ApplicationController.  
           Not used because it breaks the install.
           PARAMETERS:
              data      -- java.lang.String[][]
              cell      -- cell name.
              node      -- node name
              server    -- server name
              cluster   -- cluster name

           RETURN:
              data      -- java.lang.String[][]
		"""
		if data is not None:
			for i in range( len( data ) ):
				for j in range( len( data[i] ) ):
					#mydata = str( data[i][j] )
					if re.search( r'WebSphere:cell=', str( data[i][j] ) ):
						data[i][j] = String( "WebSphere:cell=" + str( cell ) )
						self.debug( __name__ + ".modifyTaskData(): WebSphere:cell data=" + str( data[i][j] ) + "\n" )
						continue
					if re.search( r'node=', str( data[i][j] ) ):
						data[i][j] = String( "cluster=" + str( cluster ) )
						self.debug( __name__ + ".modifyTaskData(): node data=" + str( data[i][j] ) + "\n" )
						continue
					if re.search( r'server=', str( data[i][j] ) ):
						data[i][j] = String( "server=" + str( server ) )
						self.debug( __name__ + ".modifyTaskData(): server data=" + str( data[i][j] ) + "\n" )
				#Endfor
			#Endfor
		#Endif
		return data
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	preparationPhase()
	#
	#	DESCRIPTION:
	#		Prepare the application for installation or redeployment.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def preparationPhase(self,earFile,appName, cell=None, node=None, server=None, cluster=None, default_host="default_host"):
		"""Install an application.  The caller may look at the AppManagement.status and
           the AppManagement.message to determine issues.
           PARAMETERS:
              earFile      -- java.lang.String containing the ear file name.
              appName      -- java.lang.String containing the app name.
              default_host -- java.lang.String containing the default host name.

           RETURN:
              options - Hashtable to be used by the proxy.installApplication() or
			            the proxy.redeployApplication().
		"""
		self.debug( __name__ + ".preparationPhase(): earFile=" + str( earFile ) + "\n" )
		self.debug( __name__ + ".preparationPhase(): appName=" + str( appName ) + "\n" )
		self.debug( __name__ + ".preparationPhase(): default_host=" + str( default_host ) + "\n" )
		self.appName = appName

		#################################################################################
		#	Preparation phase: Begin
		#	Through the preparation phase you populate the enterprise archive (EAR) file
		#	with WebSphere Application Server-specific binding information.  For example,
		#	you can specify Java Naming and Directory Interface (JNDI) names for the
		#	enterprise beans, or virtual hosts for Web modules, and so on.
		#################################################################################

		#################################################################################
		#	First, crate the control and populate the EAR file with the appropriate
		#	options.
		#################################################################################
		prefs = Hashtable()
		prefs.put( AppConstants.APPDEPL_LOCALE, Locale.getDefault() )

		#################################################################################
		#	You can optionally run the default binding generator by using the following
		#	options.  Refer to Java documentation for the AppDeploymentController class
		#	to see all the options that you can set.
		#################################################################################
		defaultBnd = Properties()
		prefs.put( AppConstants.APPDEPL_DFLTBNDG, defaultBnd )
		defaultBnd.put( AppConstants.APPDEPL_DFLTBNDG_FORCE, AppConstants.YES_KEY )

		if default_host is not None:
			#defaultBnd = Properties()
			#prefs.put( AppConstants.APPDEPL_DFLTBNDG, defaultBnd )
			defaultBnd.put( AppConstants.APPDEPL_DFLTBNDG_VHOST, default_host )
		#Endif

		#################################################################################
		#	Create the controller.
		#################################################################################
		controller = AppDeploymentController.readArchive( earFile, prefs )

		if True:
			###############################################
			#	This logic may be completely unneccessary
			#	but it is done for completness from the 
			#	example java code.
			###############################################
			#myrand = random.randint( 1, 100 )

			task = controller.getFirstTask()
			while task is not None:
				###############################
				#	Populate the task data.
				###############################
				data = task.getTaskData()

				##########################################################
				#file = "/nfs/home4/dmpapp/appd4ec/tmp/denis_" + str( myrand ) + ".csv"
				#self.writeTaskData( data, file )
				##########################################################
				#	Manipulate task data which is a table of stringtask
				#	Not used.
				##########################################################
				#data = self.modifyTaskData( data, cell, server, node, cluster ) 
				#file = "/nfs/home4/dmpapp/appd4ec/tmp/denis_2_" + str( myrand ) + ".csv"
				#self.writeTaskData( data, file )
				##########################################################

				task.setTaskData( data )
				task = controller.getNextTask()
			#Endwhile
		#Endif
		controller.saveAndClose()

		options = controller.getAppDeploymentSavedResults()

		#################################################################################
		#options = controller.getAppOptions()
		#options.put( AppConstants.APPDEPL_VALIDATE_INSTALL, AppConstants.APPDEPL_VALIDATE_INSTALL_WARN )
		#options.put( AppConstants.APPDEPL_DEPLOYWS_CMDARG, True )
		#options.put( AppConstants.APPDEPL_DEPLOYWS_JARDIRS_OPTION, True )
		#options.put( AppConstants.APPDEPL_DETAILED_APP_STATUS, True )
		#options.put( AppConstants.APPDEPL_DEPLOYEJB_CMDARG, True )
		#options.put( AppConstants.APPDEPL_ARCHIVE_UPLOAD, True )
		#options.put( AppConstants.APPDEPL_ASYNC_REQUEST_DISPATCH, AppConstants.APPDEPL_ASYNC_REQUEST_DISPATCH_CLIENT )
		#options.put( AppConstants.APPDEPL_DEPLOYEJB_CMDARG, True )
		#options.put( AppConstants.APPDEPL_INSTALL_DIR, "/apps/WebSphere7/profiles/cell101Dmgr/config/cells/cell101/applications/EFIServicesEA.ear" )
		#options.put( AppConstants.APPDEPL_INSTALL_DIR_FINAL, "/apps/WebSphere7/profiles/cell101Dmgr/config/cells/cell101/applications/EFIServicesEA.ear" )
		#options.put( AppConstants.APPDEPL_DETAILED_APP_STATUS, AppConstants.APPDEPL_DETAILED_APP_STATUS_FAILURE )
		#options.put( AppConstants.APPDEPL_DETAILED_APP_STATUS, True )
		#################################################################################

		#################################################################################
		#	The previous options table contains the module-to-server relationship if it
		#	was set by using tasks.
		#	Preparation phase: End
		#################################################################################

		return options
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	logHashTable()
	#
	#	DESCRIPTION:
	#		Log the given hashtable.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def logHashTable(self,hashtable):
		"""Log the given hashtable.
           PARAMETERS:
              hashtable   -- java.util.Hashtable containing the hashtable.

           RETURN:
		"""
		e = hashtable.keys()
		els = list( e )
		els.sort()
		for k in els:
			self.logIt( __name__ + ".logHashTable(): " + str( k ) + "=" + str( hashtable.get( k ) ) + "\n" )
		#Endfor
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	fixActivationPlan()
	#
	#	DESCRIPTION:
	#		Fix the activation plan
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def fixActivationPlan(self,hashtable):
		"""Fix the activation plan.  Not used because it breaks things.
           PARAMETERS:
              hashtable   -- java.util.Hashtable containing the hashtable.

           RETURN:
		   hashtable
		"""
		k = AppConstants.APPDEPL_MODULE_TO_SERVER
		k2 = AppConstants.APPDEPL_ACTIVATION_PLAN_ADD
		k3 = AppConstants.APPDEPL_ACTIVATION_PLAN_REMOVE
		#newplan = Hashtable()

		module2ServerHash = hashtable.get( k )
		activationplanHash = hashtable.get( k2 )
		activationplanRemoveHash = hashtable.get( k3 )
		mkeys = module2ServerHash.keys()
		smkeys = list( mkeys )
		smkeys.sort()
		for sk in smkeys:
			v = module2ServerHash.get( sk )
			activationplanHash.put( sk, [String(v)] ) 	
			activationplanRemoveHash.put( sk, [String(v)] ) 	
		#Endfor
		hashtable.put( k2, activationplanHash )
		hashtable.put( k3, activationplanRemoveHash )
		return hashtable
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	modifyModule2ServerHash()
	#
	#	DESCRIPTION:
	#		Modify the module to server hash.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def modifyModule2ServerHash(self,hashtable,cell,cluster,node=None,server=None):
		"""Modify the module to server hash.
           PARAMETERS:
              hashtable   -- java.util.Hashtable containing the hashtable.
              cell        -- cell name to deploy to.
              cluster     -- cluster name to deploy to.
              node        -- Not used.
              server      -- Not used.

           RETURN:
              The modified hashtable
		"""
		target = String( "WebSphere:cell=" + str( cell ) + ",cluster=" + str( cluster ) )
		###################################################################################
		#target = String( "WebSphere:cell=" + str( cell ) + ",node=" + str( node ) )
		#target = String( "WebSphere:cell=" + str( cell ) + ",server=" + str( server ) + ",cluster=" + str( cluster ) )
		#target = String( "WebSphere:cell=" + str( cell ) + ",node=" + str( node ) + ",server=" + str( server ) + ",cluster=" + str( cluster ) )
		#target = String( "WebSphere:cell=" + str( cell ) + ",server=" + str( server ) + ",cluster=" + str( cluster ) )
		#target = String( "WebSphere:cluster=" + str( cluster ) )
		#target = String( "WebSphere:cell=" + str( cell ) + ",node=" + str( node ) + ",server=" + str( server ) )
		#hashtable.put( "*", target )
		#return hashtable
		###################################################################################

		###################################################################################
		#	Search through the module2server has for the META-INF and WEB-INF keys
		#	and replace the values(targets) of the keys with the target string from
		#	above.  The install will fail if the target values are not right.
		###################################################################################
		e = hashtable.keys()
		els = list( e )
		els.sort()
		for k in els:
			self.logIt( __name__ + ".modifyModule2ServerHash(): key=" + str( k ) + "\n" )
			v = hashtable.get( k )
			self.logIt( __name__ + ".modifyModule2ServerHash(): value=" + str( v ) + "\n" )
			self.logIt( __name__ + ".modifyModule2ServerHash():  re.search( r'META-INF', k )=" + str(  re.search( r'META-INF', k ) ) + "\n" )
			if re.search( r'META-INF', k ):
				self.logIt( __name__ + ".modifyModule2ServerHash(): " + str( k ) + "=" + str( v ) + "\n" )
				hashtable.put( k, String( target ) )
				self.logIt( __name__ + ".modifyModule2ServerHash(): Changed to=>" + str( k ) + "=" + str( target ) + "\n" )
			self.logIt( __name__ + ".modifyModule2ServerHash():  re.search( r'WEB-INF', k )=" + str(  re.search( r'WEB-INF', k ) ) + "\n" )
			if re.search( r'WEB-INF', k ):
				self.logIt( __name__ + ".modifyModule2ServerHash(): " + str( k ) + "=" + str( v ) + "\n" )
				hashtable.put( k, String( target ) )
				self.logIt( __name__ + ".modifyModule2ServerHash(): Changed to=>" + str( k ) + "=" + str( target ) + "\n" )
			#Endif
		#Endfor
		#hashtable.put( AppConstants.APPDEPL_CELL, String( cell ) )
		if self.logger.DEBUG: self.logHashTable( hashtable )
		
		return hashtable
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setModule2ServerRelationship()
	#
	#	DESCRIPTION:
	#		Set the module to server relationship.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def setModule2ServerRelationship(self,earFile,appName,options,cell=None,nodeName=None,server=None,cluster=None):
		"""Set the module to server relationship.  The caller may look at the AppManagement.status and
           the AppManagement.message to determine issues.
           PARAMETERS:
              earFile      -- java.lang.String containing the ear file name.
              appName      -- java.lang.String containing the app name.
              options      -- java.util.Hashtable containing the options establish in preparationPhase().
              cell         -- java.lang.String containing the cell name.
              nodeName     -- java.lang.String containing the node name.
              server       -- java.lang.String containing the server name.
              cluster      -- java.lang.String containing the cluster name.

           RETURN:
              True if successful or False
		"""
		self.debug( __name__ + ".setModule2ServerRelationship(): earFile=" + str( earFile ) + "\n" )
		self.debug( __name__ + ".setModule2ServerRelationship(): appName=" + str( appName ) + "\n" )
		self.debug( __name__ + ".setModule2ServerRelationship(): options=" + str( dir( options ) ) + "\n" )
		self.debug( __name__ + ".setModule2ServerRelationship(): cell=" + str( cell ) + "\n" )
		self.debug( __name__ + ".setModule2ServerRelationship(): nodeName=" + str( nodeName ) + "\n" )
		self.debug( __name__ + ".setModule2ServerRelationship(): server=" + str( server ) + "\n" )
		self.debug( __name__ + ".setModule2ServerRelationship(): cluster=" + str( cluster ) + "\n" )
		self.logHashTable( options )

		mymodule2server = options.get( AppConstants.APPDEPL_MODULE_TO_SERVER )
		self.debug( __name__ + ".setModule2ServerRelationship(): mymodule2server=" + str( mymodule2server ) + "\n" )
		self.debug( __name__ + ".setModule2ServerRelationship(): mymodule2server type=" + str( type( mymodule2server ) ) + "\n" )
		if self.logger.DEBUG: self.logHashTable( mymodule2server )

		#################################################################################
		#	If code for the preparation phase has been run, then you already have the
		#	options table.
		#	If not, create a new table and add the module-to-server relationship to it
		#	by creating a new Hashtable if the options is None.
		#################################################################################
		if options is None: 
			options = Hashtable()
			options.put( AppConstants.APPDEPL_LOCALE, Locale.getDefault() )

		#################################################################################
		#	Add the module to the server relationship.
		#################################################################################
		if cell is not None and nodeName is not None and server is not None and cluster is not None:
			module2Server = options.get( AppConstants.APPDEPL_MODULE_TO_SERVER )
			module2server = self.modifyModule2ServerHash(module2Server,cell,cluster,node=nodeName,server=server)
			options.put( AppConstants.APPDEPL_MODULE_TO_SERVER, module2server )
			#options = self.fixActivationPlan(options)
		#Endif
		if self.logger.DEBUG: self.logHashTable( options )
		return options
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	installApplication()
	#
	#	DESCRIPTION:
	#		Install an application.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def installApplication(self,earFile,appName,default_host="default_host",cell=None,nodeName=None,server=None,cluster=None,timeout=60):
		"""Install an application.  The caller may look at the AppManagement.status and
           the AppManagement.message to determine issues.
           PARAMETERS:
              earFile      -- java.lang.String containing the ear file name.
              appName      -- java.lang.String containing the app name.
              default_host -- java.lang.String containing the default host name.
              cell         -- java.lang.String containing the cell name.
              nodeName     -- java.lang.String containing the node name.
              server       -- java.lang.String containing the server name.
              cluster      -- java.lang.String containing the cluster name.
              timeout      -- maximum time to wait for the install to complete in seconds.

           RETURN:
              True if successful or False
		"""
		self.debug( __name__ + ".installApplication(): earFile=" + str( earFile ) + "\n" )
		self.debug( __name__ + ".installApplication(): appName=" + str( appName ) + "\n" )
		self.debug( __name__ + ".installApplication(): default_host=" + str( default_host ) + "\n" )
		self.debug( __name__ + ".installApplication(): cell=" + str( cell ) + "\n" )
		self.debug( __name__ + ".installApplication(): nodeName=" + str( nodeName ) + "\n" )
		self.debug( __name__ + ".installApplication(): server=" + str( server ) + "\n" )
		self.debug( __name__ + ".installApplication(): cluster=" + str( cluster ) + "\n" )
		self.debug( __name__ + ".installApplication(): timeout=" + str( timeout ) + "\n" )

		#################################################################################
		#	Preparation phase: Begin
		#	Through the preparation phase you populate the enterprise archive (EAR) file
		#	with WebSphere Application Server-specific binding information.  For example,
		#	you can specify Java Naming and Directory Interface (JNDI) names for the
		#	enterprise beans, or virtual hosts for Web modules, and so on.
		#################################################################################

		options = self.preparationPhase( earFile, appName, cell=cell, node=nodeName, server=server, cluster=cluster, default_host=default_host )

		#################################################################################
		#	Create the application management proxy, AppManagement.
		#	This was done in the constructor of this class.
		#################################################################################
		##proxy = AppManagementProxy.getJMXProxyForClient( adminClient.connection )
		#################################################################################

		#################################################################################
		#	Add the module to the server relationship.
		#################################################################################
		#globalSettings = self.proxy.getGlobalSettings();
		#self.logHashTable( globalSettings )
		options = self.setModule2ServerRelationship(earFile,appName,options,cell=cell,nodeName=nodeName,server=server,cluster=cluster)

		#################################################################################
		#	Create and add the notification listener for listening to installation events.
		#################################################################################
		listener = self.addListener( AppNotification.INSTALL, handbackObj="Install: " + str( appName ) )

		#################################################################################
		#	Install the application.
		#################################################################################
		if self.configService is not None:
			self.proxy.installApplication( earFile, appName, options, self.configService.session.toString() )
		else:
			self.proxy.installApplication( earFile, appName, options, None )

		#################################################################################
		#	Wait for some timeout.  The installation application programming interface
		#	(API) is asynchronous and so it returns immediately.
		#	We need to wait for the listener to tell us of completness.
		#################################################################################
		rc = self.waitForListener(listener,timeout=timeout)

		################################################
		#	Remove the notification listener.
		################################################
		listener.closeMe()

		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	redeployApplication()
	#
	#	DESCRIPTION:
	#		Redeploy an application.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def redeployApplication(self,earFile,appName,default_host="default_host",cell=None,nodeName=None,server=None,cluster=None,timeout=60):
		"""Redeploy an application.  The caller may look at the AppManagement.status and
           the AppManagement.message to determine issues.
           PARAMETERS:
              earFile      -- java.lang.String containing the ear file name.
              appName      -- java.lang.String containing the app name.
              default_host -- java.lang.String containing the default host name.
              cell         -- java.lang.String containing the cell name.
              nodeName     -- java.lang.String containing the node name.
              server       -- java.lang.String containing the server name.
              cluster      -- java.lang.String containing the cluster name.
              timeout      -- maximum time to wait for the install to complete in seconds.

           RETURN:
              True if successful or False
		"""
		self.debug( __name__ + ".redeployApplication(): earFile=" + str( earFile ) + "\n" )
		self.debug( __name__ + ".redeployApplication(): appName=" + str( appName ) + "\n" )
		self.debug( __name__ + ".redeployApplication(): default_host=" + str( default_host ) + "\n" )
		self.debug( __name__ + ".redeployApplication(): cell=" + str( cell ) + "\n" )
		self.debug( __name__ + ".redeployApplication(): nodeName=" + str( nodeName ) + "\n" )
		self.debug( __name__ + ".redeployApplication(): server=" + str( server ) + "\n" )
		self.debug( __name__ + ".redeployApplication(): cluster=" + str( cluster ) + "\n" )
		self.debug( __name__ + ".redeployApplication(): timeout=" + str( timeout ) + "\n" )

		#################################################################################
		#	Preparation phase: Begin
		#	Through the preparation phase you populate the enterprise archive (EAR) file
		#	with WebSphere Application Server-specific binding information.  For example,
		#	you can specify Java Naming and Directory Interface (JNDI) names for the
		#	enterprise beans, or virtual hosts for Web modules, and so on.
		#################################################################################

		options = self.preparationPhase( earFile, appName, cell=cell, node=nodeName, server=server, cluster=cluster, default_host=default_host )

		#################################################################################
		#	Create the application management proxy, AppManagement.
		#	This was done in the constructor of this class.
		#################################################################################
		##proxy = AppManagementProxy.getJMXProxyForClient( adminClient.connection )
		#################################################################################

		#################################################################################
		#	Add the module to the server relationship.
		#################################################################################
		options = self.setModule2ServerRelationship(earFile,appName,options,cell=cell,nodeName=nodeName,server=server,cluster=cluster)

		#################################################################################
		#	Create and add the notification listener for listening to installation events.
		#################################################################################
		listener = self.addListener( AppNotification.INSTALL, handbackObj="Redeploy: " + str( appName ) )

		#################################################################################
		#	Redeploy the application.
		#################################################################################
		if self.configService is not None:
			self.proxy.redeployApplication( earFile, appName, options, self.configService.session.toString() )
		else:
			self.proxy.redeployApplication( earFile, appName, options, None )

		#################################################################################
		#	Wait for some timeout.  The installation application programming interface
		#	(API) is asynchronous and so it returns immediately.
		#	We need to wait for the listener to tell us of completness.
		#################################################################################
		rc = self.waitForListener(listener,timeout=timeout)

		################################################
		#	Remove the notification listener.
		################################################
		listener.closeMe()

		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	uninstallApplication()
	#
	#	DESCRIPTION:
	#		Uninstall an application.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def uninstallApplication(self,appName,timeout=60):
		"""Uninstall an application.  The caller may look at the AppManagement.status and
           the AppManagement.message to determine issues.
           PARAMETERS:
              appName      -- java.lang.String containing the app name.
              timeout      -- maximum time to wait for the install to complete in seconds.

           RETURN:
              True if successful or False
		"""
		self.debug( __name__ + ".uninstallApplication(): appName=" + str( appName ) + "\n" )
		self.debug( __name__ + ".uninstallApplication(): timeout=" + str( timeout ) + "\n" )

		options = Hashtable()
		options.put( AppConstants.APPDEPL_LOCALE, Locale.getDefault() )

		#################################################################################
		#	Create and add the notification listener for listening to installation events.
		#################################################################################
		listener = self.addListener( AppNotification.UNINSTALL, handbackObj="Uninstall: " + str( appName ) )

		#################################################################################
		#	UnInstall the application.
		#################################################################################
		if self.configService is not None:
			self.proxy.uninstallApplication( appName, options, self.configService.session.toString() )
		else:
			self.proxy.uninstallApplication( appName, options, None )

		#################################################################################
		#	Wait for some timeout.  The installation application programming interface
		#	(API) is asynchronous and so it returns immediately.
		#	We need to wait for the listener to tell us of completness.
		#################################################################################
		rc = self.waitForListener(listener,timeout=timeout)

		################################################
		#	Remove the notification listener.
		################################################
		listener.closeMe()

		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	addListener()
	#
	#	DESCRIPTION:
	#		Add a listener.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def addListener(self,notify_type,handbackObj=None):
		"""Add a listener to this object.
        PARMETERS:
           notify_type - AppNotification.<type>
		   handbackObj - an instance of the java.lang.Object, something like "Install: " + str( appName )
        RETURN:
           The object handle to the listener.
        """

		self.debug( __name__ + ".addListener(): notify_type=" + str( notify_type ) + "\n" )
		self.debug( __name__ + ".addListener(): handbackObj=" + str( handbackObj ) + "\n" )

		#################################################################################
		#	Create the notification listener for listening to installation events.
		#################################################################################
		myFilter = NotificationFilterSupport()
		myFilter.enableType( AppConstants.NotificationType )

		#################################################################################
		#	Add the listener.
		#################################################################################
		iter = self.adminClient.connection.queryNames( ObjectName( "WebSphere:type=AppManagement,*" ), None ).iterator()
		on = iter.next()
		listener = self.adminClient.registerListener( on, filter=myFilter, handback=handbackObj, etype=notify_type )

		return listener
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	sync()
	#
	#	DESCRIPTION:
	#		Perform a synchronize "multiSync" on all the nodes in the cell.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def sync(self):
		"""Perform a "multiSync" on all teh nodes in the cell.
        PARMETERS:
        RETURN:
           True if completed or False
        """
		self.debug( __name__ + ".sync(): Called.\n" )
		rc = False
		iter = self.adminClient.connection.queryNames( ObjectName( "WebSphere:*,type=DeploymentManager" ), None ).iterator()
		while iter.hasNext():
			on = iter.next()
			self.logIt( __name__ + ".sync(): " + on.toString() + "\n" )
			self.adminClient.invoke( on, "multiSync", [Boolean( Boolean.TRUE )], ["java.lang.Boolean"] )
			self.logIt( __name__ + ".sync(): Successfully synced all nodes.\n" )
			rc = True
		#Endwhile
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	waitForListener()
	#
	#	DESCRIPTION:
	#		Wait for the listener
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def waitForListener(self,listener,timeout=60):
		"""Wait for the listener
        PARMETERS:
           timeout - number of seconds to wait.
        RETURN:
           True if completed or False
        """

		self.debug( __name__ + ".waitForListener(): listener=" + str( listener ) + "\n" )
		self.debug( __name__ + ".waitForListener(): timeout=" + str( timeout ) + "\n" )

		done = False
		self.message = "Listener timed out."
		maxtries = timeout / 6
		while not done and maxtries > 0:
			time.sleep( 6 )
			#done = listener.received
			if listener.received:
				if listener.status == AppNotification.STATUS_COMPLETED or listener.status == AppNotification.STATUS_FAILED:
					done = True
				#Endif
			#Endif
			maxtries -= 1
			self.debug( __name__ + ".waitForListener(): done=" + str( done ) + "\n" )
			self.debug( __name__ + ".waitForListener(): maxtries=" + str( maxtries ) + "\n" )
		#Endwhile
		rc = True
		self.debug( __name__ + ".waitForListener(): listener.status=" + str( listener.status ) + "\n" )
		if listener.status == AppNotification.STATUS_FAILED: rc = False
		self.status = listener.status
		self.message= listener.message
		self.props	= listener.props
		if self.logger.DEBUG: self.logHashTable( self.props )
		return rc
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
	#	checkResults()
	#
	#	DESCRIPTION:
	#		Check the results of the listener.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def checkResults(self):
		"""Check the results of the listener."""
		rc = True
		self.debug( __name__ + ".checkResults(): called.\n" )

		###############################################
		#prefs = Hashtable()
		#prefs.put( AppConstants.APPDEPL_LOCALE, Locale.getDefault() )
		#appDeploymentTaskArray = self.proxy.getApplicationInfo( self.appName, prefs, self.configService.session.toString() )
		###############################################

		#########################################
		#	Check to see if we got a status.
		#########################################
		if self.status is not None:
			################################
			#	Status processing.
			################################
			if self.status != AppNotification.STATUS_FAILED:
				###############################################
				#	Process a failed status.
				###############################################
				self.logIt( __name__ + ".checkResults(): status=" + str( self.status ) + "\n" )
				self.logIt( __name__ + ".checkResults(): message=" + str( self.message ) + "\n" )

				###############################################
				#	Report if the app exists.
				###############################################
				if self.appName is not None and self.checkIfAppExists( self.appName, prefs=None ):
					self.logIt( __name__ + ".checkResults(): appName=" + str( self.appName ) + " exists.\n" )
					#if self.configService is not None:
					#	self.configService.save( self.configService.session, False )
					#	self.logIt( __name__ + ".checkResults(): saving the session." + str( self.configService.session ) + "\n" )
				else:
					self.logIt( __name__ + ".checkResults(): appName=" + str( self.appName ) + " does not exist.\n" )
					#if self.configService is not None:
					#	self.logIt( __name__ + ".checkResults(): discarding the session." + str( self.configService.session ) + "\n" )
					#	self.configService.discard( self.configService.session )
					rc = False
			else:
				##############################################
				#	Process a success status.
				##############################################
				if self.logger.DEBUG: self.logHashTable( self.props )
				self.logIt( __name__ + ".checkResults(): status=" + str( self.status ) + "\n" )
				self.logIt( __name__ + ".checkResults(): message=" + str( self.message ) + "\n" )
				#if self.configService is not None:
				#	self.logIt( __name__ + ".checkResults(): discarding the session." + str( self.configService.session ) + "\n" )
				#	self.configService.discard( self.configService.session )
				rc = False
			#Endif
		else:
			####################################
			#	No status processing.
			####################################
			#if self.configService is not None:
			#	self.logIt( __name__ + ".checkResults(): discarding the session." + str( self.configService.session ) + "\n" )
			#	self.configService.discard( self.configService.session )
			rc = False
		#Endif
		return rc
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
		#Endif
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	__del__()
	#
	#	DESCRIPTION:
	#		Really closes this instance.
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

######################################################################################
#Endclass
######################################################################################

#########################################################################
#	For testing.
#########################################################################
def main():
	myLogger	= MyLogger( LOGFILE="/tmp/AppManager.log", STDOUT=True, DEBUG=True )
	#adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1" )
	adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1", cellName='cellA' )
	try:
		myclient	= adminObject.createSOAPDefault()
		results		= adminObject.getResults()
		#adminObject.logResults( results )
	except Exception, e:
		myLogger.logIt( "main(): " + str(e) + "\n" )
		myLogger.logIt( "main(): Unable to connect to the AdminClient().  Make sure that the WebSphere Server Manager is running.\n" )
		raise
	#Endtry

	###################################################################################################
	#
	#configService.createConfigData(session, node, "Server", "Server", attrList);
	#javax.management.ObjectName createConfigData(Session session,
    #                                         javax.management.ObjectName parent,
    #                                         java.lang.String attributeName,
    #                                         java.lang.String type,
    #                                         javax.management.AttributeList attrList)
    #                                         throws ConfigServiceException,
    #                                                ConnectorException
	#
    #create a Config Data. If the attribute is a collection type attribute, this method will 
	#create the object and add the newly created object at the end of list.
	#
    #Parameters:
    #    session - the seesion id.
    #    parent - the id of the parent config data.
    #    attributeName - the name of the relationship or attribute between the parent and child config data.
    #    type - the type of created config data. The type can be the type of the attribute specified in the attribute meta 
	#	 info, it can also be one of the subtypes listed in the attribute _ATTRIBUTE_METAINFO_SUBTYPES in the meta info of the attribute.
    #    attrList - the AttributeList of created config object. 
    #Returns:
    #    the config data id of created config object or config data. 
    #Throws:
    #    ConfigServiceException 
    #    ConnectorException
	###################################################################################################
	
	earFile = "/nfs/home4/dmpapp/appd4ec/tmp/DamnSchappettEA.ear"
	mycell = "ServicesA"
	mynodeName = "node_ServicesA_01"
	myserver = "as_ServicesA_a01"
	myappName = "DamnSchappettEA"
	mycluster = "cl_ServicesA_a"
	rc = False
	redeploy = False

	#scope = "Cell=" + str( mycell ) + ":Node=" + str( mynodeName ) + ":Cluster=" + str( mycluster ) + ":Server=" + str( myserver )
	scope = "Cell=" + str( mycell ) + ":Node=" + str( mynodeName ) + ":Server=" + str( myserver )
	attributeName = 'Server'
	attributeType = 'Server'
	attributeList = AttributeList()

	configService 	= ConfigService( adminClient=myclient, logger=myLogger )
	myAppManager 	= AppManager(adminObject, scope, configService, logger=myLogger)

	################################################
	#	Uninstall app if it exists.
	################################################
	if myAppManager.checkIfAppExists( myappName ):
		myLogger.logIt( "main(): UNINSTALLING " + str( myappName) + ".\n" )
		rc = myAppManager.uninstallApplication(myappName,timeout=480)
		myLogger.logIt( "main(): Completed UNINSTALL of " + str( myappName) + ".\n" )
	print "rc=" + str( rc )

	rc = myAppManager.checkResults()
	
	if rc:
		rc = myAppManager.sync()

	################################################
	#	install app if it does not exist.
	################################################
	if myAppManager.checkIfAppExists( myappName ):
		myLogger.logIt( "main(): REDEPLOYING " + str( myappName) + ".\n" )
		rc = myAppManager.redeployApplication(earFile,myappName,default_host="default_host",cell=mycell,nodeName=mynodeName,server=myserver,cluster=mycluster,timeout=480)
		myLogger.logIt( "main(): Completed REDEPLOY of " + str( myappName) + ".\n" )
		redeploy = True
	else:
		myLogger.logIt( "main(): INSTALLING " + str( myappName) + ".\n" )
		rc = myAppManager.installApplication(earFile,myappName,default_host="default_host",cell=mycell,nodeName=mynodeName,server=myserver,cluster=mycluster,timeout=480)
		myLogger.logIt( "main(): Completed INSTALL of " + str( myappName) + ".\n" )
	print "rc=" + str( rc )

	rc = myAppManager.checkResults()
	
	if rc:
		rc = myAppManager.sync()
	if rc and not redeploy:
		myAppManager.startApplication( myappName )

	################################################
	#	Redeploy app if it exists.
	################################################
	if myAppManager.checkIfAppExists( myappName ):
		myLogger.logIt( "main(): REDEPLOYING " + str( myappName) + ".\n" )
		rc = myAppManager.redeployApplication(earFile,myappName,default_host="default_host",cell=mycell,nodeName=mynodeName,server=myserver,cluster=mycluster,timeout=480)
		myLogger.logIt( "main(): Completed REDEPLOY of " + str( myappName) + ".\n" )
		redeploy = True
	else:
		myLogger.logIt( "main(): INSTALLING " + str( myappName) + ".\n" )
		rc = myAppManager.installApplication(earFile,myappName,default_host="default_host",cell=mycell,nodeName=mynodeName,server=myserver,cluster=mycluster,timeout=480)
		myLogger.logIt( "main(): Completed INSTALL of " + str( myappName) + ".\n" )
	print "rc=" + str( rc )

	rc = myAppManager.checkResults()
	
	if rc: configService.save( configService.session, False )

	if rc:
		rc = myAppManager.sync()
	if rc and not redeploy:
		myAppManager.startApplication( myappName )
	
	myAppManager.closeMe()
	adminObject.closeMe()
	##################################################################################
	#Enddef
	##################################################################################

######################################################################################
#   End
######################################################################################
if __name__ == "__main__":
	main()

