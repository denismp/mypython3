#!/usr/bin/env jython
######################################################################################
##	ConfigService.py
##
##	Python module extends the ConfigService and contains the 
##	Session, SystemAttributes, and SessionPropertyConstants objects.
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

import com.ibm.websphere.management.AdminClient
from com.ibm.websphere.management.configservice import ConfigService
from com.ibm.websphere.management.configservice import ConfigServiceProxy
from com.ibm.websphere.management.configservice import ConfigServiceHelper

from com.ibm.websphere.management.configservice import SessionPropertyConstants
from com.ibm.websphere.management.configservice import SystemAttributes

from com.ibm.websphere.management import Session

class ConfigService( ConfigServiceProxy ):
	"""ConfigService class that contains WebSphere ConfigService utilities."""

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
				adminClient=None,
				sessionUser=None,
				shareWorkspace=False,
				logger=None
		):
		"""Class Initializer.
           Python module extends the WAS ConfigServiceProxy and contains the
           SessionPropertyConstants, SystemAttributes, ConfigServiceHelper, and Session objects.
           PARAMETERS:
               adminClient - instance of the com.ibm.websphere.management.AdminClient class.
               sessionUser - optional session user id.
               shareWorkspace - default is False
               logger      - instance of the pylib.Utils.MyLogger class.

           RETURN:
               An instance of this class
		"""
		self.logger						= logger
		if adminClient is None: raise Exception, "Please specify the com.ibm.websphere.management.AdminClient connection instance."
		ConfigServiceProxy.__init__( self, adminClient )
		#if logger is None: raise Exception, "Please specify the logger instance."
		self.configServiceHelper		= ConfigServiceHelper()
		self.systemAttributes			= SystemAttributes()
		self.sessionPropertyConstants	= SessionPropertyConstants
		if sessionUser is None:
			self.session				= Session()
		else:
			self.session				= Session( sessionUser, shareWorkspace )

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
				if re.search( 'supportedConfigObjectTypes',  attr ): continue
				#self.debug( __name__ + ".logMySelf(): attr=" + str( attr ) + "\n" )
				if( debugOnly == True ):
					self.debug( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				else:
					self.logIt( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				#Endif
			except Exception, e:
				self.debug( __name__ + ".logMySelf(): " + str( e ) + "\n" )
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
		self.debug( __name__ + ".closeMe(): Discarding session=" + str( self.session.toString() ) + "\n" )
		self.discard( self.session )
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
	#	resolveObjectName()
	#
	#	DESCRIPTION:
	#		Get the javax.management.ObjectName's via a query string.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def resolveObjectName(self, query):
		"""
        Get the javax.management.ObjectName's via a query string.  This is the 
        equivalent of the AdminConfig.getid().
        PARAMETERS:
            query -- something like "VirtualHost=default_host", or "Cell=mycell"
        RETURN:
            An array of javax.management.ObjectName values.
		"""
		self.debug( __name__ + ".getObjectNameByQuery(): called.\n" )
		self.debug( __name__ + ".getObjectNameByQuery(): query=" + str( query ) + ".\n" )
		results = self.resolve( self.session, query )
		return results
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getList()
	#
	#	DESCRIPTION:
	#		Get a list of the requested objectType and query.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getList(self, objectType, query=None, attributeName=None):
		"""
        Get a list of the requested objectType and query.
        PARAMETERS:
			objectType -- something like "VirtualHost"
            query -- something like "Cell=Services_A"
			attributeName -- attribute name to search against for collections.  Something like "hostname" for a objectType of aliases.
        RETURN:
            A list of names.
		"""
		rList = list()
		
		###############################################
		#	Log parameters.
		###############################################
		self.debug( __name__ + ".getList(): called.\n" )
		self.debug( __name__ + ".getList(): objectType=" + str( objectType ) + ".\n" )
		self.debug( __name__ + ".getList(): query=" + str( query ) + ".\n" )
		self.debug( __name__ + ".getList(): attributeName=" + str( attributeName ) + ".\n" )
		
		results = self.resolveObjectName( query )
		#self.debug( __name__ + ".getList(): results=" + str( results ) + ".\n" )
		#self.debug( __name__ + ".getList(): results length=" + str( len( results ) ) + ".\n" )
		if len( results ) < 1: return rList

		attributes = array( [ objectType ], String )
		relationShips = self.getRelationships( self.session, results[0], attributes )
		#self.debug( __name__ + ".getList(): relationShips=" + str( relationShips ) + ".\n" )
		#self.debug( __name__ + ".getList(): relationShips length=" + str( len( relationShips ) ) + ".\n" )

		##############################################
		#	If we get the relationships then get
		#	the display names.
		##############################################
		if len( relationShips ) > 0:
			for relationShip in relationShips:
				for myObject in relationShip.getValue():
					#self.debug( __name__ + ".getList(): myObject=" + str( myObject ) + ".\n" )
					myname = self.configServiceHelper.getDisplayName( myObject )
					#self.debug( __name__ + ".getList(): myname=" + str( myname ) + ".\n" )
					#self.debug( __name__ + ".getList(): myname type=" + str( type( myname ) ) + ".\n" )
					rList.append( myname )
				#Endfor
			#Endfor
		else:
			################################################
			#	We didn't get any relationships so now we
			#	have to dig deeper and match the names on
			#	the attributeName value.
			################################################
			attributes = array( [ objectType ], String )
			myAttrList = self.getAttributes( self.session, results[0], attributes, False )
			#self.debug( __name__ + ".getList(): myAttrList=" + str( myAttrList ) + ".\n" )
			#self.debug( __name__ + ".getList(): myAttrList length=" + str( len( myAttrList ) ) + ".\n" )
			objectList = self.configServiceHelper.getAttributeValue( myAttrList, objectType )

			for myObject in objectList:
				#self.debug( __name__ + ".getList(): myObject=" + str( myObject ) + ".\n" )
				myAttrList = self.getAttributes( self.session, myObject, None, False )
				#self.debug( __name__ + ".getList(): myAttrList=" + str( myAttrList ) + ".\n" )
				for attr in myAttrList:
					if attr.getName() == attributeName:
						myname = attr.getValue()
						#self.debug( __name__ + ".getList(): myname=" + str( myname ) + ".\n" )
						#self.debug( __name__ + ".getList(): myname type=" + str( type( myname ) ) + ".\n" )
						rList.append( myname )
				#Endif
			#Endfor
		#Endif
		return sorted( rList )
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
	myLogger	= MyLogger( LOGFILE="/tmp/ConfigService.log", STDOUT=True, DEBUG=True )
	#adminClient = AdminClient( logger=myLogger, hostname="dilabvirt31-v1" )
	adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1", cellName='cellA' )
	try:
		myconn		= adminClient.createSOAPDefault()
		print dir( myconn )
		myObject	= ConfigService( myconn, logger=myLogger )
		tmyconn		= myObject.getAdminClient()
		print dir( tmyconn )
		print dir( myObject )
		print dir( myObject.systemAttributes )
		print dir( myObject.sessionPropertyConstants )
		myObject.closeMe()
	except Exception, e:
		myLogger.logIt( "main(): Unable to connect to the AdminClient.  Make sure that the WAS Manager is running.\n" + str( e ) + "\n" )
	#EndExcept
	##################################################################################
	#Enddef
	##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
	main()

