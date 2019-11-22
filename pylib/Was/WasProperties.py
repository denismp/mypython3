#!/usr/bin/env jython
######################################################################################
##	WasProperties.py
##
##	Python module deals with WAS Properties.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	09/21/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.WasEnvironment import *

class WasProperties( WasEnvironment ):
	"""
    WasProperties class that deals with the WAS property files.
    """

	##################################################################################
	#	__init__()
	#
	#	DESCRIPTION:
	#		Class initializer.
	#
	#	PARAMETERS:
	#		logger	    - instance of the pylib.Utils.MyLogger class.
	#		domain	    - something like "V6_DEV|LAB|QUAL|PROD"
	#		properties_file - a websphere properities file.
	#
	#	RETURN:
	#		An instance of this class
	##################################################################################
	def __init__(
				self, 
				logger=None,
				domain=None,
				properties_file=None
		):
		"""Class Initializer.
           PARAMETERS:
               logger   - instance of the pylib.Utils.MyLogger class.
               domain   - something like "V6_DEV|LAB|QUAL|PROD"
			   properties_file - typically something like /dmp/WDT/bin/v6/ant/build_v6.properties

           RETURN:
               An instance of this class
		"""
		self.env = WasEnvironment.__init__( self, domain=domain, logger=logger )
		self.properties_file = properties_file
		if properties_file is None:
			self.properties_file = self.calculatePropertiesFile()

		try:
			self.snarfPropertiesFile()
		except IOError, e:
			raise IOError, "Unable to load " + str( self.properties_file ) 
			return
		#Endtry

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	calculatePropertiesFile()
	#
	#	DESCRIPTION:
	#		Calculate the location of the WAS properties file.
	#
	#	PARAMETERS:
	#		domain - something like V6_DEV
	#
	#	RETURN:
	#		the name of the properties file.
	##################################################################################
	def calculatePropertiesFile(self):
		"""Calculate the location of the WAS properties file.
           PARAMETERS:
               domain - something like V6_DEV

           RETURN:
               the name of the properties file.
		"""

		value = ""

		myEnv = self.getWasEnv()
		version = self.getDomainVersion()
		hostname = socket.gethostname()
		if re.search( 'deploy11', hostname ):
			value = "/nfs/dist/dmp/WDT/" + str( myEnv ) + "/bin/" + str( version ) + "/ant/build_" + str( version ) + ".properties"
		else:
			if myEnv == "PROD":
				value = "/dmp/WDT/bin/" + str( version ) + "/ant/build_" + str( version ) + ".properties"
			else:
				value = "/dmp/WDT/" + str( myEnv ) + "/bin/" + str( version ) + "/ant/build_" + str( version ) + ".properties"
			#Endif
		#Endif
		return value

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	snarfPropertiesFile()
	#
	#	DESCRIPTION:
	#		Load the properties_file data into this class instance and make the 
	#		values available via the dot notation.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def snarfPropertiesFile(self):
		"""Load the contents of the properties file and add the attribute value pairs
           to this class instance.
        PARMETERS:
        """

		try:
			FH = open( self.properties_file, "r" )
			line = ""
			for line in FH:
				line = re.sub( '\n$', '', line )
				if line == '': continue
				if re.match( '^#', line ): continue
				#self.logIt( "pylib.Was.WasProperties.snarfPropertiesFile(): line=>'" + str( line ) + "'\n" )
				ar = re.split( '=', line )
				name = ar[0]
				name = re.sub( '\.', '_', name )
				value = ar[1]
				setattr( self, name, value )
			#Endfor
			FH.close()
		except IOError, e:
			self.logIt( "pylib.Was.WasProperties.snarfPropertiesFile(): Unable to read the " + str( self.properties_file ) + ": " + str( e ) + "\n" )
			raise
			return
		#Endtry

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
				self.debug( "pylib.Was.WasProperties.logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
			else:
				self.logIt( "pylib.Was.WasProperties.logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
			#Endif
		#Endfor
		#self.logEnv( debugOnly=debugOnly )

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
		WasEnvironment.closeMe(self)
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
def main():
	myLogger = MyLogger( LOGFILE="/tmp/WasProperties.log", STDOUT=True, DEBUG=False )
	#myObject = WasProperties(domain="V6_DEV", logger=myLogger, properties_file='/nfs/dist/dmp/WDT/PROD/bin/v6/ant/build_v6.properties')
	myObject = WasProperties(domain="V6_DEV", logger=myLogger )
	myObject.logMySelf( debugOnly=False )

	myObject.closeMe();
	##################################################################################
	#Enddef
	##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
	main()

