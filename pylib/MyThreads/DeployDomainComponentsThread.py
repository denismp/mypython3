#!/usr/bin/env python
######################################################################################
##	DeployDomainComponentsThread.py
##
##	Python module deals with deployment using threading.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	02/08/2010	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
import time
import random
from threading import Thread

from traitlets import ObjectName
from urllib3.contrib._securetransport.bindings import Boolean

from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.AdminClient import *
from pylib.Was.WasData import *
from pylib.Was.WasObject import *
from pylib.Was.AdminClient import *
from pylib.Was.ConfigService import *
from pylib.Was.AttributeUtils import *
# from java.lang import NullPointerException
# from java.lang import NoClassDefFoundError
# from java.lang import String
# from java.lang import Boolean
# from javax.management import InstanceNotFoundException
# from javax.management import MalformedObjectNameException
# from javax.management import ObjectName
# from com.ibm.websphere.management.application import AppManagement
# from com.ibm.websphere.management.application import AppConstants
# from com.ibm.websphere.management.application import AppManagementProxy
# from com.ibm.websphere.management import Session
# from com.ibm.websphere.management.exception import AdminException
# from com.ibm.websphere.management.configservice import ConfigServiceHelper
#from com.ibm.websphere.management.application.client import AppDeploymentController
#from com.ibm.websphere.management.application.client import AppDeploymentTask
#from com.ibm.websphere.management.application import AppNotification

# import com.ibm.websphere.security.WebSphereRuntimePermission as WebSphereRuntimePermission
# import com.ibm.websphere.security.auth.WSLoginFailedException as WSLoginFailedException
# import com.ibm.ws.security.util.InvalidPasswordDecodingException as InvalidPasswordDecodingException
# import com.ibm.websphere.management.exception.ConnectorException as ConnectorException

class DeployDomainComponentsThread( Thread ):
	"""DeployDomainComponentsThread class extends the Thread class to deploy domain components."""

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
				threadName=None,
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               adminClient	 - instance of the pylib.Was.AdminClient class.
               configService - ConfigService instance.
               logger        - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		Thread.__init__(self, name=threadName)	# Initialize the super.
		self.adminClient		= adminClient
		self.logger				= logger
		self.configService		= configService
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
	#	logHashTable()
	#
	#	DESCRIPTION:
	#		Log the given hashtable.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def logHashTable(self,hashtable):
		"""Log the given hashtable.
           PARAMETERS:
              hashtable   -- java.util.Hashtable containing the hashtable.

           RETURN:
		"""
		e = hashtable.keys()
		els = list( e )
		els.sort()
		for k in els:
			self.logIt( __name__ + ".logHashTable(): " + str( k ) + "=" + str( hashtable.get( k ) ) + "\n" )
		#Endfor
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	sync()
	#
	#	DESCRIPTION:
	#		Perform a synchronize "multiSync" on all the nodes in the cell.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def sync(self):
		"""Perform a "multiSync" on all the nodes in the cell.
        PARMETERS:
        RETURN:
           True if completed or False
        """
		self.debug( __name__ + ".sync(): Called.\n" )
		rc = False
		iter = self.adminClient.connection.queryNames( ObjectName( "WebSphere:*,type=DeploymentManager" ), None ).iterator()
		while iter.hasNext():
			on = iter.next()
			self.logIt( __name__ + ".sync(): " + on.toString() + "\n" )
			self.adminClient.invoke( on, "multiSync", [Boolean( Boolean.TRUE )], ["java.lang.Boolean"] )
			self.logIt( __name__ + ".sync(): Successfully synced all nodes.\n" )
			rc = True
		#Endwhile
		return rc
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
				if re.search( '__doc__',  attr ): continue
				if re.search( '__module__',  attr ): continue
				if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
				if re.search( 'instance', str( getattr( self, attr ) ) ): continue
				if re.search( 'attributes', str( attr ) ):
					items = str( getattr( self, attr ) ).split( ',' )
					for item in items:
						self.debug( __name__ + ".logMySelf(): item=" + str( item ) + "\n" )
					#Endfor
					continue
				#Endif
				if( debugOnly == True ):
					self.debug( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				else:
					self.logIt( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				#Endif
			except AttributeError as e:
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
		#Endif
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	__del__()
	#
	#	DESCRIPTION:
	#		Really closes this instance.
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
	#	run()
	#
	#	DESCRIPTION:
	#		Override the Thread run() method with what we want to do.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		
	##################################################################################
	def run(self):
		"""Override the Thread run() method with what we want to do.
           This method performs the following step:
           1. Stop all runnable processes.
           2. Make new files active.
           3. Configure the MNE as a whole (not the WAS install).  Not the Web Servers (yet).
           4. Configure and install the WAS app. (May involve more threading.)
           5. Run postconfigs on all machines except web servers. (May involve more threading.)
           6. Start the NON-WAS components.  (May involve more threading.)
           7. Run the WAS POST SCRIPT.  (May involve more threading.)
           8. Configure the Web Servers - start to finish.  (May involve more threading.)
           9. Be sure all deployments went OK.  (May involve more threading.)
           10. Perform WAS restarts.
           PARAMETERS:

           RETURN:
		"""
		rVal = False
		#return rVal
		#return True
		time.sleep( 2 )

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
	myLogger	= MyLogger( LOGFILE="/tmp/DeployDomainComponentsThread.log", STDOUT=True, DEBUG=True )
	adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1", cellName='cellA' )
	try:
		myclient	= adminObject.createSOAPDefault()
		results		= adminObject.getResults()
		#adminObject.logResults( results )
	except Exception as e:
		myLogger.logIt( "main(): " + str(e) + "\n" )
		myLogger.logIt( "main(): Unable to connect to the AdminClient().  Make sure that the WebSphere Server Manager is running.\n" )
		raise
	#Endtry

	mycell = "ServicesA"
	mynodeName = "node_ServicesA_01"
	myserver = "as_wdt_01"
	myappName = "DamnSchappettEA"
	mycluster = "cl_ServicesA_a"
	rc = False

	#scope = "Cell=" + str( mycell ) + ":Node=" + str( mynodeName ) + ":Cluster=" + str( mycluster ) + ":Server=" + str( myserver )
	#scope = "Cell=" + str( mycell ) + ":Node=" + str( mynodeName ) + ":Server=" + str( myserver )

	configService 					= ConfigService( adminClient=myclient, logger=myLogger )
	myDeployDomainComponentsThread 	= DeployDomainComponentsThread(adminObject, configService, logger=myLogger)

	threadList = []
	for mythread in range( 0, 3 ):
		current = DeployDomainComponentsThread( adminObject, configService, threadName='thread' + str( mythread ), logger=myLogger )
		threadList.append( current )
		current.start()
	#Endfor

	for mythread in threadList:
		mythread.join()
		myLogger.logIt( "main(): " + str(mythread) + "\n" )
	#Endfor
	
	myDeployDomainComponentsThread.closeMe()
	adminObject.closeMe()
	##################################################################################
	#Enddef
	##################################################################################

######################################################################################
#   End
######################################################################################
if __name__ == "__main__":
	main()

