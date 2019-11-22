#!/usr/bin/env jython
######################################################################################
##	WasEnvironment.py
##
##	Python module deals with WAS Environment.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	09/21/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Utils.Environment import *

class WasEnvironment( Environment ):
	"""
    WasEnvironment class that deals with the WAS environment.
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
		self.env = Environment.__init__( self, logger=logger )
		self.getWasEnv()
		self.setWasEnv( self.WDT_ENVIRONMENT )
		self.domain_version	= self.calcDomainVersion()
		self.domain_env		= self.calcDomainEnv()
		self.home			= self.calcHome()
		self.setMyEnvironment()
		self.validate()

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setMyEnvironment()
	#
	#	DESCRIPTION:
	#		Set the environment variable that can be used.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setMyEnvironment(self):
		"""Set the WAS environment variables that my be useful.
           Some of the variables may be legacy and no longer used.
           Typically the user should not call this function.
           PARAMETERS:

           RETURN:
		"""
		self.WDT_HOME = self.home

		self.getUpdateKey()

		self.setUpdateKey( self.UPDATEKEY )

		self.getStatusTempFile()

		self.setStatusTempFile( self.STATUS_TMP_FILE )

		self.getUseDAO()

		self.setUseDB( value=self.USE_DAO )

		self.setUseDAO( value=self.USE_DAO )

		self.getGenXML()

		self.setGenXML( value=self.GEN_XML )

		#self.getWasEmergency()

		#self.setWasEmergency( value=self.WAS_EMERGENCY )

		self.getDeploymentManagerDown()

		self.setDeploymentManagerDown( value=self.DEPLOYMENT_MANAGER_DOWN )

		self.setGenerateXML( value=self.GEN_XML )

		self.getWasRunningApplicationUpdate()

		self.setWasRunningApplicationUpdate( value=self.WAS_RUNNING_APPLICATION_UPDATE )

		self.setUpdateProcessRunning( value=self.WAS_RUNNING_APPLICATION_UPDATE )

		self.setAntCmdVariables()

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
			self.logIt( "pylib.Was.WasEnvironment.validate(): WARNING!  The domain=" + str( domain_env ) + " and the environment=" + str( self.getWasEnv() ) + " are not consistent.\n" )
			self.logMySelf()
			rVal = False
		#Endif
		return rVal

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setAntCmdVariables()
	#
	#	DESCRIPTION:
	#		Sets the path to the three ant files: ANT_CMD, ANT_PROPERTY_FILE,
	#		and the BUILDFILE
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setAntCmdVariables(self):
		"""
        Sets the path to the three ant files: ANT_CMD, ANT_PROPERTY_FILE, and the BUILDFILE.
		"""
		myHost				= socket.gethostname()
		myhome				= self.getDomainHome()
		myEnv				= self.getDomainEnv()
		myDomainVersion 	= self.getDomainVersion()
		ant_base_dir		= myhome + "/bin"
		ant_base_prop_dir	= ant_base_dir + "/" + myDomainVersion + "/ant"
		ant_cmd				= ant_base_dir + "/runant"
		ant_buildfile		= ant_base_dir + "/build.xml"
		ant_property_file	= ant_base_prop_dir + "/build_" + myDomainVersion + ".properties"
		self.setEnvironmentVariable( name='ANT_CMD', value=ant_cmd )	
		self.setEnvironmentVariable( name='BUILDFILE', value=ant_buildfile )	
		self.setEnvironmentVariable( name='ANT_PROPERTY_FILE', value=ant_property_file )	
		self.setEnvironmentVariable( name='DOMAIN_VERSION', value=myDomainVersion )	

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
	#	getWasEmergency()
	#
	#	DESCRIPTION:
	#		Get the WAS_EMERGENCY value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		WAS_EMERGENCY
	##################################################################################
	def getWasEmergency(self):
		"""Get the ugen_xml value.
           PARAMETERS:

           RETURN:
               value
		"""
		value		= self.getEnvironmentVariable( name='WAS_EMERGENCY', default='FALSE' )
		self.WAS_EMERGENCY = value
		return value

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setWasEmergency()
	#
	#	DESCRIPTION:
	#		Set the WAS_EMERGENCY value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setWasEmergency(self, value='NULL'):
		"""Set the gen_xml value.
           PARAMETERS:
               value is either 'true', 'false', or 'NULL'

           RETURN:
		"""
		self.setEnvironmentVariable( name='WAS_EMERGENCY', value=value.upper() )

	##################################################################################
	#Enddef
	##################################################################################
	
	##################################################################################
	#	getDeploymentManagerDown()
	#
	#	DESCRIPTION:
	#		Get the DEPLOYMENT_MANAGER_DOWN value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		WAS_EMERGENCY
	##################################################################################
	def getDeploymentManagerDown(self):
		"""Get the DEPLOYMENT_MANAGER_DOWN value.
           PARAMETERS:

           RETURN:
               value
		"""
		value = self.getEnvironmentVariable( name='DEPLOYMENT_MANAGER_DOWN', default='FALSE' )
		self.DEPLOYMENT_MANAGER_DOWN = value
		return value

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setDeploymentManagerDown()
	#
	#	DESCRIPTION:
	#		Set the WAS_EMERGENCY value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setDeploymentManagerDown(self, value='NULL'):
		"""Set the gen_xml value.
           PARAMETERS:
               value is either 'TRUE', 'FALSE', or 'NULL'

           RETURN:
		"""
		self.setEnvironmentVariable( name='DEPLOYMENT_MANAGER_DOWN', value=value )

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

           RETURN:
               value
		"""
		was_running_application_update		= self.getEnvironmentVariable( name='WAS_RUNNING_APPLICATION_UPDATE', default='FALSE' )
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
		self.setEnvironmentVariable( name='UPDATE_PROCESS_RUNNING', value=value.lower() )
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
	#	getWdtHome()
	#
	#	DESCRIPTION:
	#		Get the WDT_HOME value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		updatekey
	##################################################################################
	def getWdtHome(self):
		"""Get the WDT_HOME value.
           PARAMETERS:

           RETURN:
               value
		"""
		value	= self.getEnvironmentVariable( name='WDT_HOME', default='NULL' )
		self.WDT_HOME = value
		return value

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setWdtHome()
	#
	#	DESCRIPTION:
	#		Set the WDT_HOME value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setWdtHome(self, value='NULL'):
		"""Set the WDT_HOME value.
           PARAMETERS:
               value or 'NULL'

           RETURN:
		"""
		self.setEnvironmentVariable( name='WDT_HOME', value=value )
		self.WDT_HOME = value

	##################################################################################
	#Enddef
	##################################################################################
	##################################################################################
	#	getUpdateKey()
	#
	#	DESCRIPTION:
	#		Get the UPDATEKEY value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		updatekey
	##################################################################################
	def getUpdateKey(self):
		"""Get the UPDATEKEY value.
           PARAMETERS:

           RETURN:
               updatekey
		"""
		updatekey	= self.getEnvironmentVariable( name='UPDATEKEY', default='NULL' )
		return updatekey

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setUpdateKey()
	#
	#	DESCRIPTION:
	#		Set the updatekey value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setUpdateKey(self, value='NULL'):
		"""Set the updatekey value.
           PARAMETERS:
               value or 'NULL'

           RETURN:
		"""
		self.setEnvironmentVariable( name='UPDATEKEY', value=value.upper() )
		#self.use_dao		= value

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getStatusTempFile()
	#
	#	DESCRIPTION:
	#		Get the UPDATEKEY value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		updatekey
	##################################################################################
	def getStatusTempFile(self):
		"""Get the STATUS_TMP_FILE value.
           PARAMETERS:

           RETURN:
               status_tmp_file
		"""
		pidvalue = ''
		pid = os.getpid()
		if pid == 0:
			pidvalue = os.getlogin()
		else:
			pidvalue = str( pid )
		value="/tmp/" + str( socket.gethostname() ) + "." + str( pidvalue )
		status_tmp_file	= self.getEnvironmentVariable( name='STATUS_TMP_FILE', default=value )
		return status_tmp_file

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	setStatusTempFile()
	#
	#	DESCRIPTION:
	#		Set the status_tmp_file value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def setStatusTempFile(self, value='NULL'):
		"""Set the status_tmp_file value.
           PARAMETERS:
               value or 'NULL'

           RETURN:
		"""
		self.setEnvironmentVariable( name='STATUS_TMP_FILE', value=value )

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
			self.logIt( "pylib.Was.WasEnvironment.setWasEnv(): value is not set.  Assuming 'prod'\n" )
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
		myenv = self.getDomainEnv()
		#print "myenv=" + str( myenv )
		if self.getWasEnv().lower() == 'prod':
			#rVal = '/nfs/dist/dmp/WDT'
			rVal = '/dmp/WDT'
		else:
			#rVal = '/nfs/dist/dmp/WDT/' + str( self.getWasEnv().upper() )
			rVal = '/dmp/WDT/' + str( self.getWasEnv().upper() )
		#Endif
		myHost = socket.gethostname()
		if re.search( 'diploy11', myHost ):
			#rVal = "/nfs/dist" + rVal
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
				self.debug( "pylib.Was.WasEnvironment.logEnv(): " + str( env ) + "=" + str( myEnv.get( env ) ) + "\n" )
			else:
				self.logIt( "pylib.Was.WasEnvironment.logEnv(): " + str( env ) + "=" + str( myEnv.get( env ) ) + "\n" )
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
				self.debug( "pylib.Was.WasEnvironment.logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
			else:
				self.logIt( "pylib.Was.WasEnvironment.logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
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
	myLogger = MyLogger( LOGFILE="/tmp/WasEnvironment.log", STDOUT=True, DEBUG=False )
	myObject = WasEnvironment(domain="V6_DEV", logger=myLogger)
	#myObject2 = WasEnvironment(domain="V6_DEV", logger=myLogger);
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

