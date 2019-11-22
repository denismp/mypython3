#!/usr/bin/env jython
######################################################################################
##	AppManagementService.py
##
##	Python module deals with WAS AppManagementService.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	10/29/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.WasProperties import *
from pylib.Was.AdminClient import *
import java.lang.NullPointerException as NullPointerException
import java.lang.NoClassDefFoundError as NoClassDefFoundError

from com.ibm.websphere.management.application import AppManagementProxy
from com.ibm.websphere.management.application import EarUtils
from com.ibm.websphere.management.application import AppConstants
from com.ibm.websphere.management.sync import SyncResult

class AppManagementService():
	"""AppManagementService class that contains the WAS AppManagementProxy class."""

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
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               logger      - instance of the pylib.Utils.MyLogger class.

           RETURN:
               An instance of this class
		"""
		#if logger is None: raise Exception, "Please specify the logger instance."
		self.logger				= logger
		self.appManagementProxy = AppManagementProxy
		self.earUtils			= EarUtils()
		self.appConstants		= AppConstants
		self.syncResult			= SyncResult
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

		once = False
		myAttrs = dir( self )
		for attr in myAttrs:
			try:
				#if re.search( '__doc__',  attr ): continue
				##if re.search( '__module__',  attr ): continue
				#if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
				##if re.search( 'instance', str( getattr( self, attr ) ) ): continue
				#if re.search( 'supportedConfigObjectTypes',  attr ): continue
				#self.debug( __name__ + ".logMySelf(): attr=" + str( attr ) + "\n" )
				if( debugOnly == True ):
					self.debug( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				else:
					self.logIt( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				#Endif
			except Exception, e:
				if once and re.search( 'Default constructor failed for Java superclass',  str(e) ):
					self.debug( __name__ + ".logMySelf(): " + str( e ) + "\n" )
					once = True
				else:
					continue
				self.debug( __name__ + ".logMySelf(): " + str( e ) + "\n" )
				continue
			#Endtry
		#Endfor
		#self.env.logMySelf( debugOnly=debugOnly )

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getJMXProxyForClient()
	#
	#	DESCRIPTION:
	#		Get the JMX Proxy for the given admin client.
	#
	#	PARAMETERS:
	#		see below
	#
	#	RETURN:
	##################################################################################
	def getJMXProxyForClient(self, adminClient):
		"""Get the JMX Proxy for the given admin client and store it in self.appManagementClientProxy.
		   PARAMETERS:
		       adminClient - an instance of com.ibm.websphere.management.AdminClient 
		   RETURN:
		       com.ibm.websphere.management.application.AppManagementProxy instance.
		"""

		self.appManagementClientProxy = AppManagementProxy.getJMXProxyForClient( adminClient )
		return self.appManagementClientProxy
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getJMXProxyForServer()
	#
	#	DESCRIPTION:
	#		Get the JMX Proxy for the server.
	#
	#	PARAMETERS:
	#		see below
	#
	#	RETURN:
	##################################################################################
	def getJMXProxyForServer(self):
		"""Get the JMX Proxy for the server and store it in self.appManagementServerProxy.
		   PARAMETERS:
		   RETURN:
		       com.ibm.websphere.management.application.AppManagementProxy instance.
		"""

		self.appManagementServerProxy = AppManagementProxy.getJMXProxyForServer()
		return self.appManagementServerProxy
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getLocalProxy()
	#
	#	DESCRIPTION:
	#		Get the local Proxy for the server.
	#
	#	PARAMETERS:
	#		see below
	#
	#	RETURN:
	##################################################################################
	def getLocalProxy(self):
		"""Get the JMX Proxy for the given admin client and store it in self.appManagementProxy.
		   PARAMETERS:
		   RETURN:
		       com.ibm.websphere.management.application.AppManagementProxy instance.
		"""

		self.appManagementLocalProxy = AppManagementProxy.getLocalProxy()
		return self.appManagementLocalProxy
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
	##################################################################################
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

######################################################################################
#Endclass
######################################################################################

#########################################################################
#	For testing.
#########################################################################
def main():
	myLogger	= MyLogger( LOGFILE="/tmp/AppManagementService.log", STDOUT=True, DEBUG=True )
	#adminClient = AdminClient( logger=myLogger, hostname="dilabvirt31-v1" )
	adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1", cellName='cellA' )
	try:
		myconn					= adminClient.createRMIDefault()
		print dir( myconn )
		myObject				= AppManagementService( logger=myLogger )
		myAppManagementClient	= myObject.getJMXProxyForClient( myconn )
		#myAppManagementServer	= myObject.getJMXProxyForServer()
		myAppManagementLocal	= myObject.getLocalProxy()
		print dir( myAppManagementClient )
		#print dir( myAppManagementServer )
		print dir( myAppManagementLocal )
		print dir( myObject )
		print dir( myObject.appConstants )
		myObject.closeMe()
		adminClient.closeMe()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
	#EndExcept
	##################################################################################
	#Enddef
	##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
	main()

