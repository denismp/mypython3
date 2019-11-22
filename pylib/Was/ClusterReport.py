#!/usr/bin/env jython
######################################################################################
##	ClusterReport.py
##
##	Python module deals with WAS ClusterReport.
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
from pylib.Was.WasObject import *
from pylib.Was.AdminClient import *
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

class ClusterReport():
	"""ClusterReport class that contains cluster data methods."""

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
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               adminClient - instance of the pylib.Was.AdminClient class.
               logger      - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		self.adminClient		= adminClient
		self.logger				= logger
		self.clusterMembers 	= dict()
		self.clusterMgr			= None
		self.clusterData		= None	# array of com.ibm.websphere.management.wlm.ClusterData
		self.getClusterMembers()
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
	#	getClusterNames()
	#
	#	DESCRIPTION:
	#		Get the cluster names
	#
	#	PARAMETERS:
	#		See comments.
	#
	#	RETURN:
	#		A sorted list of the cluster names
	##################################################################################
	def getClusterNames(self):
		"""
		Get the cluster names.
		PARAMETERS:
		    
		RETURN:
		    A sorted list of the cluster names.
		"""
		return sorted( self.clusterMembers.keys() )
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getClusterMemberDataByClusterName()
	#
	#	DESCRIPTION:
	#		Get the com.ibm.websphere.management.wlm.ClusterMemberData for the cluster
	#
	#	PARAMETERS:
	#		See comments.
	#
	#	RETURN:
	#		An array of com.ibm.websphere.management.wlm.ClusterMemberData
	##################################################################################
	def getClusterMemberDataByClusterName(self, clusterName):
		"""
		Get the com.ibm.websphere.management.wlm.ClusterMemberData for the cluster.
		PARAMETERS:
		    
		RETURN:
		    An array of com.ibm.websphere.management.wlm.ClusterMemberData
		"""
		clusterMemberData = self.clusterMembers.get( clusterName )
		return clusterMemberData;
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getServersByClusterName()
	#
	#	DESCRIPTION:
	#		Get the server names
	#
	#	PARAMETERS:
	#		See comments.
	#
	#	RETURN:
	#		A sorted list of the server names
	##################################################################################
	def getServersByClusterName(self, clusterName):
		"""
		Get the server names by cluster name.
		PARAMETERS:
		    
		RETURN:
		    A list of server names.
		"""
		servers = list()
		clusterMemberData = self.clusterMembers.get( clusterName )
		for clusterMember in clusterMemberData:
			servers.append( clusterMember.memberName )
		#Endfor
		if len( servers ) > 0: servers = sorted( servers )
		return servers
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	checkIfClusterExists()
	#
	#	DESCRIPTION:
	#		Check to see if the cluster exists.
	#
	#	PARAMETERS:
	#		See comments.
	#
	#	RETURN:
	#		True or False
	##################################################################################
	def checkIfClusterExists( self, clusterName ):
		"""
		Check to see if the cluster exists.
		PARAMETERS:
		    clusterName - name of the cluster to check.
		    
		RETURN:
		    True or False
		"""
		clusterMemberData = self.clusterMembers.get( clusterName )
		if clusterMemberData is None:
			return False
		else:
			return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getNodesByClusterName()
	#
	#	DESCRIPTION:
	#		Get the node names
	#
	#	PARAMETERS:
	#		See comments.
	#
	#	RETURN:
	#		A sorted list of the node names
	##################################################################################
	def getNodesByClusterName(self, clusterName):
		"""
		Get the server names by cluster name.
		PARAMETERS:
		    
		RETURN:
		    A list of server names.
		"""
		nodes = list()
		clusterMemberData = self.clusterMembers.get( clusterName )
		for clusterMember in clusterMemberData:
			nodes.append( clusterMember.nodeName )
		#Endfor
		if len( nodes ) > 0: nodes = sorted( nodes )
		return nodes
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getServersByClusterNameAndNode()
	#
	#	DESCRIPTION:
	#		Get the cluster names
	#
	#	PARAMETERS:
	#		See comments.
	#
	#	RETURN:
	#		A sorted list of the cluster names
	##################################################################################
	def getServersByClusterNameAndNode(self, clusterName, nodeName):
		"""
		Get the server names by cluster name and node name.
		PARAMETERS:
		    
		RETURN:
		    A list of server names.
		"""
		servers = list()
		clusterMemberData = self.clusterMembers.get( clusterName )
		for clusterMember in clusterMemberData:
			if clusterMember.nodeName == nodeName: servers.append( clusterMember.memberName )
		#Endfor
		if len( servers ) > 0: servers = sorted( servers )
		return servers
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getClusterMembers()
	#
	#	DESCRIPTION:
	#		Get the cluster members dictionary.
	#
	#	PARAMETERS:
	#		See comments.
	#
	#	RETURN:
	#		A dictionary of the com.ibm.websphere.management.wlm.ClusterMemberData[].
	##################################################################################
	def getClusterMembers(self):
		"""
		Get the cluster members list.
		PARAMETERS:
		    
		RETURN:
		    A dictionary of com.ibm.websphere.management.wlm.ClusterMemberData[]
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
		myWas = WasData(logger=self.logger)
		myWas.queryWAS( self.adminClient, query="WebSphere:*,type=ClusterMgr" )

		self.clusterMgr = myWas.objectNames[0]
		#print dir( self.clusterMgr )
		#print type( self.clusterMgr )

		myListener = self.adminClient.registerListener( self.clusterMgr )
		
		#print dir( self.clusterMgr )
		self.clusterData = self.adminClient.invoke( self.clusterMgr, "retrieveClusters", None,  None )
		#print dir( self.clusterData )

		self.clusterMembers = dict()

		for clusterStuff in self.clusterData:
			#print "DEBUG1 clusterStuff=" + str( dir( clusterStuff ) )
			#print clusterStuff
			self.debug( __name__ + ".getClusterMembers(): clusterStuff.clusterName=" + str( clusterStuff.clusterName ) + "\n" )
			#myClusterMembers = clusterStuff.clusterMembers
			self.clusterMembers[clusterStuff.clusterName] = clusterStuff.clusterMembers
		#Endfor
		myWas.closeMe()
		myListener.closeMe()

		#print self.clusterMembers
		return self.clusterMembers
	##################################################################################
	#	Enddef
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
	#	printData()
	#
	#	DESCRIPTION:
	#		Write the cluster data to the given file in a cvs format.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def printData(self,cluster=None,node=None,server=None):
		"""Write the data."""

		#################################################
		#	Set up the header.
		#################################################
		header = "CLUSTER,NODE,SERVER,TYPE,UNIQUE_ID,WMEMBER_NAME,WNODE,WEIGHT"
		try:
			print header

			if cluster is None and node is None and server is None:
				self.debug( __name__ + ".printData(): case 000\n" )
				clusterNames = self.getClusterNames()
				for mycluster in clusterNames:
					ostr = ""
					clusterMemberData = self.getClusterMemberDataByClusterName( mycluster )	
					for clusterMember in clusterMemberData:
						lclusterName = clusterMember.clusterName
						lserver		= clusterMember.memberName
						lnode		= clusterMember.nodeName
						type		= clusterMember.type
						uniqueID	= clusterMember.uniqueID
						wmember		= clusterMember.weightTableEntry.memberName
						wnode		= clusterMember.weightTableEntry.nodeName
						weight		= clusterMember.weightTableEntry.weight
						ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + "," + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight)
						print ostr
					#Endfor
				#Endfor
			elif cluster is None and node is None and server is not None: 
				self.debug( __name__ + ".printData(): case 001\n" )
				clusterNames = self.getClusterNames()
				for mycluster in clusterNames:
					ostr = ""
					clusterMemberData = self.getClusterMemberDataByClusterName( mycluster )	
					for clusterMember in clusterMemberData:
						lclusterName = clusterMember.clusterName
						lserver		= clusterMember.memberName
						lnode		= clusterMember.nodeName
						type		= clusterMember.type
						uniqueID	= clusterMember.uniqueID
						wmember		= clusterMember.weightTableEntry.memberName
						wnode		= clusterMember.weightTableEntry.nodeName
						weight		= clusterMember.weightTableEntry.weight
						if server == clusterMember.memberName:
							ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + "," + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight)
							print ostr
						#Endif
					#Endfor
				#Endfor
			elif cluster is None and node is not None and server is None: 
				self.debug( __name__ + ".printData(): case 010\n" )
				clusterNames = self.getClusterNames()
				clusterNames = self.getClusterNames()
				for mycluster in clusterNames:
					ostr = ""
					clusterMemberData = self.getClusterMemberDataByClusterName( mycluster )	
					for clusterMember in clusterMemberData:
						lclusterName = clusterMember.clusterName
						lserver		= clusterMember.memberName
						lnode		= clusterMember.nodeName
						type		= clusterMember.type
						uniqueID	= clusterMember.uniqueID
						wmember		= clusterMember.weightTableEntry.memberName
						wnode		= clusterMember.weightTableEntry.nodeName
						weight		= clusterMember.weightTableEntry.weight
						if node == clusterMember.nodeName:
							ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + "," + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight)
							print ostr
						#Endif
					#Endfor
				#Endfor
			elif cluster is None and node is not None and server is not None: 
				self.debug( __name__ + ".printData(): case 011\n" )
				clusterNames = self.getClusterNames()
				clusterNames = self.getClusterNames()
				for mycluster in clusterNames:
					ostr = ""
					clusterMemberData = self.getClusterMemberDataByClusterName( mycluster )	
					for clusterMember in clusterMemberData:
						lclusterName = clusterMember.clusterName
						lserver		= clusterMember.memberName
						lnode		= clusterMember.nodeName
						type		= clusterMember.type
						uniqueID	= clusterMember.uniqueID
						wmember		= clusterMember.weightTableEntry.memberName
						wnode		= clusterMember.weightTableEntry.nodeName
						weight		= clusterMember.weightTableEntry.weight
						if server == clusterMember.memberName and node == clusterMember.nodeName:
							ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + "," + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight)
							print ostr
						#Endif
					#Endfor
				#Endfor
			elif cluster is not None and node is None and server is None: 
				self.debug( __name__ + ".printData(): case 100\n" )
				clusterNames = self.getClusterNames()
				ostr = ""
				clusterMemberData = self.getClusterMemberDataByClusterName( cluster )	
				for clusterMember in clusterMemberData:
					lclusterName = clusterMember.clusterName
					lserver		= clusterMember.memberName
					lnode		= clusterMember.nodeName
					type		= clusterMember.type
					uniqueID	= clusterMember.uniqueID
					wmember		= clusterMember.weightTableEntry.memberName
					wnode		= clusterMember.weightTableEntry.nodeName
					weight		= clusterMember.weightTableEntry.weight
					ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + "," + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight)
					print ostr
				#Endfor
			elif cluster is not None and node is None and server is not None: 
				self.debug( __name__ + ".printData(): case 101\n" )
				clusterNames = self.getClusterNames()
				ostr = ""
				clusterMemberData = self.getClusterMemberDataByClusterName( cluster )	
				for clusterMember in clusterMemberData:
					lclusterName = clusterMember.clusterName
					lserver		= clusterMember.memberName
					lnode		= clusterMember.nodeName
					type		= clusterMember.type
					uniqueID	= clusterMember.uniqueID
					wmember		= clusterMember.weightTableEntry.memberName
					wnode		= clusterMember.weightTableEntry.nodeName
					weight		= clusterMember.weightTableEntry.weight
					if server == clusterMember.memberName:
						ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + "," + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight)
						print ostr
					#Endif
				#Endfor
			elif cluster is not None and node is not None and server is None: 
				self.debug( __name__ + ".printData(): case 110\n" )
				clusterNames = self.getClusterNames()
				ostr = ""
				clusterMemberData = self.getClusterMemberDataByClusterName( cluster )	
				for clusterMember in clusterMemberData:
					lclusterName = clusterMember.clusterName
					lserver		= clusterMember.memberName
					lnode		= clusterMember.nodeName
					type		= clusterMember.type
					uniqueID	= clusterMember.uniqueID
					wmember		= clusterMember.weightTableEntry.memberName
					wnode		= clusterMember.weightTableEntry.nodeName
					weight		= clusterMember.weightTableEntry.weight
					if node == clusterMember.nodeName:
						ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + "," + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight)
						print ostr
					#Endif
				#Endfor
			elif cluster is not None and node is not None and server is not None: 
				self.debug( __name__ + ".printData(): case 111\n" )
				#self.debug( __name__ + ".printData(): server=" + str( server ) +  "\n" )
				#self.debug( __name__ + ".printData(): node=" + str( node ) +  "\n" )
				clusterNames = self.getClusterNames()
				ostr = ""
				clusterMemberData = self.getClusterMemberDataByClusterName( cluster )	
				for clusterMember in clusterMemberData:
					lclusterName = clusterMember.clusterName
					lserver		= clusterMember.memberName
					lnode		= clusterMember.nodeName
					type		= clusterMember.type
					uniqueID	= clusterMember.uniqueID
					wmember		= clusterMember.weightTableEntry.memberName
					wnode		= clusterMember.weightTableEntry.nodeName
					weight		= clusterMember.weightTableEntry.weight
					if server == clusterMember.memberName and node == clusterMember.nodeName:
						ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + "," + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight)
						print ostr
					#Endif
				#Endfor
			else:
				self.debug( __name__ + ".printData(): invalid parameter combination\n" )
			#Endif
		except Exception, e:
			self.logIt( __name__ + ".printData(): " + str( e ) + "\n" )
			raise
		#Endtry
	##################################################################################
	#	Enddef
	##################################################################################
	##################################################################################
	#	writeData()
	#
	#	DESCRIPTION:
	#		Write the cluster data to the given file in a cvs format.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def writeData(self,fileName,cluster=None,node=None,server=None):
		"""Write the data."""

		#################################################
		#	Set up the header.
		#################################################
		header = "CLUSTER,NODE,SERVER,TYPE,UNIQUE_ID,WMEMBER_NAME,WNODE,WEIGHT\n"
		try:
			oFH = open( fileName, 'w' )
			oFH.write( header )

			if cluster is None and node is None and server is None:
				clusterNames = self.getClusterNames()
				for mycluster in clusterNames:
					ostr = ""
					clusterMemberData = self.getClusterMemberDataByClusterName( mycluster )	
					for clusterMember in clusterMemberData:
						lclusterName = clusterMember.clusterName
						lserver		= clusterMember.memberName
						lnode		= clusterMember.nodeName
						type		= clusterMember.type
						uniqueID	= clusterMember.uniqueID
						wmember		= clusterMember.weightTableEntry.memberName
						wnode		= clusterMember.weightTableEntry.nodeName
						weight		= clusterMember.weightTableEntry.weight
						ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + ",_" + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight) + "\n"
						#	Write it.
						oFH.write( ostr  )
					#Endfor
				#Endfor
			elif cluster is None and node is None and server is not None: 
				clusterNames = self.getClusterNames()
				for mycluster in clusterNames:
					ostr = ""
					clusterMemberData = self.getClusterMemberDataByClusterName( mycluster )	
					for clusterMember in clusterMemberData:
						lclusterName = clusterMember.clusterName
						lserver		= clusterMember.memberName
						lnode		= clusterMember.nodeName
						type		= clusterMember.type
						uniqueID	= clusterMember.uniqueID
						wmember		= clusterMember.weightTableEntry.memberName
						wnode		= clusterMember.weightTableEntry.nodeName
						weight		= clusterMember.weightTableEntry.weight
						if server == clusterMember.memberName:
							ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + ",_" + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight) + "\n"
							#	Write it.
							oFH.write( ostr  )
						#Endif
					#Endfor
				#Endfor
			elif cluster is None and node is not None and server is None: 
				clusterNames = self.getClusterNames()
				for mycluster in clusterNames:
					ostr = ""
					clusterMemberData = self.getClusterMemberDataByClusterName( mycluster )	
					for clusterMember in clusterMemberData:
						lclusterName = clusterMember.clusterName
						lserver		= clusterMember.memberName
						lnode		= clusterMember.nodeName
						type		= clusterMember.type
						uniqueID	= clusterMember.uniqueID
						wmember		= clusterMember.weightTableEntry.memberName
						wnode		= clusterMember.weightTableEntry.nodeName
						weight		= clusterMember.weightTableEntry.weight
						if node == clusterMember.nodeName:
							ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + ",_" + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight) + "\n"
							#	Write it.
							oFH.write( ostr  )
						#Endif
					#Endfor
				#Endfor
			elif cluster is None and node is not None and server is not None: 
				clusterNames = self.getClusterNames()
				for mycluster in clusterNames:
					ostr = ""
					clusterMemberData = self.getClusterMemberDataByClusterName( mycluster )	
					for clusterMember in clusterMemberData:
						lclusterName = clusterMember.clusterName
						lserver		= clusterMember.memberName
						lnode		= clusterMember.nodeName
						type		= clusterMember.type
						uniqueID	= clusterMember.uniqueID
						wmember		= clusterMember.weightTableEntry.memberName
						wnode		= clusterMember.weightTableEntry.nodeName
						weight		= clusterMember.weightTableEntry.weight
						if server == clusterMember.memberName and node == clusterMember.nodeName:
							ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + ",_" + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight) + "\n"
							#	Write it.
							oFH.write( ostr  )
						#Endif
					#Endfor
				#Endfor
			elif cluster is not None and node is None and server is None: 
				ostr = ""
				clusterMemberData = self.getClusterMemberDataByClusterName( cluster )	
				for clusterMember in clusterMemberData:
					lclusterName = clusterMember.clusterName
					lserver		= clusterMember.memberName
					lnode		= clusterMember.nodeName
					type		= clusterMember.type
					uniqueID	= clusterMember.uniqueID
					wmember		= clusterMember.weightTableEntry.memberName
					wnode		= clusterMember.weightTableEntry.nodeName
					weight		= clusterMember.weightTableEntry.weight
					ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + ",_" + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight) + "\n"
					#	Write it.
					oFH.write( ostr  )
				#Endfor
			elif cluster is not None and node is None and server is not None: 
				ostr = ""
				clusterMemberData = self.getClusterMemberDataByClusterName( cluster )	
				for clusterMember in clusterMemberData:
					lclusterName = clusterMember.clusterName
					lserver		= clusterMember.memberName
					lnode		= clusterMember.nodeName
					type		= clusterMember.type
					uniqueID	= clusterMember.uniqueID
					wmember		= clusterMember.weightTableEntry.memberName
					wnode		= clusterMember.weightTableEntry.nodeName
					weight		= clusterMember.weightTableEntry.weight
					if server == clusterMember.memberName:
						ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + ",_" + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight) + "\n"
						#	Write it.
						oFH.write( ostr  )
					#Endif
				#Endfor
			elif cluster is not None and node is not None and server is None: 
				ostr = ""
				clusterMemberData = self.getClusterMemberDataByClusterName( cluster )	
				for clusterMember in clusterMemberData:
					lclusterName = clusterMember.clusterName
					lserver		= clusterMember.memberName
					lnode		= clusterMember.nodeName
					type		= clusterMember.type
					uniqueID	= clusterMember.uniqueID
					wmember		= clusterMember.weightTableEntry.memberName
					wnode		= clusterMember.weightTableEntry.nodeName
					weight		= clusterMember.weightTableEntry.weight
					if node == clusterMember.nodeName:
						ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + ",_" + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight) + "\n"
						#	Write it.
						oFH.write( ostr  )
					#Endif
				#Endfor
			elif cluster is not None and node is not None and server is not None: 
				ostr = ""
				clusterMemberData = self.getClusterMemberDataByClusterName( cluster )	
				for clusterMember in clusterMemberData:
					lclusterName = clusterMember.clusterName
					lserver		= clusterMember.memberName
					lnode		= clusterMember.nodeName
					type		= clusterMember.type
					uniqueID	= clusterMember.uniqueID
					wmember		= clusterMember.weightTableEntry.memberName
					wnode		= clusterMember.weightTableEntry.nodeName
					weight		= clusterMember.weightTableEntry.weight
					if server == clusterMember.memberName and node == clusterMember.nodeName:
						ostr		= str( lclusterName ) + "," + str( lnode ) + "," + str( lserver ) + "," + str(type) + ",_" + str(uniqueID) + "," + str(wmember) + "," + str(wnode) + "," + str(weight) + "\n"
						#	Write it.
						oFH.write( ostr  )
					#Endif
				#Endfor
			else:
				self.debug( __name__ + ".writeData(): invalid parameter combination\n" )
			#Endif
			oFH.close()
		except Exception, e:
			self.logIt( __name__ + ".writeData(): " + str( e ) + "\n" )
			raise
		#Endtry
	##################################################################################
	#	Enddef
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
	myLogger	= MyLogger( LOGFILE="/tmp/ClusterReport.log", STDOUT=True, DEBUG=True )
	#adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1" )
	adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1", cellName='cellA' )
	try:
		myclient	= adminObject.createSOAPDefault()
		results		= adminObject.getResults()
		#adminObject.logResults( results )
	except Exception, e:
		myLogger.logIt( "main(): " + str(e) + "\n" )
		myLogger.logIt( "main(): Unable to connect to the AdminClient().  Make sure that the WebSphere Server Manager is running.\n" )
		raise
	#Endtry
	myClusterReport = ClusterReport(adminObject, logger=myLogger)

	for clusterName,clusterMemberData in myClusterReport.clusterMembers.items():
		myLogger.logIt( "main(): clusterName=" + str( clusterName ) + "\n" )
		myLogger.logIt( "main(): clusterMemberData=" + str( clusterMemberData ) + "\n" )
		#print clusterName
		#print clusterMemberData
	#Endfor
	clusterMemberKeys =  myClusterReport.clusterMembers.keys()
	#for clusterName in myClusterReport.clusterMembers.keys():
	for clusterName in sorted( clusterMemberKeys ):
		clusterMemberData = myClusterReport.clusterMembers.get( clusterName )
		for clusterMember in clusterMemberData:
			myLogger.logIt( "main(): clusterMember.clusterName=" + str( clusterMember.clusterName ) + "\n" )
			myLogger.logIt( "main(): clusterMember.clusterObjectName=" + str( clusterMember.clusterObjectName ) + "\n" )
			myLogger.logIt( "main(): clusterMember.memberName=" + str( clusterMember.memberName ) + "\n" )
			myLogger.logIt( "main(): clusterMember.memberObjectName=" + str( clusterMember.memberObjectName ) + "\n" )
			myLogger.logIt( "main(): clusterMember.nodeName=" + str( clusterMember.nodeName ) + "\n" )
			myLogger.logIt( "main(): clusterMember.type=" + str( clusterMember.type ) + "\n" )
			myLogger.logIt( "main(): clusterMember.uniqueID=" + str( clusterMember.uniqueID ) + "\n" )
			myLogger.logIt( "main(): clusterMember.weightTableEntry.memberName=" + str( clusterMember.weightTableEntry.memberName ) + "\n" )
			myLogger.logIt( "main(): clusterMember.weightTableEntry.nodeName=" + str( clusterMember.weightTableEntry.nodeName ) + "\n" )
			myLogger.logIt( "main(): clusterMember.weightTableEntry.weight=" + str( clusterMember.weightTableEntry.weight ) + "\n" )
			myLogger.logIt( "main(): \n" )
		#Endfor
	#Endfor

	clusterNames = myClusterReport.getClusterNames()
	print clusterNames
	for clusterName in clusterNames:
		servers = myClusterReport.getServersByClusterName( clusterName )
		for server in servers:
			nodes = myClusterReport.getNodesByClusterName( clusterName )
			for node in nodes:
				myLogger.logIt( "main(): clusterName=" + str( clusterName ) + "\n" )
				myLogger.logIt( "main(): server=" + str( server ) + "\n" )
				myLogger.logIt( "main(): node=" + str( node ) + "\n" )
			#Endfor
		#Endfor
		nodes = myClusterReport.getNodesByClusterName( clusterName )
		for node in nodes:
			myservers = myClusterReport.getServersByClusterNameAndNode( clusterName, node )
			for server in myservers:
				myLogger.logIt( "main(): clusterName=" + str( clusterName ) + "\n" )
				myLogger.logIt( "main(): server=" + str( server ) + "\n" )
				myLogger.logIt( "main(): node=" + str( node ) + "\n" )
			#Endfor
		#Endfor
		clusterMemberData = myClusterReport.getClusterMemberDataByClusterName( clusterName )
		myLogger.logIt( "main(): clusterMemberData for " + str(clusterName) + " = " + str( clusterMemberData ) + "\n" )
	#Endfor
	myClusterReport.writeData( "/nfs/home4/dmpapp/appd4ec/tmp/denis.csv" )
	myClusterReport.printData()
	myClusterReport.closeMe()
	adminObject.closeMe()
	##################################################################################
	#Enddef
	##################################################################################

######################################################################################
#   End
######################################################################################
if __name__ == "__main__":
	main()

