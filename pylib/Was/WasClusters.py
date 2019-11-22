#!/usr/bin/env jython
######################################################################################
##	WasClusters.py
##
##	Python module deals with WAS WasClusters.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	11/23/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.AdminClient import *
from pylib.Was.WasData import *
from pylib.Was.NotificationListener import *
from java.lang import NullPointerException
from java.lang import NoClassDefFoundError
from javax.management import InstanceNotFoundException
from javax.management import MalformedObjectNameException
from javax.management import ObjectName

try:
	from com.dmp.was.admin.service import WASNotificationListener
except ImportError, ie:
	print "Unable to import the WASNotificationListener.  Please verify the CLASSPATH."
	exit( 1 )
except NoClassDefFoundError, nce:
	print "Unable to import the WASNotificationListener.  Most likely you are not on a WebSphere host. " + str( nce )
	exit( 1 )
#Endtry
import com.ibm.websphere.security.WebSphereRuntimePermission as WebSphereRuntimePermission
import com.ibm.websphere.security.auth.WSLoginFailedException as WSLoginFailedException
import com.ibm.ws.security.util.InvalidPasswordDecodingException as InvalidPasswordDecodingException
import com.ibm.websphere.management.exception.ConnectorException as ConnectorException

class WasClusters( WasData ):
	"""WasClusters class that contains ClusterDataMember's methods."""

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
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               logger      - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		self.logger				= logger
		WasData.__init__( self )
		self.clusterMembers		= list()
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
				if( debugOnly == True ):
					self.debug( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				else:
					self.logIt( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				#Endif
			except AttributeError, e:
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

	#######################################################
	#	getClusterMembers()
	#
	#	DESCRIPTION:
	#		Get the cluster members list.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		A list of the com.ibm.websphere.management.wlm.ClusterMemberData.
	#######################################################
	def getClusterMembers(self,myclient):
		"""
		Get the cluster members list.
		PARAMETERS:
		    myclient - com.ibm.websphere.management.AdminClient
		RETURN:
		    com.ibm.websphere.management.wlm.ClusterMemberData[]
		"""
		##########################################################################
		#Need to somthing like the following to get the ClusterData[]:
		#retrieveClusters()
		#       Retrieve an array of ClusterData objects which include 
		#		information such as the cluster name, the JMX object name, etc.
		#
		#  The Notification handler is in pylib.Was.NotificationListener
		#
		#String opName = "launchProcess"; 
		#String signature[] = { "java.lang.String" }; 
		#Object params[] = { "MyServer" }; 
		#try 
		#{ 
		#   adminClient.invoke(nodeAgent, opName, params, signature); 
		#} 
		#catch (Exception e) 
		#	{ 
		#   System.out.println("Exception invoking launchProcess: " + e); 
		#}
		#adminClient.addNotificationListener(nodeAgent, this, null, null);
		#
		#public void handleNotification(Notification n, Object handback) 
		#{ 
		#   System.out.println("******************************************"); 
		#   System.out.println("* Notification received at "  
		#	  + new Date().toString()); 
		#   System.out.println("* type = " + n.getType()); 
		#   System.out.println("* message = " + n.getMessage()); 
		#   System.out.println("* source = " + n.getSource()); 
		#   System.out.println("* seqNum = "  
		#	  + Long.toString(n.getSequenceNumber())); 
		#   System.out.println("* timeStamp = " + new Date(n.getTimeStamp())); 
		#   System.out.println("* userData = " + n.getUserData()); 
		#   System.out.println("*******************************************"); 
		#}
		##########################################################################
		myNotifier	= NotificationListener()
		myWas = WasData(logger=self.logger)
		myWas.queryWAS( myclient, query="WebSphere:*,type=ClusterMgr" )

		clusterMgr = myWas.objectNames[0]
		#print dir( clusterMgr )
		myNotifier.registerNotificationListener( myclient, clusterMgr, myNotifier, None, None )
		
		clusterData = myclient.invoke( clusterMgr, "retrieveClusters", None,  None )
		memberName = None
		self.clusterMembers = list()
		for clusterStuff in clusterData:
			#print "DEBUG1 clusterStuff=" + str( dir( clusterStuff ) )
			#self.debug( __name__ + ".getClusterMembers(): ClusterName=" + str( clusterStuff.clusterName ) + "\n" )
			myClusterMembers = clusterStuff.clusterMembers
			for clusterMember in myClusterMembers:
				#print dir( clusterMember )
				#print "DEBUG2 clusterMember=" + str( dir( clusterMember ) )
				#print "DEBUG"
				self.clusterMembers.append( clusterMember )
				#memberName = clusterMember.memberName
				#print memberName
			#Endif
		#Endif
		myWas.closeMe()
		return self.clusterMembers
	#######################################################
	#	Enddef
	#######################################################

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

######################################################################################
#Endclass
######################################################################################

#########################################################################
#	For testing.
#########################################################################
def main():
	myLogger	= MyLogger( LOGFILE="/tmp/WasClusters.log", STDOUT=True, DEBUG=True )
	adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1" )
	try:
		myclient	= adminObject.createSOAPDefault()
		results		= adminObject.getResults()
		adminObject.logResults( results )
		myClusterObject = WasClusters(logger=myLogger)
		clusterMembers = myClusterObject.getClusterMembers( myclient )
		print dir( myClusterObject.clusterMembers )
		for clusterMember in clusterMembers:
			#print dir( clusterMember )
			print clusterMember.clusterName
			print clusterMember.memberName
			print clusterMember.type
			print clusterMember.nodeName
			print clusterMember.uniqueID
			print clusterMember.clusterObjectName.toString()
			print clusterMember.weightTableEntry.memberName
			print clusterMember.weightTableEntry.weight
			print clusterMember.weightTableEntry.nodeName
		#Endif
		adminObject.closeMe()
	except:
		myLogger.logIt( "main(): Unable to connect to the AdminClient().  Make sure that the WebSphere Server Manager is running.\n" )
		raise
	#Endfi
	##################################################################################
	#Enddef
	##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
	main()

