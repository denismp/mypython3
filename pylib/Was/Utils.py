#!/usr/bin/env jython
######################################################################################
##	Utils.py
##
##	Python module deals with WAS Utils.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	09/17/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.WasEnvironment import *

class Utils():
	"""Utils class that contains with the WAS utilities."""

	##################################################################################
	#	__init__()
	#
	#	DESCRIPTION:
	#		Class initializer.
	#
	#	PARAMETERS:
	#		domain	    - something like "V6_DEV|LAB|QUAL|PROD"
	#		env		    - an instance of the pylib.Was.WasEnvironment class.
	#
	#	RETURN:
	#		An instance of this class
	##################################################################################
	def __init__(
				self, 
				logger=None,
				env=None,
				processCallBack=None
		):
		"""Class Initializer.
           PARAMETERS:
               logger   - instance of the MyLogger class.
               env      - instance of the pylib.Was.WasEnvironment class.
               processCallBack - function callback reference.

           RETURN:
               An instance of this class
		"""
		self.env			= env
		self.logger			= logger
		self.processCallBack		= processCallBack
		self.utils			= MyUtils()
		self.hostname		= socket.gethostname()
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
			if re.search( '__doc__',  attr ): continue
			if re.search( '__module__',  attr ): continue
			if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
			if re.search( 'instance', str( getattr( self, attr ) ) ): continue
			if( debugOnly == True ):
				self.debug( "pylib.Was.Utils.logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
			else:
				self.logIt( "pylib.Was.Utils.logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
			#Endif
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
	#	processRequest()
	#
	#	DESCRIPTION:
	#		Closes this instance.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def processRequest(self):
		"""Call the callback."""
		if self.processCallBack is not None:
			self.processCallBack()
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
		self.debug( "pylib.Was.Utils.closeMe(): called.\n" )
		pass
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
		#self.logIt( "pylib.Was.Utils.__del__(): called.\n" )
		self.closeMe()
	##################################################################################
	#Enddef
	##################################################################################

#####################################################################################
#Endclass
#####################################################################################

#########################################################################
#	For testing.
#########################################################################
def foo():
	print "Hello world."

def main():
	myLogger	= MyLogger( LOGFILE="/tmp/Utils.log", STDOUT=True, DEBUG=False )
	myEnv		= WasEnvironment( domain="V6_DEV", logger=myLogger )
	myObject	= Utils( env=myEnv, logger=myLogger, processCallBack=foo)
	myEnv.logMySelf( debugOnly=False )
	myObject.logMySelf( debugOnly=False )
	myObject.processRequest()

	myObject.closeMe();
	##################################################################################
	#Enddef
	##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
	main()

