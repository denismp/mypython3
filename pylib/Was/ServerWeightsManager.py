#!/usr/bin/env jython
######################################################################################
##	ServerWeightsManager.py
##
##	Python module for ServerWeightsManager attributes.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	02/03/2010	Denis M. Putnam		Created.
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
from pylib.Was.AttributeUtils import *
from pylib.Was.TemplateListManager import *
from pylib.Was.JDBCProviderManager import *
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

class ServerWeightsManager( AttributeUtils ):
	"""
    ServerWeightsManager class that contains methods to manager server weights.
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
				templateListManager,
				scope,
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               adminClient         - instance of the pylib.Was.AdminClient class.
               configService       - instance of the pylib.Was.ConfigService class.
               templateListManager - instance of the pylib.Was.TemplateListManager class.
			   scope               - Something like:
                                       "Node=node_ServicesA_01:Server=as_was7test_01"
               logger              - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		self.adminClient			= adminClient
		self.configService			= configService
		self.templateListManager	= templateListManager
		self.logger					= logger
		AttributeUtils.__init__( self, configService, scope, type='ClusterMember', logger=self.logger )
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
				if re.search( '__doc__',  attr ): continue
				if re.search( '__module__',  attr ): continue
				if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
				if re.search( 'instance', str( getattr( self, attr ) ) ): continue
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
	#	modifyServerWeights()
	#
	#	DESCRIPTION:
	#		Modify the server weights attributes.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifyServerWeights( 
							self, 
							memberName,
							serverWeight='2'
							):
		"""Modify the server weights attributes.
		   PARAMETERS:
		       memberName   -- The name of the Server that is this cluster member. This attribute 
                               matches the name attribute for the Server.
		       serverWeight -- The relative amount of work to be routed to this cluster member.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifyServerWeights(): memberName=" + str( memberName ) + "\n" )
		self.debug( __name__ + ".modifyServerWeights(): serverWeight=" + str( serverWeight ) + "\n" )

		rVal = False

		############################################################
		#	For all our configuration Objects within the scope,
		#	find the matching memberName and modify the attributes.
		#	The type is expected to be 'ClusterMember'.
		############################################################
		for configObject in self.configObjects:
			self.debug( __name__ + ".modifyServerWeights(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".modifyServerWeights(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the AttributeList
			########################################################
			#pArgs 				= array( ['members'], java.lang.String )
			pArgs 				= None
			memberAttributeList	= self.configService.getAttributes( self.configService.session, configObject, pArgs, False )
			myMemberName		= self.configService.configServiceHelper.getAttributeValue( memberAttributeList, 'memberName' )
			myWeight			= self.configService.configServiceHelper.getAttributeValue( memberAttributeList, 'weight' )

			if myMemberName != memberName: continue

			self.debug( __name__ + ".modifyServerWeights(): myMemberName=" + str( myMemberName ) + "\n" )
			self.debug( __name__ + ".modifyServerWeights(): myWeight=" + str( myWeight ) + "\n" )
			self.debug( __name__ + ".modifyServerWeights(): BEFORE memberAttributeList=" + str( memberAttributeList ) + "\n" )
			self.debug( __name__ + ".modifyServerWeights(): BEFORE memberAttributeList type=" + str( type( memberAttributeList ) ) + "\n" )
			#######################################################
			#	Set the AttributeList values.
			#######################################################
			self.configService.configServiceHelper.setAttributeValue( memberAttributeList, 'weight', int( serverWeight ) )

			self.debug( __name__ + ".modifyServerWeights(): AFTER memberAttributeList=" + str( memberAttributeList ) + "\n" )

			####################################################################
			#	Save the attributes to the current session.
			####################################################################
			self.configService.setAttributes( self.configService.session, configObject, memberAttributeList )
			rVal = True
			break
		#Endfor

		if rVal: self.refresh()
		return rVal
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	testFunc()
	#
	#	DESCRIPTION:
	#		Do not use.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def testFunc( self ):
		"""Do not use.
		   PARAMETERS:
		   RETURN:
		       True if successful, or False.
		"""

		rVal = True

		############################################################
		#	Display as much as possible.
		############################################################
		for configObject in self.configObjects:

			self.debug( __name__ + ".testFunc(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".testFunc(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the classloaders AttributeList
			########################################################
			pArgs = array( ['memberName'], java.lang.String )
			#pArgs = None
			myAttributeList			= self.configService.getAttributes( self.configService.session, configObject, pArgs, True )
			self.debug( __name__ + ".testFunc(): myAttributeList=" + str( myAttributeList ) + "\n" )
			self.debug( __name__ + ".testFunc(): myAttributeList type=" + str( type( myAttributeList ) ) + "\n" )

			for propAttr in myAttributeList:
				propName = propAttr.getName()
				propValue= propAttr.getValue()
				self.debug( __name__ + ".testFunc(): propName=" + str( propName ) + "\n" )
				#self.debug( __name__ + ".testFunc(): propName type=" + str( type( propName ) ) + "\n" )
				self.debug( __name__ + ".testFunc(): propValue=" + str( propValue ) + "\n" )
				#self.debug( __name__ + ".testFunc(): propValue type=" + str( type( propValue ) ) + "\n" )
			#Endfor
		#Endfor

		#if rVal: self.refresh()
		return rVal
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
	myLogger	= MyLogger( LOGFILE="/tmp/ServerWeightsManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/ServerWeightsManager.log", STDOUT=True, DEBUG=False )
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
	serverName	= "as_ServicesA_a01"
	clusterName	= "cl_ServicesA_a"
	jdbcProvider= "OracleJdbcDriverXA"
	dataSource	= "ForOracleXAJF"
	template	= "DataSoure_ora_6"

	#myscope			= "Node=" + nodeName + ":ServerIndex:ServerEntry=" + serverName
	#myscope			= "Node=" + nodeName + ":ServerIndex:ServerEntry=" + serverName
	#myscope			= "Cell=" + cellName + ":Node=" + nodeName + ":Server=" + serverName
	#myscope				= "Node=" + nodeName + ":Server=" + serverName
	myscope				= "ServerCluster=" + clusterName
	configService 		= ConfigService( adminClient=myclient, logger=myLogger )
	templateListManager	= TemplateListManager( configService, type="ClusterMember", logger=myLogger )
	myServerWeightsManager	= ServerWeightsManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in myServerWeightsManager.attributesList:
		myServerWeightsManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myServerWeightsManager.attributesList:
		myServerWeightsManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myServerWeightsManager.attributesList:
			myServerWeightsManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	myServerWeightsManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/ServerWeightsManager.tsv" )

	myServerWeightsManager.testFunc()

	rc = myServerWeightsManager.modifyServerWeights( 
							'as_ServicesA_a01',
							serverWeight=3
							)

	myServerWeightsManager.testFunc()
	rc = myServerWeightsManager.modifyServerWeights( 
							'as_ServicesA_a01',
							serverWeight=2
							)

	#myServerWeightsManager.testFunc()
	if rc: myServerWeightsManager.saveSession( False )

	configService.closeMe()
	myServerWeightsManager.closeMe()
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
