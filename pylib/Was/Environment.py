#!/usr/bin/env jython
######################################################################################
##	Environment.py
##
##	Python module deals with WAS Environment.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	09/16/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *

class Environment():
	"""
    Environment class that deals with the WAS environment.
	When this class is instantiated, it sucks in the entire user environment.
    This makes all the environment variable available via the python dot
    notation.  Setting new environment variables also makes them available.
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
	#		env		    - something like "prod", "qual", or "dev"
	#
	#	RETURN:
	#		An instance of this class
	##################################################################################
	def __init__(
				self, 
				logger=None,
				domain=None 
		):
		"""Class Initializer.
           PARAMETERS:
               logger   - instance of the pylib.Utils.MyLogger class.
               domain   - something like "V6_DEV|LAB|QUAL|PROD"

           RETURN:
               An instance of this class
		"""
		self.domain			= domain
		self.logger			= logger
		self.utils			= MyUtils()
		self.getAllTheEnvironment()
		self.getEnvVars()
		self.domain_version	= self.calcDomainVersion()
		self.domain_env		= self.calcDomainEnv()
		self.home			= self.calcHome()
		#self.logMySelf()
		self.validate()

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getEnvVars()
	#
	#	DESCRIPTION:
	#		Get the environment variable that can be used.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getEnvVars(self):
		"""Get the environment variables that my be useful.
           Some of the variables may be legacy and no longer used.
           Typically the user should not call this function.
           PARAMETERS:

           RETURN:
		"""
		self.getWasEnv()

		self.setWasEnv( self.WDT_ENVIRONMENT )

		self.getUseDAO()

		self.setUseDB( value=self.USE_DAO )

		self.setUseDAO( value=self.USE_DAO )

		self.getGenXML()

		self.setGenXML( value=self.GEN_XML )

		self.setGenerateXML( value=self.GEN_XML )

		self.getWasRunningApplicationUpdate()

		self.setWasRunningApplicationUpdate( value=self.WAS_RUNNING_APPLICATION_UPDATE )

		self.setUpdateProcessRunning( value=self.WAS_RUNNING_APPLICATION_UPDATE )

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
		rVal = True
		domain_env = self.domain_env.lower()
		if domain_env != self.getWasEnv().lower():
			self.logIt( "pylib.Was.Environment.validate(): WARNING!  The domain=" + str( domain_env ) + " and the environment=" + str( self.getWasEnv() ) + " are not consistent.\n" )
			self.logMySelf()
			rVal = False
		#Endif
		return rVal

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getUseDAO()
	#
	#	DESCRIPTION:
	#		Get the use_dao value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		use_dao
	##################################################################################
	def getUseDAO(self):
		"""Get the use_dao value.
           PARAMETERS:

           RETURN:
               use_dao
		"""
		use_dao		= self.getEnvironmentVariable( name='USE_DAO', default='NULL' )
		return use_dao

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setUseDAO()
	#
	#	DESCRIPTION:
	#		Set the use_dao value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setUseDAO(self, value='NULL'):
		"""Set the use_dao value.
           PARAMETERS:
               value is either 'true', 'false', or 'NULL'

           RETURN:
		"""
		self.setEnvironmentVariable( name='USE_DAO', value=value.upper() )
		#self.use_dao		= value

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getGenXML()
	#
	#	DESCRIPTION:
	#		Get the gen_xml value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		gen_xml
	##################################################################################
	def getGenXML(self):
		"""Get the ugen_xml value.
           PARAMETERS:

           RETURN:
               gen_xml
		"""
		gen_xml		= self.getEnvironmentVariable( name='GEN_XML', default='NULL' )
		return gen_xml

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setGenXML()
	#
	#	DESCRIPTION:
	#		Set the gen_xml value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setGenXML(self, value='NULL'):
		"""Set the gen_xml value.
           PARAMETERS:
               value is either 'true', 'false', or 'NULL'

           RETURN:
		"""
		self.setEnvironmentVariable( name='GEN_XML', value=value.upper() )

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getGenerateXML()
	#
	#	DESCRIPTION:
	#		Get the generate_xml value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		generate_xml
	##################################################################################
	def getGenerateXML(self):
		"""Get the generate_xml value.
           PARAMETERS:

           RETURN:
               generate_xml
		"""
		generate_xml		= self.getEnvironmentVariable( name='GENERATE_XML', default='NULL' )
		return generate_xml

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setGenerateXML()
	#
	#	DESCRIPTION:
	#		Set the generate_xml value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setGenerateXML(self, value='FALSE'):
		"""Get the generate_xml value.
           PARAMETERS:
              value of either 'TRUE' or 'FALSE'

           RETURN:
		"""
		self.setEnvironmentVariable( name='GENERATE_XML', value=value.upper() )
		#self.generate_xml = value

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getUseDB()
	#
	#	DESCRIPTION:
	#		Get the use_db value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		use_db
	##################################################################################
	def getUseDB(self):
		"""Get the use_db value.
           PARAMETERS:

           RETURN:
              use_db
		"""
		use_db		= self.getEnvironmentVariable( name='USE_DB', default='NULL' )
		return use_db

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setUseDB()
	#
	#	DESCRIPTION:
	#		Set the use_db value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setUseDB(self, value='FALSE'):
		"""Get the use_db value.
           PARAMETERS:
              value of either 'TRUE' or 'FALSE'

           RETURN:
		"""
		self.setEnvironmentVariable( name='USE_DB', value=value.upper() )
		#self.use_db = value

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setWasRunningApplicationUpdate()
	#
	#	DESCRIPTION:
	#		Set the was_running_application_update value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setWasRunningApplicationUpdate(self, value=''):
		"""Get the was_running_application_update value.
           PARAMETERS:
              value of either 'TRUE' or 'FALSE'

           RETURN:
		"""
		self.setEnvironmentVariable( name='WAS_RUNNING_APPLICATION_UPDATE', value=value.upper() )
		#self.was_running_application_update = value

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getWasRunningApplicationUpdate()
	#
	#	DESCRIPTION:
	#		Get the was_running_application_update value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		was_running_application_update
	##################################################################################
	def getWasRunningApplicationUpdate(self):
		"""Get the was_running_application_update value.
           PARAMETERS:
              value of either 'TRUE' or 'FALSE'

           RETURN:
		"""
		was_running_application_update		= self.getEnvironmentVariable( name='WAS_RUNNING_APPLICATION_UPDATE', default='' )
		return was_running_application_update

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setUpdateProcessRunning()
	#
	#	DESCRIPTION:
	#		Set the update_process_running value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setUpdateProcessRunning(self, value='false'):
		"""Get the use_db value.
           PARAMETERS:
              value of either 'TRUE' or 'FALSE'

           RETURN:
		"""
		self.setEnvironmentVariable( name='UPDATE_PROCESS_RUNNING', value=value.upper() )
		#self.update_process_running = value

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getWasEnv()
	#
	#	DESCRIPTION:
	#		Get the WAS environment.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		env
	##################################################################################
	def getWasEnv(self):
		"""Get the WAS environment.
           PARAMETERS:

           RETURN:
               env
		"""
		env		= self.getEnvironmentVariable( name='WDT_ENVIRONMENT', default='PROD' )
		return env

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getEnvironmentVariable()
	#
	#	DESCRIPTION:
	#		Get an environment variable
	#
	#	PARAMETERS:
	#       name is the name of the environment variable.
   	#       default is the default value of the environment variable if it is not set.
	#
	#	RETURN:
	#		value
	##################################################################################
	def getEnvironmentVariable(self, name=None, default=''):
		"""Get the WAS environment.
           PARAMETERS:
               name is the name of the environment variable.
               default is the default value of the environment variable if it is not set.

           RETURN:
               value
		"""
		if name is None: return None

		value = default
		try:
			value = os.environ[name]
		except KeyError, e:
			self.logIt( "pylib.Was.Environment.getEnvironmentVariable(): Unable to get " + str( e ) + ".  Using " + str( default ) + ".\n" )
			value = default
		#Endtry
		setattr(self, name, value )
		return value

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setEnvironmentVariable()
	#
	#	DESCRIPTION:
	#		Set an environment variable
	#
	#	PARAMETERS:
	#       name is the name of the environment variable.
   	#       value is the value of the environment variable.
	#
	#	RETURN:
	##################################################################################
	def setEnvironmentVariable(self, name=None, value=None ):
		"""Get the WAS environment.
           PARAMETERS:
               name is the name of the environment variable.
               value is the value of the environment variable.
               default is the default value of the environment variable if value is None.

           RETURN:
		"""
		if name is None: return
		if value is None:
			self.logIt( "pylib.Was.Environment.setEnvironmentVariable(): value=" + str( value ) + ".  Environment variable " + str( name ) + " is not set.\n" )
			return
		#Endif

		try:
			os.environ[name] = value
			setattr(self, name, value )
		except KeyError, e:
			self.logIt( "pylib.Was.Environment.setEnvironmentVariable(): Unable to set " + str( e ) + ".\n" )
		#Endtry

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setWasEnv()
	#
	#	DESCRIPTION:
	#		Set the WAS environment.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setWasEnv(self, value=None):
		"""Get the WAS environment.
           PARAMETERS:

           RETURN:
               env
		"""
		if value is None:
			self.logIt( "pylib.Was.Environment.setWasEnv(): value is not set.  Assuming 'prod'\n" )
			value					= 'prod'
			self.WDT_ENVIRONMENT	= value.upper()
		else:
			self.setEnvironmentVariable( name='WDT_ENVIRONMENT', value=value.upper() )
		#Endif
		#self.env			= value.upper()

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getDomain()
	#
	#	DESCRIPTION:
	#		Get the WAS domain.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		env
	##################################################################################
	def getDomain(self):
		"""Get the Domain.
           PARAMETERS:

           RETURN:
               env
		"""
		return self.domain

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getDomainVersion()
	#
	#	DESCRIPTION:
	#		Get the WAS domain version.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		env
	##################################################################################
	def getDomainVersion(self):
		"""Get the DomainVersion.
           PARAMETERS:

           RETURN:
               env
		"""
		return self.domain_version

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getDomainEnv()
	#
	#	DESCRIPTION:
	#		Get the WAS domain env.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		domain_env
	##################################################################################
	def getDomainEnv(self):
		"""Get the DomainEnv.
           PARAMETERS:

           RETURN:
               domain_env
		"""
		return self.domain_env

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getDomainHome()
	#
	#	DESCRIPTION:
	#		Get the WAS domain home.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		domain_home
	##################################################################################
	def getDomainHome(self):
		"""Get the Domain home.
           PARAMETERS:

           RETURN:
               home
		"""
		return self.home

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	calcDomainVersion()
	#
	#	DESCRIPTION:
	#		Calculate the domain version.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		domain_version
	##################################################################################
	def calcDomainVersion(self):
		"""Calculate the domain version.
           PARAMETERS:

           RETURN:
               A string containing the domain version.
		"""
		rVal = "UNKNOWN"
		##############################################################
		#if( re.match( '^V7', str( self.domain ) ) ): rVal = "v7"
		#if( re.match( '^V6', str( self.domain ) ) ): rVal = "v6"
		#if( re.match( '^V5', str( self.domain ) ) ): rVal = "v5"
		#if rVal == "UNKNOWN":
		#	result = re.match( '^(\D\d)(.*)', str( self.domain) )
		#	rVal = result.group(1).lower()
		##Endif
		##############################################################
		result	= re.match( '^(\D\d)(.*)', str( self.domain) )
		rVal	= result.group(1).lower()
		return rVal

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	calcDomainEnv()
	#
	#	DESCRIPTION:
	#		Calculate the domain environment.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		domain_environment
	##################################################################################
	def calcDomainEnv(self):
		"""Calculate the domain environment.
           PARAMETERS:

           RETURN:
               A string containing the domain environment.
		"""
		rVal = "UNKNOWN"
		if( re.match( '.*LAB$', str( self.domain ) ) ):		rVal = "DEV"
		if( re.match( '.*DEV$', str( self.domain ) ) ):		rVal = "DEV"
		if( re.match( '.*QUAL$', str( self.domain ) ) ):	rVal = "QUAL"
		if( re.match( '.*PROD$', str( self.domain ) ) ):	rVal = "PROD"
		return rVal

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	calcHome()
	#
	#	DESCRIPTION:
	#		Calculate the WAS home.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		home
	##################################################################################
	def calcHome(self):
		"""Calculate the WAS home.
           PARAMETERS:

           RETURN:
               A string containing the WAS home.
		"""
		rVal = ''
		myenv = self.getWasEnv()
		#print "myenv=" + str( myenv )
		if self.getWasEnv().lower() == 'prod':
			rVal = '/nfs/dist/dmp/WDT'
		else:
			rVal = '/nfs/dist/dmp/WDT/' + str( self.getWasEnv().upper() )
		return rVal

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAllTheEnvironment()
	#
	#	DESCRIPTION:
	#		Get all the environment variables and make them part of this object.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAllTheEnvironment(self):
		"""Get all the environment variables and make them part of this object.
        PARMETERS:
        RETURN:
        """

		myEnv = os.environ
		for env in myEnv.keys():
			setattr(self, env, myEnv.get( env ) )
		#Endfor

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	logEnv()
	#
	#	DESCRIPTION:
	#		Log the environment.
	#
	#	PARAMETERS:
	#		debugOnly
	#
	#	RETURN:
	##################################################################################
	def logEnv(self, debugOnly=True):
		"""Log the environment.
        PARMETERS:
            debugOnly is either True or False.  A value of True will only log if the
            logger's debug flag is set.
        """

		myEnv = os.environ
		for env in myEnv.keys():
			if( debugOnly == True ):
				self.debug( "pylib.Was.Environment.logEnv(): " + str( env ) + "=" + str( myEnv.get( env ) ) + "\n" )
			else:
				self.logIt( "pylib.Was.Environment.logEnv(): " + str( env ) + "=" + str( myEnv.get( env ) ) + "\n" )
			#Endif
		#Endfor

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
				self.debug( "pylib.Was.Environment.logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
			else:
				self.logIt( "pylib.Was.Environment.logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
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
	myLogger = MyLogger( LOGFILE="/tmp/WasEnv.log", STDOUT=True, DEBUG=False )
	myObject = Environment(domain="V8_DEV", logger=myLogger)
	#myObject2 = Environment(domain="V6_DEV", logger=myLogger);
	print myObject.getWasEnv()
	print myObject.getDomain()
	print myObject.getDomainEnv()
	print myObject.getDomainVersion()
	print myObject.getDomainHome()
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

