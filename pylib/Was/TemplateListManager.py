#!/usr/bin/env jython
######################################################################################
##	TemplateListManager.py
##
##	Python module handle retrieving and cacheing of WebSphere resource templates.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	01/04/2010	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
import random
import time
import pickle
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.ConfigService import *
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
from com.dmp.amp.utility.serialization import SerializationUtil

class TemplateListManager():
	"""
    TemplateListManager class to handle retrieving and cacheing of WebSphere resource templates.
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
				configService,
				type="DataSource",
				dmgr="dilabvirt31-v1",
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               configService - instance of the pylib.Was.ConfigService class.
               type          - list type.  Something like "DataSource" or "JDBCProvider".
               dmgr          - dmgr host name.  Not used at the moment.
               logger        - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		self.configService		= configService
		self.logger				= logger
		self.type				= type
		self.dmgr				= dmgr
		self.rowCount			= 0
		self.templateList		= list()
		#self.templateListFile	= "/nfs/dist/dmp/amp/cache/" + str( dmgr ) + '/' + str( type ) + ".cache"
		self.templateListFile	= "/nfs/dist/dmp/amp/cache/" + str( type ) + ".cache"
		self.logMySelf()
		self.loadConfigTemplates()
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
	#	loadConfigTemplates()
	#
	#	DESCRIPTION:
	#		Get the list of configuration templates from WebSphere.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def loadConfigTemplates(self):
		"""Get the list of configuration templates from WebSphere.
		   PARAMETERS:
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".loadConfigTemplates(): called.\n" )

		################################################################
		#	Check to see if we have the cache of templates.  If so,
		#	load the cache from disk, otherwise get it from WebSphere
		#	and then write it to disk.
		################################################################
		try:
			self.debug( __name__ + ".loadConfigTemplates(): " + str( self.templateListFile ) + "\n" )
			
			if os.access( self.templateListFile, os.R_OK ):
				FH = open( self.templateListFile, 'rb' )
				myUtil = SerializationUtil()
				mybytes = FH.read()
				#self.debug( __name__ + ".loadConfigTemplates(): mybytes length" + str( len( mybtes ) ) + "\n" )
				self.templateList = myUtil.bytesToObject( mybytes )
			else:
				self.templateList = self.configService.queryTemplates( self.configService.session, self.type )
				FH = open( self.templateListFile, 'wb' )
				myUtil = SerializationUtil()
				mybytes = myUtil.objectToBytes( self.templateList )
				FH.write( mybytes )
				FH.close()
			#Endif
		################################################################
		#	If we get an exception read the template list from
		#	WebSphere and try to cache the results.
		################################################################
		except Exception, e:
			self.logIt( __name__ + ".loadConfigTemplates(): failed to access " + str( self.templateListFile ) + ":" + str( e ) + "\n" )
			self.templateList = self.configService.queryTemplates( self.configService.session, self.type )
			try:
				FH = open( self.templateListFile, 'wb' )
				myUtil = SerializationUtil()
				mybytes = myUtil.objectToBytes( self.templateList )
				FH.write( mybytes )
				FH.close()
			except Exception, e2:
				self.logIt( __name__ + ".loadConfigTemplates(): failed to write " + str( self.templateListFile ) + ":" + str( e ) + "\n" )
			#Endtry
		except java.lang.Exception, ioe:
			self.logIt( __name__ + ".loadConfigTemplates(): failed to access " + str( self.templateListFile ) + ":" + str( ioe ) + "\n" )
			self.logIt( __name__ + ".loadConfigTemplates(): Retrieving template list from WebSphere\n" )
			self.templateList = self.configService.queryTemplates( self.configService.session, self.type )
			try:
				FH = open( self.templateListFile, 'wb' )
				myUtil = SerializationUtil()
				mybytes = myUtil.objectToBytes( self.templateList )
				FH.write( mybytes )
				FH.close()
			except Exception, e2:
				self.logIt( __name__ + ".loadConfigTemplates(): failed to write " + str( self.templateListFile ) + ":" + str( e ) + "\n" )
			#Endtry
		#Endtry

		#self.debug( __name__ + ".loadConfigTemplates(): self.templateList=" + str( self.templateList ) + "\n" )
		self.debug( __name__ + ".loadConfigTemplates(): self.templateList type=" + str( type( self.templateList ) ) + "\n" )
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getTemplatesList()
	#
	#	DESCRIPTION:
	#		Get the list of configuration templates.
	# 
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getTemplatesList(self):
		"""Get the list of configuration templates from WebSphere.
		   PARAMETERS:
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getTemplatesList(): called.\n" )

		return self.templateList
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	logTemplatesList()
	#
	#	DESCRIPTION:
	#		Get the list of configuration templates.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def logTemplatesList(self):
		"""Get the list of configuration templates from WebSphere.
		   PARAMETERS:
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".logTemplatesList(): called.\n" )
		for template in self.templateList:
			configDataId = self.configService.configServiceHelper.getConfigDataId( template )
			self.logIt( __name__ + ".logTemplatesList(): configDataId=" + str( configDataId ) + '\n' )
			#self.logIt( __name__ + ".logTemplatesList(): configDataId type=" + str( type( configDataId ) ) + '\n' )
		#Endif

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getTemplateObject()
	#
	#	DESCRIPTION:
	#		Get the javax.management.ObjectName instance of the given template id.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getTemplateObject(self,templateId):
		"""Get the javax.management.ObjectName instance of the given template id.
		   PARAMETERS:
		       templateId -- something like 'JDBCProvider_3'
		   RETURN:
		       javax.management.ObjectName instance of the template.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getTemplateObject(): called.\n" )
		self.debug( __name__ + ".getTemplateObject(): templateId=" + str( templateId ) + ".\n" )
		for template in self.templateList:
			configDataId = self.configService.configServiceHelper.getConfigDataId( template )
			myHref = configDataId.getHref()
			mstr =  str( myHref ) + '$'

			if re.search( mstr, str( myHref ) ):
				return template
		#Endif
		return None
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
	myLogger	= MyLogger( LOGFILE="/tmp/TemplateListManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/TemplateListManager.log", STDOUT=True, DEBUG=False )
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
	nodeName	= "node_ServicesA_01"
	serverName	= "as_was7test_01"
	clusterName	= "cl_was7test_a"

	configService = ConfigService( adminClient=myclient, logger=myLogger )
	#myTemplateListManager = TemplateListManager( configService, type="JAASAuthData", logger=myLogger)
	#myTemplateListManager = TemplateListManager( configService, type="DataSource", logger=myLogger)
	#myTemplateListManager = TemplateListManager( configService, type="JDBCProvider", logger=myLogger)
	#myTemplateListManager = TemplateListManager( configService, type="J2EEResourceProperty", logger=myLogger)
	#myTemplateListManager = TemplateListManager( configService, type="J2CResourceAdapter", logger=myLogger)
	#myTemplateListManager = TemplateListManager( configService, type="NamedEndPoint", logger=myLogger)
	myTemplateListManager = TemplateListManager( configService, type="Property", logger=myLogger)

	#templateList = myTemplateListManager.getTemplatesList()
	#for template in templateList:
	#	configDataId = myTemplateListManager.configService.configServiceHelper.getConfigDataId( template )
	#	myLogger.logIt( "main(): configDataId=" + str( configDataId ) + "\n" )
	##Endif

	myTemplateListManager.logTemplatesList()

	template = myTemplateListManager.getTemplateObject( 'builtin_rra' )
	myLogger.logIt( "main(): template=" + str( template ) + "\n" )

	configService.discard( configService.session )

	configService.closeMe()
	myTemplateListManager.closeMe()
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
