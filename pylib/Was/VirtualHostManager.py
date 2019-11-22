#!/usr/bin/env jython
######################################################################################
##	VirtualHostManager.py
##
##	Python module replaces some of the functions in the 
##	/nfs/dist/dmp/amp/wdt/_cluster.jacl 
##	file and makes virtual host management object oriented.
##
##	Most likely the methods 
##	addVirtualHostWithAliasesList(self, cellName, destVhost, aliasList) 
##	and 
##	createVirtualHostWithAliasesList(self, cellName, destVhost, aliasList) 
##	will be the most used of the module.
##
##	There is a self.fast instance variable that is defaulted to False.  When this 
##	variable is false, then the module performs WebSphere JMX calls to verify whether 
##	a host alias exists or not.  If you set the self.fast variable to True, you risk 
##	putting duplicate host aliases in the VirtualHost tables in WebSphere.
##
##	The two methods mentioned above use the fast method, but they ensure no 
##	duplicates.  The destination virtual host is deleted and recreated and then the 
##	host aliases are added.  This reduces the execution time from minutes to seconds.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	12/21/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.AdminClient import *
from pylib.Was.WasData import *
from pylib.Was.WasObject import *
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

import com.ibm.websphere.security.WebSphereRuntimePermission as WebSphereRuntimePermission
import com.ibm.websphere.security.auth.WSLoginFailedException as WSLoginFailedException
import com.ibm.ws.security.util.InvalidPasswordDecodingException as InvalidPasswordDecodingException
import com.ibm.websphere.management.exception.ConnectorException as ConnectorException

class VirtualHostManager():
	"""
    VirtualHostManager class that contains VirtualHost management methods.
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
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               adminClient   - instance of the pylib.Was.AdminClient class.
               configService - instance of the pylib.Was.ConfigService class.
               logger        - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		self.adminClient		= adminClient
		self.configService		= configService
		self.logger				= logger
		self.aliasNamesList		= list()
		self.hostAliasesList	= list()
		self.lastVirtualHost	= None
		self.lastvHostObject	= None
		self.fast				= False  # If True, turns of checking for existing host aliases.
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
		#self.configService.closeMe()
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
	#	getVirtualHostObjectName()
	#
	#	DESCRIPTION:
	#		Get the VirtualHost ObjectName
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getVirtualHostObjectName(self,vhName):
		"""Get the VirtualHost ObjectName.
		   PARAMETERS:
		       vhName -- name of the virtual host.
		   RETURN:
		       The ObjectName of the VirtualHost.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getVirtualHostObjectName(): called.\n" )
		self.debug( __name__ + ".getVirtualHostObjectName(): vhName=" + str( vhName ) + ".\n" )
		self.debug( __name__ + ".getVirtualHostObjectName(): lastVirtualHost=" + str( self.lastVirtualHost ) + ".\n" )

		##############################################
		#	If the vhName is the same as the last call
		#	just return the lastvHostObject to avoid
		#	the trip back to the WebSphere process.
		##############################################
		if self.lastVirtualHost	== vhName and self.lastvHostObject is not None:
			return self.lastvHostObject
		else:
			self.lastVirtualHost = vhName

		################################################################
		#	Query for the virtual host name.
		################################################################
		myQuery = "VirtualHost=" + str( vhName )
		#self.debug( __name__ + ".getVirtualHostObjectName(): myQuery=" + str( myQuery ) + "\n" )
		#myresults = self.configService.resolve( self.configService.session, myQuery )
		myresults = self.configService.resolveObjectName( myQuery )

		#self.debug( __name__ + ".getVirtualHostObjectName(): myresults=" + str( myresults ) + "\n" )
		#self.debug( __name__ + ".getVirtualHostObjectName(): length of myresults is " + str( len( myresults ) ) + "\n" )

		###############################################################
		#	See if we found the virtual host.
		###############################################################
		if len( myresults ) == 1:
			################################
			#	This is most likely case.
			################################
			myHostObjectName = myresults[0]
			#self.debug( __name__ + ".getVirtualHostObjectName(): myHostObjectName=" + str( myHostObjectName ) + "\n" )
			hostFound = True
		else:
			###########################################
			#	We did not find the virtual host name.
			###########################################
			self.debug( __name__ + ".getVirtualHostObjectName(): No virtual hosts found.\n" )
			hostFound = False
		#Endif

		#######################################################
		#	Return None if we didn't find the virtual host.
		#######################################################
		if not hostFound: 
			self.lastvHostObject = None
			return None
		else:
			self.lastvHostObject = myresults[0]
			return myresults[0]
		#Endif
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getVirtualHostNamesList()
	#
	#	DESCRIPTION:
	#		Get the VirtualHost names list.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getVirtualHostNamesList(self,cell):
		"""Get the VirtualHost names list.
		   PARAMETERS:
		       cell - the cell name.
		   RETURN:
		       The list of VirtualHost's
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getVirtualHostNamesList(): called.\n" )
		self.debug( __name__ + ".getVirtualHostNamesList(): cell=" + str( cell ) + ".\n" )

		myQuery = "Cell=" + str( cell )
		myList = self.configService.getList( "VirtualHost", query=myQuery )
		return myList
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	checkVirtualHost()
	#
	#	DESCRIPTION:
	#		Get the VirtualHost names list.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def checkVirtualHost(self,cell,virtualHost):
		"""Get the VirtualHost names list.
		   PARAMETERS:
		       cell        - the cell name.
			   virtualHost - name of the virtualHost.
		   RETURN:
		       True if the virtual host exists.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".checkVirtualHost(): called.\n" )
		self.debug( __name__ + ".checkVirtualHost(): cell=" + str( cell ) + ".\n" )

		myQuery = "Cell=" + str( cell )
		myList = self.configService.getList( "VirtualHost", query=myQuery )
		for host in myList:
			if host == virtualHost: return True
		#Endfor
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getVirtualHostAliasNamesList()
	#
	#	DESCRIPTION:
	#		Get the VirtualHost HostAlias names list.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getVirtualHostAliasNamesList(self,virtualHostName):
		"""Get the VirtualHost HostAlias names list.
		   PARAMETERS:
		       cell            - the cell name.
		       virtualHostName - the VirtualHost name.
		   RETURN:
		       The list of HostAlias's
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getVirtualHostAliasNamesList(): called.\n" )
		self.debug( __name__ + ".getVirtualHostAliasNamesList(): virtualHostName=" + str( virtualHostName ) + ".\n" )

		#self.aliasNamesList = list()
		aList = list()
		#myQuery = "Cell=" + str( cell ) + ":VirtualHost=" + str( virtualHostName )
		#myQuery = "VirtualHost=" + str( virtualHostName )
		#myList = self.configService.getList( "HostAlias", query=myQuery )
		#myList = self.configService.getList( "aliases", query=myQuery, attributeName="hostname" )

		#self.debug( __name__ + ".getVirtualHostAliasNamesList(): self.lastVirtualHost=" + str( self.lastVirtualHost ) + ".\n" )
		#self.debug( __name__ + ".getVirtualHostAliasNamesList(): self.aliasNamesList=" + str( self.aliasNamesList ) + ".\n" )
		#self.debug( __name__ + ".getVirtualHostAliasNamesList(): self.hostAliasesList=" + str( self.hostAliasesList ) + ".\n" )
		self.hostAliasesList = self.getAliasesList( virtualHostName )
		for hostAliasObjectName in self.hostAliasesList:
			#self.debug( __name__ + ".getVirtualAliasNamesList(): hostAliasObjectName=" + str( hostAliasObjectName ) + "\n" )
			hostname = self.configService.getAttribute( self.configService.session, hostAliasObjectName, "hostname" )
			port = self.configService.getAttribute( self.configService.session, hostAliasObjectName, "port" )
			#self.debug( __name__ + ".getVirtualAliasNamesList(): hostname=" + str( hostname ) + "\n" )
			#self.debug( __name__ + ".getVirtualAliasNamesList(): port=" + str( port ) + "\n" )
			#self.aliasNamesList.append( { hostname: port } )
			aList.append( { hostname: port } )
		#Endfor
		#return self.aliasNamesList
		self.debug( __name__ + ".getVirtualAliasNamesList(): aList=" + str( aList ) + "\n" )
		myutils = MyUtils()
		aList = myutils.uniquer( aList, self.uniqueID )
		self.debug( __name__ + ".getVirtualAliasNamesList(): aList=" + str( aList ) + "\n" )
		self.aliasNamesList = aList

		return aList
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAliasesList()
	#
	#	DESCRIPTION:
	#		Get the VirtualHost.aliases
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAliasesList(self,vhName):
		"""Get the VirtualHost.aliases list.
		   PARAMETERS:
		       vhName -- name of the virtual host.
		   RETURN:
		       The list of VirtualHost.aliases
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getAliasesList(): called.\n" )
		self.debug( __name__ + ".getAliasesList(): vhName=" + str( vhName ) + ".\n" )

		################################################################
		#	Query for the virtual host name.
		################################################################
		myHostObjectName = self.getVirtualHostObjectName( vhName )

		###########################################################
		#	Return None if we didn't find the virtual host object.
		###########################################################
		if myHostObjectName is None: return None

		################################################################
		#	Get the hostAliases ObjectName for the VirtualHost from the
		#	myHostObjectName.
		################################################################
		attributes = array( ['aliases'], String )
		hostAliasesAttributes = self.configService.getAttributes( self.configService.session, myHostObjectName, attributes, False )

		################################################################
		#self.debug( __name__ + ".getAliasesList(): hostAliasesAttributes=" + str( hostAliasesAttributes ) + "\n" )
		#self.debug( __name__ + ".getAliasesList(): hostAliasesAttributes length=" + str( len( hostAliasesAttributes ) ) + "\n" )
		#self.debug( __name__ + ".getAliasesList(): hostAliasesAttributes type=" + str( type( hostAliasesAttributes ) ) + "\n" )
		#for alias in hostAliasesAttributes:
		#	self.debug( __name__ + ".getAliasesList(): alias=" + str( alias ) + "\n" )
		##Endfor
		################################################################

		##############################################################################
		#	Get the hostAliasesList from the hostAliases ObjectName.
		##############################################################################
		self.hostAliasesList = self.configService.configServiceHelper.getAttributeValue( hostAliasesAttributes, "aliases" )
		for myObject in self.hostAliasesList:
			self.debug( __name__ + ".getAliasesList(): myObject=" + str( myObject ) + "\n" )
		#Endfor
		return self.hostAliasesList
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	checkVirtualHostAlias()
	#
	#	DESCRIPTION:
	#		Check to see if the virtual host entry exists in WebSphere.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def checkVirtualHostAlias(self,vhName,aliasHost,aliasPort):
		"""Check to see if the virtual host entry exists in WebSphere.
		   PARAMETERS:
		       vhName -- name of the virtual host.
		       aliasHost -- real name of the host.
		       aliasPort -- host port.
		   RETURN:
		       True if the virtual host and port exist.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		aList = list()
		self.debug( __name__ + ".checkVirtualHostAlias(): called.\n" )
		self.debug( __name__ + ".checkVirtualHostAlias(): vhName=" + str( vhName ) + ".\n" )
		self.debug( __name__ + ".checkVirtualHostAlias(): aliasHost=" + str( aliasHost ) + ".\n" )
		self.debug( __name__ + ".checkVirtualHostAlias(): aliasPort=" + str( aliasPort ) + ".\n" )

		##################################################
		#	If the fast flag is set skip checking.
		##################################################
		if self.fast: return False

		###########################################################################
		#	Get the hostname and port from each hostAliasObjectName in the hostAliasesList.
		###########################################################################
		#aList = self.getVirtualHostAliasNamesList( vhName )
		#self.debug( __name__ + ".checkVirtualHostAlias(): aList=" + str( aList ) + ".\n" )
		#for item in aList:
		#	self.debug( __name__ + ".checkVirtualHostAlias(): item=" + str( item ) + ".\n" )
		#	for hostname in item:
		#		port = item.get( hostname )
		#		self.debug( __name__ + ".checkVirtualHostAlias(): hostname=" + str( hostname ) + ":" + "port=" + str( port ) +  "\n" )
		#		if aliasHost == hostname and aliasPort == port:
		#			# Found it.
		#			self.debug( __name__ + ".checkVirtualHostAlias(): return True.\n" )
		#			return True
		#	#Endfor
		##Endfor
		hostAliasesList = self.getAliasesList( vhName )
		for hostAliasObjectName in hostAliasesList:
			#self.debug( __name__ + ".checkVirtualHostAlias(): hostAliasObjectName=" + str( hostAliasObjectName ) + "\n" )
			hostname = self.configService.getAttribute( self.configService.session, hostAliasObjectName, "hostname" )
			#self.debug( __name__ + ".checkVirtualHostAlias(): hostname=" + str( hostname ) + "\n" )
			port = self.configService.getAttribute( self.configService.session, hostAliasObjectName, "port" )
			#self.debug( __name__ + ".checkVirtualHostAlias(): port=" + str( port ) + "\n" )
			if aliasHost == hostname and aliasPort == port:
				# Found it.
				return True
		#Endfor

		#self.debug( __name__ + ".checkVirtualHostAlias(): return False.\n" )
		return False	
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	deleteVirtualHostAlias()
	#
	#	DESCRIPTION:
	#		Check to see if the virtual host entry exists in WebSphere.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deleteVirtualHostAlias(self,vhName,aliasHost,aliasPort):
		"""Check to see if the virtual host entry exists in WebSphere.
		   PARAMETERS:
		       vhName -- name of the virtual host.
		       aliasHost -- real name of the host.
		       aliasPort -- host port.
		   RETURN:
		       True if the virtual host and port exist.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".deleteVirtualHostAlias(): called.\n" )
		self.debug( __name__ + ".deleteVirtualHostAlias(): vhName=" + str( vhName ) + ".\n" )
		self.debug( __name__ + ".deleteVirtualHostAlias(): aliasHost=" + str( aliasHost ) + ".\n" )
		self.debug( __name__ + ".deleteVirtualHostAlias(): aliasPort=" + str( aliasPort ) + ".\n" )

		###########################################################################
		#	Get the hostname and port from each hostAliasObjectName in the hostAliasesList.
		###########################################################################
		hostAliasesList = self.getAliasesList( vhName )
		for hostAliasObjectName in hostAliasesList:
			#self.debug( __name__ + ".deleteVirtualHostAlias(): hostAliasObjectName=" + str( hostAliasObjectName ) + "\n" )
			hostname = self.configService.getAttribute( self.configService.session, hostAliasObjectName, "hostname" )
			#self.debug( __name__ + ".deleteVirtualHostAlias(): hostname=" + str( hostname ) + "\n" )
			port = self.configService.getAttribute( self.configService.session, hostAliasObjectName, "port" )
			#self.debug( __name__ + ".deleteVirtualHostAlias(): port=" + str( port ) + "\n" )
			if aliasHost == hostname and aliasPort == port:
				# Delete the host alias.
				self.configService.deleteConfigData( self.configService.session, hostAliasObjectName )
				return True
		#Endfor

		return False	
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	addVirtualHostAlias()
	#
	#	DESCRIPTION:
	#		Adds a VirtualHost alias to the VirtualHost.aliases list in WebSphere.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def addVirtualHostAlias(self,vhName,aliasHost,aliasPort):
		"""Adds a VirtualHost alias to the VirtualHost.aliases list in WebSphere.
		   PARAMETERS:
		       vhName -- name of the virtual host.
		       aliasHost -- alias host name.
		       aliasPort -- alias port.
		   RETURN:
		       True if successful or False
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".addVirtualHostAlias(): called.\n" )
		self.debug( __name__ + ".addVirtualHostAlias(): vhName=" + str( vhName ) + ".\n" )
		self.debug( __name__ + ".addVirtualHostAlias(): aliasHost=" + str( aliasHost ) + ".\n" )
		self.debug( __name__ + ".addVirtualHostAlias(): aliasPort=" + str( aliasPort ) + ".\n" )
		if not self.checkVirtualHostAlias(vhName,aliasHost,aliasPort):
			myHostObjectName = self.getVirtualHostObjectName( vhName )
			attr1 = Attribute( "hostname", aliasHost )
			attr2 = Attribute( "port", aliasPort )
			attrList = AttributeList()
			attrList.add( attr1 )
			attrList.add( attr2 )
			result = self.configService.createConfigData( self.configService.session, myHostObjectName, "aliases", "HostAlias", attrList )
			#self.debug( __name__ + ".addVirtualHostAlias(): result=" + str( result ) + ".\n" )
			# Clear teh lastVirtualHost name.
			self.lastVirtualHost = None
			if result is not None: 
				return True
			else:
				return False
		#Endif
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	addVirtualHost()
	#
	#	DESCRIPTION:
	#		Adds a VirtualHost to WebSphere.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def addVirtualHost(self,cellName,vhName):
		"""Adds a VirtualHost to WebSphere.
		   PARAMETERS:
		       cellname -- name of the WebSphere cell.
		       vhName   -- name of the virtual host.
		   RETURN:
		       True if successful or False
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".addVirtualHost(): called.\n" )
		self.debug( __name__ + ".addVirtualHost(): vhName=" + str( vhName ) + ".\n" )

		###########################################################
		#	First check to see if the virtual host already exists.
		###########################################################
		#query = "Cell=" + str( cellName ) + ":VirtualHost=" + str( vhName )
		vObject = self.getVirtualHostObjectName( vhName )
		self.debug( __name__ + ".addVirtualHost(): vObject=" + str( vObject ) + ".\n" )
		if vObject is None:
			############################################################
			#	The virtual host does not exist in the cell, so add it.
			############################################################
			query = "Cell=" + str( cellName )
			cellObjects = self.configService.resolveObjectName( query )
			#self.debug( __name__ + ".addVirtualHost(): cellObjects=" + str( cellObjects ) + ".\n" )
			#self.debug( __name__ + ".addVirtualHost(): len(cellObjects)=" + str( len( cellObjects ) ) + ".\n" )
			if len( cellObjects ) > 0:
				attr1		= Attribute( "name", vhName )
				attrList	= AttributeList()
				attrList.add( attr1 )
				result		= self.configService.createConfigData( self.configService.session, cellObjects[0], "VirtualHost", "VirtualHost", attrList )
				#self.debug( __name__ + ".addVirtualHost(): result=" + str( result ) + ".\n" )
				if result is not None: return True
			else:
				self.logIt( __name__ + ".addVirtualHost(): Unable to resolve" + str( query ) + ".\n" )
			#Endif
		else:
			#####################################################
			#	Virtual host exists in the cell so return happy.
			#####################################################
			return True
		#Endif
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	deleteVirtualHost()
	#
	#	DESCRIPTION:
	#		Deletes a VirtualHost from WebSphere.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deleteVirtualHost(self,vhName):
		"""Deletes a VirtualHost from WebSphere.
		   PARAMETERS:
		       vhName   -- name of the virtual host.
		   RETURN:
		       True if successful or False
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".deleteVirtualHost(): called.\n" )
		self.debug( __name__ + ".deleteVirtualHost(): vhName=" + str( vhName ) + ".\n" )

		###########################################################
		#	First check to see if the virtual host already exists.
		###########################################################
		vObject = self.getVirtualHostObjectName( vhName )
		#self.debug( __name__ + ".deleteVirtualHost(): vObject=" + str( vObject ) + ".\n" )
		if vObject is not None:
			self.configService.deleteConfigData( self.configService.session, vObject )
		else:
			#############################################################
			#	Virtual host does not exist in the cell so return happy.
			#############################################################
			return True
		#Endif
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	copyClean()
	#
	#	DESCRIPTION:
	#		Copy the host aliases from the sourceVhost to the destVhost.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def copyClean(self,cellName,sourceVhost,destVhost):
		"""Copy the host aliases from the sourceVhost to the destVhost.
		   If the destVhost exists, it will be deleted and recreated.
		   WARNING:  This is a destructive copy.
		   PARAMETERS:
		       cellName    -- name of the cell.
		       sourceVhost -- name of the source virtual host.
		       destVhost   -- name of the destination virtual host.
		   RETURN:
		       True if successful.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".copyClean(): called.\n" )
		self.debug( __name__ + ".copyClean(): cellName=" + str( cellName ) + ".\n" )
		self.debug( __name__ + ".copyClean(): sourceVhost=" + str( sourceVhost ) + ".\n" )
		self.debug( __name__ + ".copyClean(): destVhost=" + str( destVhost ) + ".\n" )
		rc = self.deleteVirtualHost( destVhost )
		rc = self.copy(cellName,sourceVhost,destVhost,fast=True)

		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	copy()
	#
	#	DESCRIPTION:
	#		Copy the host aliases from the sourceVhost to the destVhost.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def copy(self,cellName,sourceVhost,destVhost,fast=False):
		"""Copy the host aliases from the sourceVhost to the destVhost.
		   If the destVhost does not exist, it will be created.
		   PARAMETERS:
		       cellName    -- name of the cell.
		       sourceVhost -- name of the source virtual host.
		       destVhost   -- name of the destination virtual host that may or may not exist.
		       fast        -- don't check if the aliases exists.  Do it fast.  This can create dups.
		   RETURN:
		       True if successful.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".copy(): called.\n" )
		self.debug( __name__ + ".copy(): cellName=" + str( cellName ) + ".\n" )
		self.debug( __name__ + ".copy(): sourceVhost=" + str( sourceVhost ) + ".\n" )
		self.debug( __name__ + ".copy(): destVhost=" + str( destVhost ) + ".\n" )
		self.debug( __name__ + ".copy(): fast=" + str( fast ) + ".\n" )

		###########################
		#	Set the fast mode.
		###########################
		self.fast = fast

		################################################################
		#	Get the unique list of aliases from the source host.
		################################################################
		aList = self.getVirtualHostAliasNamesList( sourceVhost )
		self.debug( __name__ + ".copy(): aList=" + str( aList ) + "\n" )
		self.debug( __name__ + ".copy(): aList length=" + str( len( aList ) ) + "\n" )

		########################################################################
		#	Add the destination virtual host if it does not exist and copy the
		#	aliases from the source virtual host to the destination one.
		########################################################################
		rc = self.addVirtualHost(cellName,destVhost)
		if rc:
			self.debug( __name__ + ".copy(): Added " + str( cellName ) + ":" + str( destVhost ) + "\n" )
			for item in aList:
				for hostname in item.keys():
					alias_port = item.get( hostname )
					self.debug( __name__ + ".copy(): hostname=" + str( hostname ) + ":" + "port=" + str( alias_port ) +  "\n" )
					rc = self.addVirtualHostAlias( str( destVhost ), str( hostname ), str( alias_port ) )
					if rc:
						self.debug( __name__ + ".copy(): Added " + str( hostname ) + ":" + str( alias_port ) + "\n" )
					else:
						self.logIt( __name__ + ".copy(): Did not add " + str( hostname ) + ":" + str( alias_port ) + "\n" )
						self.fast = False	# Turn off fast mode.
						return False
					#Endif
				#Endif
			#Endif
			self.fast = False	# Turn off fast mode.
		else:
			self.logIt( __name__ + ".copy(): Did not add " + str( cellName ) + ":" + str( destVhost ) + "\n" )
			self.fast = False	# Turn off fast mode.
			return False
		#Endif
		return True

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	addVirtualHostWithAliasesList()
	#
	#	DESCRIPTION:
	#		Add the given list of aliases to a possibly existing VirtualHost.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def addVirtualHostWithAliasesList(self,cellName,destVhost,aliasList):
		"""
		   Add the given list of aliases to a possibly existing VirtualHost.
		   PARAMETERS:
		       cellName    -- name of the cell.
		       destVhost   -- name of the destination virtual host that may or may not exist.
		       aliasList   -- list of aliases dictionary values that look like { "host1": "9999" }
		   RETURN:
		       True if successful.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): called.\n" )
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): cellName=" + str( cellName ) + ".\n" )
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): destVhost=" + str( destVhost ) + ".\n" )
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): aliasList=" + str( aliasList ) + ".\n" )

		###########################
		#	Turn on fast mode.
		###########################
		self.fast = True

		##################################################################
		#	Get the unique list of aliases from the existing virtual host.
		##################################################################
		destList = self.getVirtualHostAliasNamesList( destVhost )
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): destList=" + str( destList ) + "\n" )
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): destList length=" + str( len( destList ) ) + "\n" )

		###########################################################
		#	Merge the aliasList with the destList and make the
		#	resulting destList unique.
		###########################################################
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): destList=" + str( destList ) +  "\n" )
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): destList length=" + str( len( destList ) ) +  "\n" )
		destList.extend( aliasList )
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): destList length=" + str( len( destList ) ) +  "\n" )
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): destList length=" + str( len( destList ) ) +  "\n" )
		myutils = MyUtils()
		destList = myutils.uniquer( destList, self.uniqueID )
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): destList length=" + str( len( destList ) ) +  "\n" )
		self.debug( __name__ + ".addVirtualHostWithAliasesList(): destList length=" + str( len( destList ) ) +  "\n" )

		###########################################################
		#	Now delete the existing virtual host.
		###########################################################
		rc = self.deleteVirtualHost( destVhost )
		if rc:
			self.debug( __name__ + ".addVirtualHostWithAliasesList(): Deleted " + str( destVhost )  + "\n" )
		else:
			self.logIt( __name__ + ".addVirtualHostWithAliasesList(): Did not delete " + str( destVhost )  + "\n" )
			self.fast = False	# Turn off fast mode.
			return False
		#Endif

		###########################################################
		#	Now add it back so that it is void of aliases.
		###########################################################
		self.lastVirtualHost	= None	# Make sure that force the resolve of the new virtual host ObjectName.
		rc = self.addVirtualHost(cellName,destVhost)
		if rc:
			self.debug( __name__ + ".addVirtualHostWithAliasesList(): Added " + str( cellName ) + ":" + str( destVhost ) + "\n" )
			#######################################################
			#	Add the unique list of aliases.
			#######################################################
			for item in destList:
				for hostname in item.keys():
					alias_port = item.get( hostname )
					self.debug( __name__ + ".addVirtualHostWithAliasesList(): hostname=" + str( hostname ) + ":" + "port=" + str( alias_port ) +  "\n" )
					rc = self.addVirtualHostAlias( str( destVhost ), str( hostname ), str( alias_port ) )
					if rc:
						self.debug( __name__ + ".addVirtualHostWithAliasesList(): Added " + str( hostname ) + ":" + str( alias_port ) + "\n" )
					else:
						self.debug( __name__ + ".addVirtualHostWithAliasesList(): Did not add " + str( hostname ) + ":" + str( alias_port ) + "\n" )
						return False
					#Endif
				#Endif
			#Endif
			self.fast = False	# Turn off fast mode.
		else:
			self.logIt( __name__ + ".addVirtualHostWithAliasesList(): Did not add " + str( cellName ) + ":" + str( destVhost ) + "\n" )
			self.fast = False	# Turn off fast mode.
			return False
		#Endif
		return True

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createVirtualHostWithAliasesList()
	#
	#	DESCRIPTION:
	#		Create the given list of aliases to a possibly existing VirtualHost.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createVirtualHostWithAliasesList(self,cellName,destVhost,aliasList):
		"""
		   Create the given list of aliases to a possibly existing VirtualHost.
		   Any existing aliases will be deleted by this operation if the VirtualHost
		   exists.
		   PARAMETERS:
		       cellName    -- name of the cell.
		       destVhost   -- name of the destination virtual host that may or may not exist.
		       aliasList   -- list of aliases dictionary values that look like { "host1": "9999" }
		   RETURN:
		       True if successful.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createVirtualHostWithAliasesList(): called.\n" )
		self.debug( __name__ + ".createVirtualHostWithAliasesList(): cellName=" + str( cellName ) + ".\n" )
		self.debug( __name__ + ".createVirtualHostWithAliasesList(): destVhost=" + str( destVhost ) + ".\n" )
		self.debug( __name__ + ".createVirtualHostWithAliasesList(): aliasList=" + str( aliasList ) + ".\n" )

		###########################
		#	Turn on fast mode.
		###########################
		self.fast = True

		###########################################################
		#	Set the destList to the aliasList and make it unique.
		###########################################################
		destList = aliasList
		self.debug( __name__ + ".createVirtualHostWithAliasesList(): destList length=" + str( len( destList ) ) +  "\n" )
		self.debug( __name__ + ".createVirtualHostWithAliasesList(): destList length=" + str( len( destList ) ) +  "\n" )
		myutils = MyUtils()
		destList = myutils.uniquer( destList, self.uniqueID )
		self.debug( __name__ + ".createVirtualHostWithAliasesList(): destList length=" + str( len( destList ) ) +  "\n" )
		self.debug( __name__ + ".createVirtualHostWithAliasesList(): destList length=" + str( len( destList ) ) +  "\n" )

		###########################################################
		#	Now delete the existing virtual host.
		###########################################################
		rc = self.deleteVirtualHost( destVhost )
		if rc:
			self.debug( __name__ + ".createVirtualHostWithAliasesList(): Deleted " + str( destVhost )  + "\n" )
		else:
			self.logIt( __name__ + ".createVirtualHostWithAliasesList(): Did not delete " + str( destVhost )  + "\n" )
			self.fast = False	# Turn off fast mode.
			return False
		#Endif

		###########################################################
		#	Now add it back so that it is void of aliases.
		###########################################################
		self.lastVirtualHost	= None	# Make sure that force the resolve of the new virtual host ObjectName.
		rc = self.addVirtualHost(cellName,destVhost)
		if rc:
			self.debug( __name__ + ".createVirtualHostWithAliasesList(): Added " + str( cellName ) + ":" + str( destVhost ) + "\n" )
			#######################################################
			#	Add the unique list of aliases.
			#######################################################
			for item in destList:
				for hostname in item.keys():
					alias_port = item.get( hostname )
					self.debug( __name__ + ".createVirtualHostWithAliasesList(): hostname=" + str( hostname ) + ":" + "port=" + str( alias_port ) +  "\n" )
					rc = self.addVirtualHostAlias( str( destVhost ), str( hostname ), str( alias_port ) )
					if rc:
						self.debug( __name__ + ".createVirtualHostWithAliasesList(): Added " + str( hostname ) + ":" + str( alias_port ) + "\n" )
					else:
						self.debug( __name__ + ".createVirtualHostWithAliasesList(): Did not add " + str( hostname ) + ":" + str( alias_port ) + "\n" )
						return False
					#Endif
				#Endif
			#Endif
			self.fast = False	# Turn off fast mode.
		else:
			self.logIt( __name__ + ".createVirtualHostWithAliasesList(): Did not add " + str( cellName ) + ":" + str( destVhost ) + "\n" )
			self.fast = False	# Turn off fast mode.
			return False
		#Endif
		return True

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	uniqueID()
	#
	#	DESCRIPTION:
	#		To be used by the pylib.Utils.MyUtils.uniquer() method to make a
	#		list of dictionary items unique.  Each dictionary item must have
	#		one element that looks something like { "host": "9999" }.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def uniqueID(self,mydict):
		"""
           To be used by the pylib.Utils.MyUtils.uniquer() method to make a
           list of dictionary items unique.  Each dictionary item must have
           one element that looks something like { "host": "9999" }.
		   PARAMETERS:
		       mydict -- a dictionary of one element, something like { "host1": "port1" }
		   RETURN:
		       The string "host1:port1"
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".uniqueID(): called.\n" )
		self.debug( __name__ + ".uniqueID(): mydict=" + str( mydict ) + ".\n" )
		mykey = mydict.keys()[0]
		myvalue = mydict.get( mykey )
		return mykey + ":" + myvalue
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

######################################################################################
#Endclass
######################################################################################

#########################################################################
#	For testing.
#########################################################################
def main():
	#myLogger	= MyLogger( LOGFILE="/tmp/VirtualHostManager.log", STDOUT=True, DEBUG=True )
	myLogger	= MyLogger( LOGFILE="/tmp/VirtualHostManager.log", STDOUT=True, DEBUG=False )
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
	configService = ConfigService( adminClient=myclient, logger=myLogger )
	myVirtualHostManager = VirtualHostManager( adminObject, configService, logger=myLogger)

	cellName = "ServicesA"
	sourceVhost = "default_host"
	destVhost	= "vh_denis"
	rc = myVirtualHostManager.copyClean( cellName, sourceVhost, destVhost )
	if rc:
		myLogger.logIt( "main(): Copied " + str( sourceVhost ) + " to " + str( destVhost ) + "\n" )
	else:
		myLogger.logIt( "main(): Did not copy " + str( sourceVhost ) + " to " + str( destVhost ) + "\n" )
	#Endif

	aList = list()
	for i in range( 10 ):
		host = "host" + str( i )
		port = "000" + str( i )
		aList.append( { host: port } )
	#Endif
	myLogger.logIt( "main(): aList=" + str( aList ) + "\n" )
	rc = myVirtualHostManager.addVirtualHostWithAliasesList(cellName,destVhost,aList)
	if rc:
		myLogger.logIt( "main(): Added aliases to " + str( destVhost ) + "\n" )
	else:
		myLogger.logIt( "main(): Did not add aliases to " + str( destVhost ) + "\n" )
	#Endif

	rc = myVirtualHostManager.createVirtualHostWithAliasesList(cellName,destVhost,aList)
	if rc:
		myLogger.logIt( "main(): Added aliases to " + str( destVhost ) + "\n" )
	else:
		myLogger.logIt( "main(): Did not add aliases to " + str( destVhost ) + "\n" )
	#Endif

	vhList = myVirtualHostManager.getVirtualHostNamesList( cellName )
	myLogger.logIt( "main(): vhList=" + str( vhList ) + "\n" )

	#myVirtualHostManager.configService.save( myVirtualHostManager.configService.session, False )
	myVirtualHostManager.saveSession( False )

	myVirtualHostManager.closeMe()
	configService.closeMe()
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

