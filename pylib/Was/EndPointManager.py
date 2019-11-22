#!/usr/bin/env jython
######################################################################################
##	EndPointManager.py
##
##	Python module to
##	handle specialEndPoint resource management.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	01/18/2010	Denis M. Putnam		Created.
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

class EndPointManager( AttributeUtils ):
	"""
    EndPointManager class that contains EndPoint management methods.
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
               adminClient   - instance of the pylib.Was.AdminClient class.
               configService - instance of the pylib.Was.ConfigService class.
               templateListManager - instance of the pylib.Was.TemplateListManager class.
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

		self.adminClient		= adminClient
		self.configService		= configService
		self.templateListManager	= templateListManager
		self.logger				= logger
		AttributeUtils.__init__( self, configService, scope, type='NamedEndPoint', logger=self.logger )
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
	#	addEndPoint()
	#
	#	DESCRIPTION:
	#		Add a DataSource to websphere.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def addEndPoint(
						self,
						endPointName,
						host,
						port
						):
		"""Add a DataSource to websphere.
		   PARAMETERS:
		       endPointName -- name of the EndPoint.  Something like 'WC_adminhost'
			   host         -- name of the host.  Something like 'dilabvirt31-v1'
			   port         -- port number.
		   RETURN:
		       True if successful or the EndPoint exists, or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".addEndPoint(): called.\n" )
		self.debug( __name__ + ".addEndPoint(): endPointName=" + str( endPointName ) + ".\n" )
		self.debug( __name__ + ".addEndPoint(): host=" + str( host ) + ".\n" )
		self.debug( __name__ + ".addEndPoint(): port=" + str( port ) + ".\n" )

		#######################################################
		#	Check to see if the given dataSourceName already exists.
		#######################################################
		if self.isEndPointExist( endPointName ):
			self.logIt( __name__ + ".addEndPoint(): EndPoint " + str( endPointName ) + " already exists, so it will not be added." + ".\n" )
			return True
		#Endif

		self.logIt( __name__ + ".addEndPoint(): EndPoint " + str( endPointName ) + " doesn't exist, so it will be added." + ".\n" )
	
		######################################################
		#	Set up the attributes.
		######################################################
		endPointList				= AttributeList()
		nameAttr					= Attribute( 'endPointName',endPointName )
		hostAttr					= Attribute( 'host',		host )
		portAttr					= Attribute( 'port',		int( port ) )

		######################################################
		#	Build the AttribtueList.
		######################################################
		myAttrList	= AttributeList()

		myAttrList.add( nameAttr )

		#######################################################
		#	Create the NamedEndPoint.
		#######################################################
		attributeName	= 'specialEndpoints'
		configType		= 'NamedEndPoint'
		rc = self.createConfigData( attributeName, configType, myAttrList )

		if rc:
			myargs			= array( ['endPoint'], java.lang.String )
			endpointAttrs	= self.configService.getAttributes( self.configService.session, self.myLastConfiguredObject, myargs, False )
			self.debug( __name__ + ".addEndPoint(): endpointAttrs" + str( endpointAttrs ) + "\n" )
			self.debug( __name__ + ".addEndPoint(): endpointAttrs type" + str( type( endpointAttrs ) ) + "\n" )
			the_parent	= self.myLastConfiguredObject;
			self.debug( __name__ + ".addEndPoint(): the_parent=" + str( the_parent ) + "\n" )
			self.debug( __name__ + ".addEndPoint(): the_parent type=" + str( type( the_parent ) ) + "\n" )

			try:
				endpointList = AttributeList()
				endpointList.add( hostAttr )
				endpointList.add( portAttr )
				self.configService.createConfigData( self.configService.session, the_parent, 'endPoint', 'EndPoint', endpointList )
				self.refresh()
			except com.ibm.websphere.management.exception.ConfigServiceException, e:
				self.logIt( __name__ + ".addEndPoint(): Unable to create the EndPoint for " + str( endPointName ) + ":" + str( e ) + "\n" )
				return False
			except com.ibm.websphere.management.exception.ConnectorException, ce:
				self.logIt( __name__ + ".addEndPoint(): Unable to create the EndPoint for " + str( endPointName ) + ":" + str( ce ) + "\n" )
				return False
			#Endtry
		else:
			self.logIt( __name__ + ".addEndPoint(): Unable to create the NamedEndPoint for " + str( endPointName ) + ":" + str( e ) + "\n" )
			
		#Endif

		return rc
		
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	isEndPointExistNotUsedButAGoodReference
	#
	#	DESCRIPTION:
	#		Does the endPointName exist.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def isEndPointExistNotUsedButAGoodReference( self, epname):
		"""Does the endPointName exist.
		   PARAMETERS:
		       epname  -- name of the EndPoint.  Something like 'WC_adminhost'
		   RETURN:
		       True if successful, or False.
		"""
		#######################################################
		#	Check to see if the given EndPoint exists.
		#######################################################
		myargs			= array( ['specialEndpoints'], java.lang.String )
		endpointAttrs	= self.configService.getAttributes( self.configService.session, self.rootObjectName, myargs, False )
		#endpointAttrs	= self.configService.getAttributes( self.configService.session, self.rootObjectName, None, False )
		#self.debug( __name__ + ".isEndPointExist(): endpointAttrs=" + str( endpointAttrs ) + "\n" )
		self.debug( __name__ + ".isEndPointExist(): endpointAttrs type=" + str( type( endpointAttrs ) ) + "\n" )
		for endpointAttr in endpointAttrs:
			#self.debug( __name__ + ".isEndPointExist(): endpointAttr=" + str( endpointAttr ) + "\n" )
			self.debug( __name__ + ".isEndPointExist(): endpointAttr type=" + str( type( endpointAttr ) ) + "\n" )
			attrName = endpointAttr.getName()
			specialEndPointAttrs= endpointAttr.getValue()
			self.debug( __name__ + ".isEndPointExist(): attrName=" + str( attrName ) + "\n" )
			self.debug( __name__ + ".isEndPointExist(): attrName type=" + str( type( attrName ) ) + "\n" )
			#self.debug( __name__ + ".isEndPointExist(): specialEndPointAttrs=" + str( specialEndPointAttrs ) + "\n" )
			self.debug( __name__ + ".isEndPointExist(): specialEndPointAttrs type=" + str( type( specialEndPointAttrs ) ) + "\n" )
			if isinstance( specialEndPointAttrs, java.util.ArrayList ):
				for namedEndPoint in specialEndPointAttrs:
					#self.debug( __name__ + ".isEndPointExist(): namedEndPoint=" + str( namedEndPoint ) + "\n" )
					self.debug( __name__ + ".isEndPointExist(): namedEndPoint type=" + str( type( namedEndPoint ) ) + "\n" )
					epArgs = array( ['endPointName'], java.lang.String )
					nameAttrs	= self.configService.getAttributes( self.configService.session, namedEndPoint, epArgs, False )
					self.debug( __name__ + ".isEndPointExist(): nameAttrs=" + str( nameAttrs ) + "\n" )
					self.debug( __name__ + ".isEndPointExist(): nameAttrs type=" + str( type( nameAttrs ) ) + "\n" )
					epName = self.configService.configServiceHelper.getAttributeValue( nameAttrs, 'endPointName' )
					if epName == epname:
						return True
				#Endfor
			#Endif
		#Endfor
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	isEndPointExist()
	#
	#	DESCRIPTION:
	#		Does the endPointName exist.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def isEndPointExist( self, epname):
		"""Does the endPointName exist.
		   PARAMETERS:
		       epname  -- name of the EndPoint.  Something like 'WC_adminhost'
		   RETURN:
		       True if successful, or False.
		"""
		#######################################################
		#	Check to see if the given EndPoint exists.
		#######################################################
		myvalues = self.getAttributeValues( 'endPointName' )
		for value in myvalues:
			if value == epname:
				return True
		#Endfor
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	deleteEndPoint()
	#
	#	DESCRIPTION:
	#		Delete the EndPoint by the given name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deleteEndPoint( self, epname):
		"""Delete the EndPoint by the given name.
		   PARAMETERS:
		       epname  -- name of the EndPoint.  Something like 'WC_adminhost'
		   RETURN:
		       True if successful, or False.
		"""
		rVal = True

		########################################################
		#	Get the list of attributes for the specialEndpoints.
		########################################################
		myargs			= array( ['specialEndpoints'], java.lang.String )
		endpointAttrs	= self.configService.getAttributes( self.configService.session, self.rootObjectName, myargs, False )
		#endpointAttrs	= self.configService.getAttributes( self.configService.session, self.rootObjectName, None, False )
		#self.debug( __name__ + ".deleteEndPoint(): endpointAttrs=" + str( endpointAttrs ) + "\n" )
		self.debug( __name__ + ".deleteEndPoint(): endpointAttrs type=" + str( type( endpointAttrs ) ) + "\n" )

		#######################################################
		#	For each endpoint attribute in the attributes list
		#	search for the NamedEndPoint to see if we find
		#	a match on the givne epname.
		#######################################################
		for endpointAttr in endpointAttrs:
			#self.debug( __name__ + ".deleteEndPoint(): endpointAttr=" + str( endpointAttr ) + "\n" )
			self.debug( __name__ + ".deleteEndPoint(): endpointAttr type=" + str( type( endpointAttr ) ) + "\n" )

			attrName				= endpointAttr.getName()	# attribute name.  Not used.
			specialEndPointAttrs	= endpointAttr.getValue()	# This should be an ArrayList.

			self.debug( __name__ + ".deleteEndPoint(): attrName=" + str( attrName ) + "\n" )
			self.debug( __name__ + ".deleteEndPoint(): attrName type=" + str( type( attrName ) ) + "\n" )
			#self.debug( __name__ + ".deleteEndPoint(): specialEndPointAttrs=" + str( specialEndPointAttrs ) + "\n" )
			self.debug( __name__ + ".deleteEndPoint(): specialEndPointAttrs type=" + str( type( specialEndPointAttrs ) ) + "\n" )

			###########################################################
			#	Make sure it is an ArrayList.
			###########################################################
			if isinstance( specialEndPointAttrs, java.util.ArrayList ):

				############################################
				#	Loop over the ArrayList.
				############################################
				for namedEndPoint in specialEndPointAttrs:
					#self.debug( __name__ + ".deleteEndPoint(): namedEndPoint=" + str( namedEndPoint ) + "\n" )
					self.debug( __name__ + ".deleteEndPoint(): namedEndPoint type=" + str( type( namedEndPoint ) ) + "\n" )

					##########################################
					#	Get the NamedEndPoint attribute list.
					##########################################
					epArgs = array( ['endPointName'], java.lang.String )
					nameAttrs	= self.configService.getAttributes( self.configService.session, namedEndPoint, epArgs, False )
					self.debug( __name__ + ".deleteEndPoint(): nameAttrs=" + str( nameAttrs ) + "\n" )
					self.debug( __name__ + ".deleteEndPoint(): nameAttrs type=" + str( type( nameAttrs ) ) + "\n" )

					#########################################
					#	Get the endPointName and check for
					#	a match.
					#########################################
					epName = self.configService.configServiceHelper.getAttributeValue( nameAttrs, 'endPointName' )
					if epName == epname:
						rVal = self.deleteConfigData( namedEndPoint )
						############################################
						#	We could stop here, but not stopping
						#	removes all NamedEndPoint's that match.
						#	This keeps things clean in WebSphere.
						############################################
				#Endfor
			#Endif
		#Endfor
		if rVal: self.refresh()
		return rVal
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createEndPoint()
	#
	#	DESCRIPTION:
	#		Create a EndPoint.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createEndPoint(
						self,
						endPointName,
						host,
						port
						):
		"""Create a EndPoint.
		   PARAMETERS:
		       endPointName -- name of the EndPoint.  Something like 'WC_adminhost'
			   host         -- name of the host.  Something like 'dilabvirt31-v1'
			   port         -- port number.
		   RETURN:
		       True if successful or the EndPoint exists, or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createEndPoint(): called.\n" )
		self.debug( __name__ + ".createEndPoint(): endPointName=" + str( endPointName ) + ".\n" )
		self.debug( __name__ + ".createEndPoint(): host=" + str( host ) + ".\n" )
		self.debug( __name__ + ".createEndPoint(): port=" + str( port ) + ".\n" )

		############################################################
		#	Check to see if the given dataSourceName already exists.
		############################################################
		if self.isEndPointExist( endPointName ):
			self.logIt( __name__ + ".createEndPoint(): EndPoint " + str( endPointName ) + " already exists, so it will be deleted and then added." + ".\n" )
			self.deleteEndPoint( endPointName )
		#Endif
		self.logIt( __name__ + ".createEndPoint(): EndPoint adding " + str( endPointName ) + ".\n" )

		rc = self.addEndPoint( 
								endPointName,
								host, 
								port 
								)
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
	myLogger	= MyLogger( LOGFILE="/tmp/EndPointManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/EndPointManager.log", STDOUT=True, DEBUG=False )
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

	myscope				= "Node=" + nodeName + ":ServerIndex:ServerEntry=" + serverName
	#myscope			= "Cell=" + cellName + ":Node=" + nodeName + ":NamedEndPoint"
	configService 		= ConfigService( adminClient=myclient, logger=myLogger )
	templateListManager	= TemplateListManager( configService, type="NamedEndPoint", logger=myLogger )
	myEndPointManager	= EndPointManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in myEndPointManager.attributesList:
		myEndPointManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myEndPointManager.attributesList:
		myEndPointManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myEndPointManager.attributesList:
			myEndPointManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	myEndPointManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/EndPoints.tsv" )

	########################################################
	#	Create the data source.
	########################################################
	endPointName	= "DENIS_ENDPOINT"
	host			= 'denishost'
	port			= '9999'
	rc = myEndPointManager.createEndPoint(
						endPointName,
						host,
						port
						)

	if rc: myEndPointManager.saveSession( False )

	configService.closeMe()
	myEndPointManager.closeMe()
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
