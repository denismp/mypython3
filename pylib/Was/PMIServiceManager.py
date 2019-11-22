#!/usr/bin/env jython
######################################################################################
##	PMIServiceManager.py
##
##	Python module for PMIService attributes.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	01/25/2010	Denis M. Putnam		Created.
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

class PMIServiceManager( AttributeUtils ):
	"""
    PMIServiceManager class that contains PMIService management methods.
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

		self.adminClient			= adminClient
		self.configService			= configService
		self.templateListManager	= templateListManager
		self.logger					= logger
		AttributeUtils.__init__( self, configService, scope, type='PMIService', logger=self.logger )
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
	#	modifyPMIService()
	#
	#	DESCRIPTION:
	#		Modify the PMIService attributes.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifyPMIService( 
							self, 
							enable=True,
							initialSpecLevel='beanModule=H:cacheModule=H:connectionPoolModule=H:j2cModule=H:jvmRuntimeModule=H:orbPerfModule=H:servletSessionsModule=H:systemModule=H:threadPoolModule=H:transactionModule=H:webAppModule=H:webServicesModule=H:wlmModule=H:wsgwModule=H',
							statisticSet='basic',
							synchronizedUpdate=False
							):
		"""Modify the PMIService attributes.
		   PARAMETERS:
		       enable             -- Enable PMIService.  Default is True.
		       initialSpecLevel   -- A PMI spec string which stores the PMI spec level for all components in the 
                                     server. The spec string specifies initial performance monitoring levels for 
                                     various PMI modules. An empty value is allowed and treated as "use default level none" 
                                     for all the PMI modules. Any PMI module that is not specified is initialized 
                                     to a default level of none. The grammar of the string is a list of moduleName=level 
                                     connected by ":". The moduleName is one of the following: beanModule, acheModule, 
                                     connectionPoolModule, j2cModule, jvmRuntimeModule, orbPerfModule, servletSessionsModule, 
                                     systemModule, threadPoolModule, transactionModule, webAppModule, wlmModule, 
                                     webServicesModule, and wsgwModule. The level is one of the following: n, l, m, h, 
                                     and x, representing none, low, medium, high, and maximum, respectively. An example 
                                     spec string is beanModule=h:j2cModule=m:jvmRuntimeModule=h:webAppModule=m. 
		       statisticSet       -- Value defining the current statistic set being monitored. Can be any of several 
                                     preset statistic sets, or all, none, or custom. If custom, the enabled counters 
                                     are defined in the PMIModule. 
		       synchronizedUpdate -- When enabled, certain counters are updated within synchronized code blocks, 
                                     to allow for greater accuracy.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifyPMIService(): enable=" + str( enable ) + "\n" )
		self.debug( __name__ + ".modifyPMIService(): initialSpecLevel=" + str( initialSpecLevel ) + "\n" )
		self.debug( __name__ + ".modifyPMIService(): statisticSet=" + str( statisticSet ) + "\n" )
		self.debug( __name__ + ".modifyPMIService(): synchronizedUpdate=" + str( synchronizedUpdate ) + "\n" )

		rVal = True

		############################################################
		#	For all our configuration Objects within the scope,
		#	modify the attributes.  Hopefully there is only one
		#	configuration Object.  This depends on how the request
		#	was scoped.
		############################################################
		for configObject in self.configObjects:

			########################################################
			#	Do the scalar attributes first.
			########################################################
			self.debug( __name__ + ".modifyPMIService(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".modifyPMIService(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the PMIService AttributeList
			########################################################
			pmiServiceAttributeList	= self.configService.getAttributes( self.configService.session, configObject, None, True )

			self.debug( __name__ + ".modifyPMIService(): BEFORE pmiServiceAttributeList=" + str( pmiServiceAttributeList ) + "\n" )
			self.debug( __name__ + ".modifyPMIService(): BEFORE pmiServiceAttributeList type=" + str( type( pmiServiceAttributeList ) ) + "\n" )

			#######################################################
			#	Set the scalar PMIService AttributeList values.
			#######################################################
			self.configService.configServiceHelper.setAttributeValue( pmiServiceAttributeList, 'enable', java.lang.Boolean( enable ) )
			self.configService.configServiceHelper.setAttributeValue( pmiServiceAttributeList, 'initialSpecLevel', str( initialSpecLevel ) )
			self.configService.configServiceHelper.setAttributeValue( pmiServiceAttributeList, 'statisticSet', str( statisticSet ) )
			self.configService.configServiceHelper.setAttributeValue( pmiServiceAttributeList, 'synchronizedUpdate', java.lang.Boolean( synchronizedUpdate ) )
			self.debug( __name__ + ".modifyPMIService(): AFTER pmiServiceAttributeList=" + str( pmiServiceAttributeList ) + "\n" )
			####################################################################
			#	Save the pmiServiceAttributeList to the current session.
			####################################################################
			self.configService.setAttributes( self.configService.session, configObject, pmiServiceAttributeList )
		#Endfor

		if rVal: self.refresh()
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
	myLogger	= MyLogger( LOGFILE="/tmp/PMIServiceManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/PMIServiceManager.log", STDOUT=True, DEBUG=False )
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
	myscope				= "Node=" + nodeName + ":Server=" + serverName
	configService 		= ConfigService( adminClient=myclient, logger=myLogger )
	templateListManager	= TemplateListManager( configService, type="PMIService", logger=myLogger )
	myPMIServiceManager	= PMIServiceManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in myPMIServiceManager.attributesList:
		myPMIServiceManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myPMIServiceManager.attributesList:
		myPMIServiceManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myPMIServiceManager.attributesList:
			myPMIServiceManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	myPMIServiceManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/PMIService.tsv" )

	########################################################
	#	Make changes.
	########################################################
	rc = myPMIServiceManager.modifyPMIService( 
							enable=True,
							initialSpecLevel='beanModule=H:cacheModule=H:connectionPoolModule=H:j2cModule=H:jvmRuntimeModule=H:orbPerfModule=H:servletSessionsModule=H:systemModule=H:threadPoolModule=H:transactionModule=H:webAppModule=H:webServicesModule=H:wlmModule=H:wsgwModule=H',
							statisticSet='basic',
							synchronizedUpdate=False
							)

	if rc: myPMIServiceManager.saveSession( False )

	#for mylist in myPMIServiceManager.attributesList:
	#	myPMIServiceManager.deepLogOfAttributes( mylist )
	##Endfor
	configService.closeMe()
	myPMIServiceManager.closeMe()
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
