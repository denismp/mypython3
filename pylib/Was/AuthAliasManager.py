#!/usr/bin/env jython
######################################################################################
##	AuthAliasManager.py
##
##	Python module replaces some of the functions in the 
##	/nfs/dist/dmp/amp/wdt/_resources.jacl 
##	file and makes AuthAlias/JAASAuthData resource management object oriented.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	12/30/2009	Denis M. Putnam		Created.
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
from pylib.Was.TemplateListManager import *
from pylib.Was.AttributeUtils import *
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

class AuthAliasManager( AttributeUtils ):
	"""
    AuthAliasManager class that contains VirtualHost management methods.
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
				scope,
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               adminClient   - instance of the pylib.Was.AdminClient class.
               configService - instance of the pylib.Was.ConfigService class.
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
		self.logger					= logger
		AttributeUtils.__init__( self, self.configService, scope, type='JAASAuthData', logger=self.logger )
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
				#if re.search( '__doc__',  attr ): continue
				#if re.search( '__module__',  attr ): continue
				#if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
				#if re.search( 'instance', str( getattr( self, attr ) ) ): continue
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
	#	addAuthAlias()
	#
	#	DESCRIPTION:
	#		Add a JAASAuthData entry to websphere.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def addAuthAlias(self,alias,userid,password,description="This provider was created by the pylib.Was.AuthAliasManager."):
		"""Add a JAASAuthData entry to websphere.
		   PARAMETERS:
		       alias       -- alias name.
		       userid      -- userid.
			   password    -- password.
			   description -- description text.
		   RETURN:
		       True if successful or the jdbcName exists, or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".addAuthAlias(): called.\n" )
		self.debug( __name__ + ".addAuthAlias(): alias=" + str( alias ) + ".\n" )
		self.debug( __name__ + ".addAuthAlias(): userid=" + str( userid ) + ".\n" )
		self.debug( __name__ + ".addAuthAlias(): password=" + str( password ) + ".\n" )
		self.debug( __name__ + ".addAuthAlias(): description=" + str( description ) + ".\n" )

		#######################################################
		#	Check to see if the given alias already exists.
		#######################################################
		myvalues = self.getAttributeValues( 'alias' )
		for value in myvalues:
			if value == alias:
				self.logIt( __name__ + ".addAuthAlias(): AuthAlias " + str( alias ) + " already exists, so it will not be added." + ".\n" )
				return True
			#Endif
		#Endfor
		self.logIt( __name__ + ".addAuthAlias(): AuthAlias " + str( alias ) + " doesn't exist, so it will be added." + ".\n" )
	
		######################################################
		#	Set up the attributes.
		######################################################
		nameAttr	= Attribute( 'alias', alias )
		desAttr		= Attribute( 'description', description )
		useridAttr	= Attribute( 'userId', userid )
		passwdAttr	= Attribute( 'password', password )

		myAttrList	= AttributeList()
		myAttrList.add( nameAttr )
		myAttrList.add( desAttr )
		myAttrList.add( useridAttr )
		myAttrList.add( passwdAttr )
		
		#######################################################
		#	Create the JAASAuthData record.
		#######################################################
		rc = self.createConfigData( 'authDataEntries', 'JAASAuthData', myAttrList )
		
		return rc
		
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createAuthAlias()
	#
	#	DESCRIPTION:
	#		Create an AuthAlias
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createAuthAlias(self,alias,userid,password,description="This authentication alias was created by the pylib.Was.AuthAliasManager."):
		"""Create an AuthAlias.
		   PARAMETERS:
		       alias       -- alias name.
		       userid      -- userid.
			   password    -- password.
			   description -- description text.
		   RETURN:
		       True if successful or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createAuthAlias(): called.\n" )
		self.debug( __name__ + ".createAuthAlias(): alias=" + str( alias ) + ".\n" )
		self.debug( __name__ + ".createAuthAlias(): userid=" + str( userid ) + ".\n" )
		self.debug( __name__ + ".createAuthAlias(): password=" + str( password ) + ".\n" )
		self.debug( __name__ + ".createAuthAlias(): description=" + str( description ) + ".\n" )

		#######################################################
		#	Check to see if the given alias already exists.
		#######################################################
		myvalues = self.getAttributeValues( 'alias' )
		for value in myvalues:
			if value == alias:
				self.logIt( __name__ + ".createAuthAlias(): AuthAlias " + str( alias ) + " already exists, so it will be deleted and then added." + ".\n" )
				myindex = self.getAttributeIndexByValue( 'alias', value )
				self.debug( __name__ + ".createAuthAlias(): myindex " + str( myindex ) + ".\n" )
				configObject = self.configObjects[ myindex ]
				rc = self.deleteConfigData( configObject )
			#Endif
		#Endfor
		self.logIt( __name__ + ".createAuthAlias(): Adding " + str( alias ) + ".\n" )

		rc = self.addAuthAlias( alias, userid, password, description=description )
		return rc
		
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
	myLogger	= MyLogger( LOGFILE="/tmp/AuthAliasManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/AuthAliasManager.log", STDOUT=True, DEBUG=False )
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
	profile		= "node_ServicesA_00"
	nodeName	= "node_ServicesA_01"
	serverName	= "as_was7test_01"
	#clusterName	= "cl_was7test_a"
	clusterName	= "cl_ServicesA_a"

	myscope 			= "Cell=" + str( cellName ) + ":Security"
	configService		= ConfigService( adminClient=myclient, logger=myLogger )
	myAuthAliasManager	= AuthAliasManager( adminObject, configService, scope=myscope, logger=myLogger)

	if not myAuthAliasManager.error:

		for mylist in myAuthAliasManager.attributesList:
			myAuthAliasManager.deepLogOfAttributes( mylist )
		#Endfor
		for mylist in myAuthAliasManager.attributesList:
			myAuthAliasManager.deepPrintOfAttributes( mylist )
		#Endfor
		try:
			fileName = "/tmp/denis.txt"
			FH = open( fileName, "w" )
			for mylist in myAuthAliasManager.attributesList:
				myAuthAliasManager.deepWriteOfAttributes( mylist, FH )
			#Endfor
			FH.close()
		except Exception, e:
				myLogger.logIt( "main(): " + str( e ) + "\n" )
				raise
		#Endtry

		myAuthAliasManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/AuthAlias.tsv" )

		#myAuthAliasManager.saveSession( False )
	else:
		myLogger.logIt( "main(): No AuthAliases found for scope=" + str(myscope) + "\n" )
	#Endif

	alias = profile + "/" + "DenisAlias"
	userid = "appd4ec"
	password = "was70"
	rc = myAuthAliasManager.createAuthAlias( alias, userid, password )
	if rc: myAuthAliasManager.saveSession()

	configService.closeMe()
	myAuthAliasManager.closeMe()
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
