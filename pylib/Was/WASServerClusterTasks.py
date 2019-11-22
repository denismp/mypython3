#!/usr/bin/env jython
######################################################################################
##	WASServerClusterTasks.py
##
##	Python module deals with WAS Session.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	11/02/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from java.lang import String
import java.lang.NullPointerException as NullPointerException
import java.lang.NoClassDefFoundError as NoClassDefFoundError

from com.ibm.websphere.management.configservice import ConfigServiceProxy
from com.ibm.websphere.management import Session
from com.ibm.websphere.management.exception import ConfigServiceException
from com.ibm.websphere.management.exception import ConnectorException

from com.ibm.websphere.management.configservice.tasks import ServerClusterTasks
from com.ibm.websphere.management.configservice import ConfigService

from com.dmp.was.admin.service import WASAdminClient

class WASServerClusterTasks( ServerClusterTasks ):
	"""WASServerClusterTasks class that extends the WAS com.ibm.websphere.management.configservice.tasks.ServerClusterTasks class."""

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
				configService=None,
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
			   configService - instance of the com.ibm.websphere.management.configservice.ConfigServiceProxy class.
               logger        - instance of the pylib.Utils.MyLogger class.

           RETURN:
               An instance of this class
		"""
		self.logger	= logger
		if configService == None: 
			self.logIt( __name__ + ".__init__(): Please specify the configService parameter.\n" )
			raise Exception, "Please specify the configService parameter."
		#Endif
		ServerClusterTasks.__init__( self, configService )

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
				#if re.search( '__doc__',  attr ): continue
				##if re.search( '__module__',  attr ): continue
				#if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
				##if re.search( 'instance', str( getattr( self, attr ) ) ): continue
				if( debugOnly == True ):
					self.debug( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				else:
					self.logIt( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				#Endif
			except:
				continue
			#Endtry
		#Endfor
		#self.env.logMySelf( debugOnly=debugOnly )

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
	myLogger	= MyLogger( LOGFILE="/tmp/WASServerClusterTasks.log", STDOUT=True, DEBUG=True )
	#wasAdminClient			= WASAdminClient( "dilabvirt31-v1", None, None, None )
	wasAdminClient	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1", cellName='cellA' )
	myclient				= wasAdminClient.createRMIDefault()
	configServiceProxy		= ConfigServiceProxy( myclient )
	myObject	= WASServerClusterTasks( configService=configServiceProxy, logger=myLogger )
	print dir( myObject )
	myObject.closeMe()
	##################################################################################
	#Enddef
	##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
	main()

