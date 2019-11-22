#!/usr/bin/env jython
######################################################################################
##	AppServerManager.py
##
##	Python module deals with WAS AppManagement.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	02/04/2010	Denis M. Putnam		Created.
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

class AppServerManager():
	"""AppServerManager class that contains Application Server methods to stop and start an app server."""

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
		self.configService		= configService
		#AttributeUtils.__init__( self, self.configService, scope, type='Server', logger=self.logger )
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
           listener - The object handle to the listener returned from addListener().
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
			if listener.received:
				self.debug( __name__ + ".waitForListener(): listener.status=" + str( listener.status ) + "\n" )
				self.debug( __name__ + ".waitForListener(): listener.message=" + str( listener.message ) + "\n" )
				if listener.status == AppNotification.STATUS_COMPLETED or listener.status == AppNotification.STATUS_FAILED:
					done = True
				#Endif
				if listener.status == AppNotification.SERVER_STOP_FAILED or listener.status == AppNotification.SERVER_START_FAILED:
					done = True
				#Endif
				if listener.status == AppNotification.NODESYNC_COMPLETE or listener.status == AppNotification.NODESYNC_FAILED:
					done = True
				#Endif
			#Endif
			maxtries -= 1
			self.debug( __name__ + ".waitForListener(): done=" + str( done ) + "\n" )
			self.debug( __name__ + ".waitForListener(): maxtries=" + str( maxtries ) + "\n" )
		#Endwhile
		rc = True
		self.debug( __name__ + ".waitForListener(): listener.status=" + str( listener.status ) + "\n" )
		if listener.status == AppNotification.STATUS_FAILED:		rc = False
		if listener.status == AppNotification.SERVER_STOP_FAILED:	rc = False
		if listener.status == AppNotification.SERVER_START_FAILED:	rc = False
		self.status = listener.status
		self.message= listener.message
		self.props	= listener.props
		if self.logger.DEBUG: self.logHashTable( self.props )
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
	def addListener(self,objectName,notify_type,handbackObj=None):
		"""Add a listener to this instance.
        PARMETERS:
           notify_type - AppNotification.<type>
		   handbackObj - an instance of the java.lang.Object, something like "Install: " + str( appName )
        RETURN:
           The object handle to the listener.
        """

		self.debug( __name__ + ".addListener(): objectName=" + str( objectName ) + "\n" )
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
		listener = self.adminClient.registerListener( objectName, filter=myFilter, handback=handbackObj, etype=notify_type )

		return listener
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
		self.debug( __name__ + ".checkIfAppServerExits(): nodeName=" + str( nodeName ) + "\n" )
		self.debug( __name__ + ".checkIfAppServerExits(): serverName=" + str( serverName ) + "\n" )
		####################################################################
		#AdminControl.queryNames( "WebSphere:*,type=Server,node=node_ServicesA_01,process=as_wdt_01" )
		####################################################################

		myWas = WasData( logger=self.logger )
		myWas.queryWAS( self.adminClient, query="WebSphere:*,type=Server,node=" + str( nodeName ) + ",process=" + str( serverName ) )
		for myObjectName in myWas.objectNames:
			self.debug( __name__ + ".checkIfAppServerExits(): myObjectName=" + str( myObjectName ) + "\n" )
			self.debug( __name__ + ".checkIfAppServerExits(): myObjectName type=" + str( type( myObjectName ) ) + "\n" )
			server = myObjectName.getKeyProperty( 'name' )
			if server == serverName: return True
		#Endfor
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	stopProcess()
	#
	#	DESCRIPTION:
	#		stop a generic server process by invoking user provided command.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def stopProcess(self,nodeName,serverName,timeout=60):
		"""Stop a generic server process by invoking user provided command.
           This method invokes the 'stopProcess' and waits 'timeout' seconds for dmgr
           to complete the requested stop.
           PARAMETERS:
              nodeName    -- node name.
              serverName  -- server name.
              timeout     -- time to wait in seconds.

           RETURN:
              True if the server exists.
		"""
		self.debug( __name__ + ".stopProcess(): nodeName=" + str( nodeName ) + "\n" )
		self.debug( __name__ + ".stopProcess(): serverName=" + str( serverName ) + "\n" )
		self.debug( __name__ + ".stopProcess(): timeout=" + str( timeout ) + "\n" )
		####################################################################
		#AdminControl.queryNames( "WebSphere:*,type=Server,node=node_ServicesA_01,process=nodeagent" )
		####################################################################

		myWas = WasData( logger=self.logger )
		myWas.queryWAS( self.adminClient, query="WebSphere:*,type=Server,node=" + str( nodeName ) + ",process=nodeagent" )
		for myNodeAgent in myWas.objectNames:
			self.debug( __name__ + ".stopProcess(): myNodeAgent=" + str( myNodeAgent ) + "\n" )
			self.debug( __name__ + ".stopProcess(): myNodeAgent type=" + str( type( myNodeAgent ) ) + "\n" )

			################################################################################
			#	Set up the listener.
			################################################################################
			notify_type = AppNotification.SERVER_STOPPED
			stopListener = self.addListener( myNodeAgent, notify_type, handbackObj='STOP: ' + str( serverName ) )

			####################################
			#	Invoke the request on the MBean.
			####################################
			self.adminClient.invoke( myNodeAgent, 'stopProcess', [serverName], ['java.lang.String'] )

			#################################################################################
			#	Wait for some timeout.  The installation application programming interface
			#	(API) is asynchronous and so it returns immediately.
			#	We need to wait for the listener to tell us of completness.
			#################################################################################
			rc = self.waitForListener( stopListener, timeout=timeout )
			return rc
		#Endfor
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	terminate()
	#
	#	DESCRIPTION:
	#		kill a server process without waiting for process shutdown.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def terminate(self,nodeName,serverName):
		"""kill a server process without waiting for process shutdown.
           PARAMETERS:
              nodeName    -- node name.
              serverName  -- server name.

           RETURN:
              True if the server exists.
		"""
		self.debug( __name__ + ".terminate(): nodeName=" + str( nodeName ) + "\n" )
		self.debug( __name__ + ".terminate(): serverName=" + str( serverName ) + "\n" )
		####################################################################
		#AdminControl.queryNames( "WebSphere:*,type=Server,node=node_ServicesA_01,process=nodeagent" )
		####################################################################

		myWas = WasData( logger=self.logger )
		myWas.queryWAS( self.adminClient, query="WebSphere:*,type=Server,node=" + str( nodeName ) + ",process=nodeagent" )
		for myNodeAgent in myWas.objectNames:
			self.debug( __name__ + ".terminate(): myNodeAgent=" + str( myNodeAgent ) + "\n" )
			self.debug( __name__ + ".terminate(): myNodeAgent type=" + str( type( myNodeAgent ) ) + "\n" )
			#self.adminClient.invoke( myNodeAgent, 'terminate', [serverName], ['java.lang.String'] )
			return True
		#Endfor
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	launchProcess()
	#
	#	DESCRIPTION:
	#		launch a new server process and specify the timeout interval to wait for server initialization to complete.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def launchProcess(self,nodeName,serverName,timeout=60):
		"""Launch a new server process and specify the timeout interval to wait for server initialization to complete.
           This method invokes the 'launchProcess' and waits 'timeout' seconds for dmgr
           to complete the request.
           PARAMETERS:
              nodeName    -- node name.
              serverName  -- server name.
              timeout     -- time to wait in seconds.

           RETURN:
              True if the server exists.
		"""
		self.debug( __name__ + ".launchProcess(): nodeName=" + str( nodeName ) + "\n" )
		self.debug( __name__ + ".launchProcess(): serverName=" + str( serverName ) + "\n" )
		self.debug( __name__ + ".launchProcess(): timeout=" + str( timeout ) + "\n" )
		####################################################################
		#AdminControl.queryNames( "WebSphere:*,type=Server,node=node_ServicesA_01,process=nodeagent" )
		####################################################################

		myWas = WasData( logger=self.logger )
		myWas.queryWAS( self.adminClient, query="WebSphere:*,type=Server,node=" + str( nodeName ) + ",process=nodeagent" )
		for myNodeAgent in myWas.objectNames:
			self.debug( __name__ + ".launchProcess(): myNodeAgent=" + str( myNodeAgent ) + "\n" )
			self.debug( __name__ + ".launchProcess(): myNodeAgent type=" + str( type( myNodeAgent ) ) + "\n" )

			################################################################################
			#	Set up the listener.
			################################################################################
			notify_type = AppNotification.SERVER_STARTED
			startListener = self.addListener( myNodeAgent, notify_type, handbackObj='LAUNCH: ' + str( serverName ) )

			####################################
			#	Invoke the request on the MBean.
			####################################
			self.adminClient.invoke( myNodeAgent, 'launchProcess', [serverName,timeout], ['java.lang.String','java.lang.Integer'] )

			#################################################################################
			#	Wait for some timeout.  The installation application programming interface
			#	(API) is asynchronous and so it returns immediately.
			#	We need to wait for the listener to tell us of completness.
			#################################################################################
			rc = self.waitForListener( startListener, timeout=timeout )
			return rc
		#Endfor
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	restart()
	#
	#	DESCRIPTION:
	#		recycle the node with file sync option
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def restart(self,nodeName,timeout=60,syncFirst=True,restartServers=True):
		"""Recycle the node with file sync option.
           This method invokes the 'restart' and waits 'timeout' seconds for dmgr
           to complete the request.
           PARAMETERS:
              nodeName    -- node name.
              timeout     -- time to wait in seconds.
              syncFirst   -- recycle the node with file sync option.
              restartServers   -- option to restart all running servers while restarting the node.

           RETURN:
              True if the server exists.
		"""
		self.debug( __name__ + ".restart(): nodeName=" + str( nodeName ) + "\n" )
		self.debug( __name__ + ".restart(): syncFirst=" + str( syncFirst ) + "\n" )
		self.debug( __name__ + ".restart(): restartServers=" + str( restartServers ) + "\n" )
		self.debug( __name__ + ".restart(): timeout=" + str( timeout ) + "\n" )
		####################################################################
		#AdminControl.queryNames( "WebSphere:*,type=Server,node=node_ServicesA_01,process=nodeagent" )
		####################################################################

		myWas = WasData( logger=self.logger )
		myWas.queryWAS( self.adminClient, query="WebSphere:*,type=Server,node=" + str( nodeName ) + ",process=nodeagent" )
		for myNodeAgent in myWas.objectNames:
			self.debug( __name__ + ".restart(): myNodeAgent=" + str( myNodeAgent ) + "\n" )
			self.debug( __name__ + ".restart(): myNodeAgent type=" + str( type( myNodeAgent ) ) + "\n" )

			################################################################################
			#	Set up the listener.
			################################################################################
			notify_type = AppNotification.NODESYNC_COMPLETE
			restartListener = self.addListener( myNodeAgent, notify_type, handbackObj='RESTART: ' + str( nodeName ) )

			####################################
			#	Invoke the request on the MBean.
			####################################
			self.adminClient.invoke( myNodeAgent, 'restart', [syncFirst,restartServers], ['java.lang.Boolean','java.lang.Boolean'] )

			#################################################################################
			#	Wait for some timeout.  The installation application programming interface
			#	(API) is asynchronous and so it returns immediately.
			#	We need to wait for the listener to tell us of completness.
			#################################################################################
			rc = self.waitForListener( restartListener, timeout=timeout )
			return rc
		#Endfor
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	stopNode()
	#
	#	DESCRIPTION:
	#		stop all application servers running at the node as well as the node agent process.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def stopNode(self,nodeName,timeout=60):
		"""Stop all application servers running at the node as well as the node agent process.
           This method invokes the 'stopNode' and waits 'timeout' seconds for dmgr
           to complete the request.
           PARAMETERS:
              nodeName    -- node name.
              timeout     -- time to wait in seconds.

           RETURN:
              True if the server exists.
		"""
		self.debug( __name__ + ".stopNode(): nodeName=" + str( nodeName ) + "\n" )
		self.debug( __name__ + ".stopNode(): timeout=" + str( timeout ) + "\n" )
		####################################################################
		#AdminControl.queryNames( "WebSphere:*,type=Server,node=node_ServicesA_01,process=nodeagent" )
		####################################################################

		myWas = WasData( logger=self.logger )
		myWas.queryWAS( self.adminClient, query="WebSphere:*,type=Server,node=" + str( nodeName ) + ",process=nodeagent" )
		for myNodeAgent in myWas.objectNames:
			self.debug( __name__ + ".stopNode(): myNodeAgent=" + str( myNodeAgent ) + "\n" )
			self.debug( __name__ + ".stopNode(): myNodeAgent type=" + str( type( myNodeAgent ) ) + "\n" )

			################################################################################
			#	Set up the listener.
			################################################################################
			notify_type = AppNotification.STATUS_COMPLETE
			stopNodeListener = self.addListener( myNodeAgent, notify_type, handbackObj='STOPNODE: ' + str( nodeName ) )

			####################################
			#	Invoke the request on the MBean.
			####################################
			self.adminClient.invoke( myNodeAgent, 'stopNode', None, None )

			#################################################################################
			#	Wait for some timeout.  The installation application programming interface
			#	(API) is asynchronous and so it returns immediately.
			#	We need to wait for the listener to tell us of completness.
			#################################################################################
			rc = self.waitForListener( stopNodeListener, timeout=timeout )
			return rc
		#Endfor
		return False
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
				if re.search( 'attributes', str( attr ) ):
					items = str( getattr( self, attr ) ).split( ',' )
					for item in items:
						self.debug( __name__ + ".logMySelf(): item=" + str( item ) + "\n" )
					#Endfor
					continue
				#Endif
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
	myLogger	= MyLogger( LOGFILE="/tmp/AppServerManager.log", STDOUT=True, DEBUG=True )
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

	mycell = "ServicesA"
	mynodeName = "node_ServicesA_01"
	myserver = "as_wdt_01"
	myappName = "DamnSchappettEA"
	mycluster = "cl_ServicesA_a"
	rc = False

	#scope = "Cell=" + str( mycell ) + ":Node=" + str( mynodeName ) + ":Cluster=" + str( mycluster ) + ":Server=" + str( myserver )
	#scope = "Cell=" + str( mycell ) + ":Node=" + str( mynodeName ) + ":Server=" + str( myserver )

	configService 		= ConfigService( adminClient=myclient, logger=myLogger )
	#myAppServerManager 	= AppServerManager(adminObject, scope, configService, logger=myLogger)
	myAppServerManager 	= AppServerManager(adminObject, configService, logger=myLogger)
	rc = myAppServerManager.checkIfAppServerExists(mynodeName,myserver)
	myLogger.logIt( "main(): rc=" + str(rc) + "\n" )
	#rc = myAppServerManager.stopProcess(mynodeName,myserver)
	#myLogger.logIt( "main(): rc=" + str(rc) + "\n" )
	
	myAppServerManager.closeMe()
	adminObject.closeMe()
	##################################################################################
	#Enddef
	##################################################################################

######################################################################################
#   End
######################################################################################
if __name__ == "__main__":
	main()

