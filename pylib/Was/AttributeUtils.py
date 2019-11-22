#!/usr/bin/env jython
######################################################################################
##	AttributeUtils.py
##
##	Python module provides some common functionality for processing
##	javax.management.AttributeList, javax.management.Attribute,
##	javax.management.ObjectName, and ConfigService utilities.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	12/31/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
import random
import time
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

class AttributeUtils():
	"""
    AttributeUtils class that contains javax.management utilites.
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
				scope,
				type="DataSource",
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               configService - instance of the pylib.Was.ConfigService class.
			   scope         - Something like one of:
                                  "Cell=ServicesA:Node=node_ServicesA_01:Server=as_was7test_01"
                                  "Cell=ServicesA:Node=node_ServicesA_01"
                                  "Node=node_ServicesA_01:Server=as_was7test_01"
                                  "Node=node_ServicesA_01"
                                  "Cell=ServicesA:Cluster=cl_was7test_a"
                                  "Cluster=cl_was7test_a"
                                  "ServerCluster=cl_ServicesA_a"
               type          - list type.  Something like "DataSource" or "JDBCProvider" or "J2EEResourceProperty".
               logger        - instance of the MyLogger class.

           RETURN:
               An instance of this class
		"""

		self.configService			= configService
		self.logger					= logger
		self.type					= type
		self.attributesList			= list()	# javax.management.AttributeList[]
		self.rootObjectName			= None
		self.scope					= scope
		self.messages				= ""
		self.error					= False
		self.attributes 			= list()
		self.configRowCount			= 0
		self.configObjects			= list()	# javax.management.ObjectName[]
		self.myLastConfiguredObject	= None
		self.getRootObjectName()
		self.getAttributesList()
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
	#	getAttributeNames()
	#
	#	DESCRIPTION:
	#		Get the list of attribute names.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributeNames(self):
		"""Get the list of attribute names.
		   PARAMETERS:
		   RETURN:
		       The list of attribute names.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getAttribtuteNames(): called.\n" )
		return self.attributes
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	refresh()
	#
	#	DESCRIPTION:
	#		Get the Root ObjectName
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def refresh(self):
		"""Get the Root ObjectName.
		   PARAMETERS:
		   RETURN:
		       The ObjectName instance of the root.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".refresh(): called.\n" )
		self.getRootObjectName()
		self.getAttributesList()
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getRootObjectName()
	#
	#	DESCRIPTION:
	#		Get the Root ObjectName
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getRootObjectName(self):
		"""Get the Root ObjectName.
		   PARAMETERS:
		   RETURN:
		       The ObjectName instance of the root.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getRootObjectName(): called.\n" )

		################################################################
		#	Query for the javax.management.ObjectName
		################################################################
		myQuery		= self.scope
		#self.debug( __name__ + ".getRootObjectName(): myQuery=" + str( myQuery ) + "\n" )
		#myresults	= self.configService.resolve( self.configService.session, myQuery )
		myresults	= self.configService.resolveObjectName( myQuery )

		self.debug( __name__ + ".getRootObjectName(): myresults=" + str( myresults ) + "\n" )
		self.debug( __name__ + ".getRootObjectName(): length of myresults is " + str( len( myresults ) ) + "\n" )

		###############################################################
		#	See if we found the root ObjectName.
		###############################################################
		if len( myresults ) == 1:
			################################
			#	This is most likely case.
			################################
			myObjectName	= myresults[0]
			strArr			= str( myObjectName ).split( ',' )
			#self.debug( __name__ + ".getRootObjectName(): myObjectName=" + str( myObjectName ) + "\n" )
			for mystr in strArr:
				self.debug( __name__ + ".getRootObjectName(): mystr=" + str( mystr ) + "\n" )
			#Endfor
			objectFound = True
		else:
			###########################################
			#	We did not find the root ObjectName
			###########################################
			self.debug( __name__ + ".getRootObjectName(): No javax.management.ObjectName's found for scope=" + str( self.scope ) + ".\n" )
			self.messages += "No javax.management.ObjectName's found for scope=" + str( self.scope ) + "\n"
			self.error	= True
			objectFound = False
		#Endif

		#######################################################
		#	Return None if we didn't find the ObjectName.
		#######################################################
		if not objectFound: 
			self.rootObjectName = None
			return None
		else:
			self.rootObjectName = myresults[0]
			return myresults[0]
		#Endif
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	logAttributes()
	#
	#	DESCRIPTION:
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def logAttributes(self,name,attributes):
		"""log the attributes
		   PARAMETERS:
			   name        -- attribute name
		       aattributes -- attributes to be logged.
		   RETURN:
		"""
		self.debug( __name__ + ".logAttributes(): START...\n" )
		self.debug( __name__ + ".logAttributes(): value type=" + str( type( attributes ) ) + "\n" )
		myvalues = str( attributes ).split( ',' )

		self.debug( __name__ + ".logAttributes(): NAME=" + str( name ) + "\n" )
		for value in myvalues:
			self.debug( __name__ + ".logAttributes(): value=" + str( value ) + "\n" )
		#Endfor
		self.debug( __name__ + ".logAttributes(): FINISHED\n" )
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAttributesList()
	#
	#	DESCRIPTION:
	#		Get the attributes list.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributesList(self):
		"""Get the attributes list.
		   PARAMETERS:
		   RETURN:
		       The list of dictionary values of name/value attributes.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getAttributesList(): called.\n" )

		################################################################
		#	Query for the root object name
		################################################################
		#myObjectName = self.getRootObjectName()
		myObjectName = self.rootObjectName

		###########################################################
		#	Return None if we didn't find the rootObjectName.
		###########################################################
		if myObjectName is None: 
			self.logIt( __name__ + ".getAttributesList(): No root object for scope=" + str( self.scope ) + "\n" )
			return None

		pattern = self.configService.configServiceHelper.createObjectName( None, self.type )
		#pattern = self.configService.configServiceHelper.createObjectName( None, "DataSource" )
		#pattern = self.configService.configServiceHelper.createObjectName( None, "JDBCProvider" )
		self.debug( __name__ + ".getAttributesList(): pattern=" + str( pattern ) + "\n" )
		self.configObjects = self.configService.queryConfigObjects( self.configService.session, myObjectName, pattern, None )
		for configObject in self.configObjects:
			self.debug( __name__ + ".getAttributesList(): configObject=" + str( configObject ) + "\n" )
		#Endfor

		###########################################################
		#	List the supportedConfigObjectTypes.
		###########################################################
		#supportedConfigTypes = self.configService.getSupportedConfigObjectTypes()
		##self.debug( __name__ + ".getAttributesList(): supportedConfigTypes type=" + str( type( supportedConfigTypes ) ) + ".\n" )
		##self.debug( __name__ + ".getAttributesList(): supportedConfigTypes=" + str( supportedConfigTypes ) + ".\n" )
		#for ctype in supportedConfigTypes:
		#	self.debug( __name__ + ".getAttributesList(): ctype=" + str( ctype ) + "\n" )
		##Endfor
		
		################################################################
		#	Get the attributes for configOjects and build the
		#	return list.
		################################################################
		myAttrsList		= list()			# The list that gets returned.
		myAttributes	= AttributeList()	# Used to get the list of attributes.
		self.configRowCount	= 0
		for configObject in self.configObjects:
			#myattrList 			=  self.configService.getAttributes( self.configService.session, configObject, self.attributes, True )
			myattrList 		=  self.configService.getAttributes( self.configService.session, configObject, None, True )
			myAttributes.addAll( myattrList )
			myAttrsList.append( myattrList )	# append each javax.management.AttributeList return list.
			self.configRowCount += 1
			myconfigDataType	= self.configService.configServiceHelper.getConfigDataType( configObject )
			myconfigDataId		= self.configService.configServiceHelper.getConfigDataId( myattrList )
			self.debug( __name__ + ".getAttributesList(): myconfigDataType=" + str( myconfigDataType ) + "\n" )
			self.debug( __name__ + ".getAttributesList(): myconfigDataId=" + str( myconfigDataId ) + "\n" )
			self.debug( __name__ + ".getAttributesList(): myconfigDataId Href=" + str( myconfigDataId.getHref() ) + "\n" )
			self.debug( __name__ + ".getAttributesList(): myconfigDataId ContextUri=" + str( myconfigDataId.getContextUri() ) + "\n" )
			#self.debug( __name__ + ".getAttributesList(): myattrList type=" + str( type( myattrList ) ) + "\n" )
			#self.debug( __name__ + ".getAttributesList(): myattrList=" + str( myattrList ) + "\n" )
		#Endfor

		################################################################
		#self.debug( __name__ + ".getAttributesList(): myAttributes=" + str( myAttributes ) + "\n" )
		#self.debug( __name__ + ".getAttributesList(): myAttributes length=" + str( len( myAttributes ) ) + "\n" )
		#self.debug( __name__ + ".getAttributesList(): myAttributes type=" + str( type( myAttributes ) ) + "\n" )
		################################################################

		#################################################################
		#	Dynamically build the self.attributes list from myAttributes.
		#################################################################
		attrNames = list()
		for myattr in myAttributes:
			myname = myattr.getName()
			attrNames.append( myname )
		#	self.debug( __name__ + ".getAttributesList(): myattr name=" + str( myname ) + "\n" )
		#	#self.debug( __name__ + ".getAttributesList(): myattr value type=" + str( type( myattr.getValue() ) ) + "\n" )
			value = myattr.getValue()
			self.logAttributes( myname, value )
		#Endfor
		myutils			= MyUtils()
		attrNames		= myutils.uniquer( attrNames )	# Make the names unique.
		self.attributes = array( attrNames, String )
		self.attributesList = myAttrsList			# set the class instance variable.

		return self.attributesList
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAttributeValue()
	#
	#	DESCRIPTION:
	#		Get the attribute value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributeValue(self,index=0,key=None):
		"""Get the attribute value.
		   PARAMETERS:
		       index -- row number index into the self.attributesList
		       key   -- key to match on.
		   RETURN:
		       The value or None.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getAttributeValue(): called.\n" )
		self.debug( __name__ + ".getAttributeValue(): index=" + str( index ) + ".\n" )
		self.debug( __name__ + ".getAttributeValue(): key=" + str( key ) + ".\n" )
		if key is None: return None
		rIndex = 0
		for rowAttrList in self.attributesList:
			#self.debug( __name__ + ".getAttributeValue(): rowAttrList=" + str( rowAttrList ) + "\n" )
			if rIndex == index:
				for myAttr in rowAttrList:
					k = myAttr.getName()
					v = myAttr.getValue()
					#self.logIt( __name__ + ".getAttributeValue(): rIndex=" + str( rIndex ) + "-->" + str( k ) + "=" + str( v ) + "\n" )
					if k == key:
						return str( v )
				#Endfor
			#Endif
			rIndex += 1
		#Endfor
		return None
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAttributeIndexByValue()
	#
	#	DESCRIPTION:
	#		Get the attribute index by value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributeIndexByValue(self,key=None,value=None):
		"""Get the attribute index by value.
		   PARAMETERS:
		       key   -- key to match on.
		       value -- value to match on.
		   RETURN:
		       The index or -1.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getAttributeIndexByValue(): called.\n" )
		self.debug( __name__ + ".getAttributeIndexByValue(): key=" + str( key ) + ".\n" )
		self.debug( __name__ + ".getAttributeIndexByValue(): value=" + str( value ) + ".\n" )
		if key is None: return -1
		if value is None: return -1
		rIndex = 0
		for rowAttrList in self.attributesList:
			#self.debug( __name__ + ".getAttributeIndexByValue(): rowAttrList=" + str( rowAttrList ) + "\n" )
			for myAttr in rowAttrList:
				k = myAttr.getName()
				v = myAttr.getValue()
				#self.logIt( __name__ + ".getAttributeIndexByValue(): rIndex=" + str( rIndex ) + "-->" + str( k ) + "=" + str( v ) + "\n" )
				if k == key and v == value:
					return rIndex
			#Endfor
			rIndex += 1
		#Endfor
		return -1
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAttributeValues()
	#
	#	DESCRIPTION:
	#		Get the attribute values.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributeValues(self,key=None):
		"""Get the attribute values.
		   PARAMETERS:
		       key   -- key to match on.
		   RETURN:
		       The list of values.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getAttributeValues(): called.\n" )
		self.debug( __name__ + ".getAttributeValues(): key=" + str( key ) + ".\n" )
		if key is None: return None
		rList = list()
		for rowAttrList in self.attributesList:
			#self.debug( __name__ + ".getAttributeValues(): rowAttrList=" + str( rowAttrList ) + "\n" )
			for myAttr in rowAttrList:
				k = myAttr.getName()
				v = myAttr.getValue()
				#self.logIt( __name__ + ".getAttributeValues(): rIndex=" + str( rIndex ) + "-->" + str( k ) + "=" + str( v ) + "\n" )
				if k == key:
					rList.append( v )
			#Endfor
		#Endfor
		return rList
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	removeConfigObjectFromConfigList()
	#
	#	DESCRIPTION:
	#		Remove the given configuration object name from the config object list.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def removeConfigObjectFromConfigList(self,configObject):
		"""Remove the given configuration object name from the config object list.
		   PARAMETERS:
		       configObject   -- javax.management.ObjectName to delete.
		   RETURN:
		       True if successful or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".removeConfigObjectFromConfigList(): called.\n" )
		self.debug( __name__ + ".removeConfigObjectFromConfigList(): configObject type=" + str( type( configObject ) ) + ".\n" )
		name = configObject.getKeyProperty( '_Websphere_Config_Data_Display_Name' )
		configId = configObject.getKeyProperty( '_Websphere_Config_Data_Id' )
		index = 0
		for myConfigObject in self.configObjects:
			myname		= myConfigObject.getKeyProperty( '_Websphere_Config_Data_Display_Name' )
			myconfigId	= myConfigObject.getKeyProperty( '_Websphere_Config_Data_Id' )
			if myname == name and myconfigId == configId:
				self.configObjects.pop( index )	
				self.debug( __name__ + ".removeConfigObjectFromConfigList(): removed configObject list item at " + str( index ) + ".\n" )
			#Endif
			index += 1
		#Endfor
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	removeConfigObjectFromAttributesList()
	#
	#	DESCRIPTION:
	#		Remove the given configuration object name from the attributes object list.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def removeConfigObjectFromAttributesList(self,configObject):
		"""Remove the given configuration object name from the attributes object list.
		   PARAMETERS:
		       configObject   -- javax.management.ObjectName to delete.
		   RETURN:
		       True if successful or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".removeConfigObjectFromAttributesList(): called.\n" )
		self.debug( __name__ + ".removeConfigObjectFromAttributesList(): configObject type=" + str( type( configObject ) ) + ".\n" )
		#name		= configObject.getKeyProperty( '_Websphere_Config_Data_Display_Name' )
		configId	= configObject.getKeyProperty( '_Websphere_Config_Data_Id' )
		index 		= 0
		for myAttribute in self.attributesList:
			#attrName	= self.getAttributeValue( index, 'name' )
			attrId		= self.getAttributeValue( index, '_Websphere_Config_Data_Id' )

			#if attrName == name and attrId == configId:
			if attrId == configId:
				self.attributesList.pop( index )	
				self.debug( __name__ + ".removeConfigObjectFromAttributesList(): removed attributes list item at " + str( index ) + ".\n" )
			#Endif
			index += 1
		#Endfor
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	deleteConfigData()
	#
	#	DESCRIPTION:
	#		Delete the given configuration ObjectName.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deleteConfigData(self,configObject):
		"""Delete the given configuration ObjectName.
		   PARAMETERS:
		       configObject   -- javax.management.ObjectName to delete.
		   RETURN:
		       True if successful or False.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".deleteConfigData(): called.\n" )
		self.debug( __name__ + ".deleteConfigData(): configObject type=" + str( type( configObject ) ) + ".\n" )
		if isinstance( configObject, javax.management.ObjectName ):
			try:
				self.configService.deleteConfigData( self.configService.session, configObject )
				self.removeConfigObjectFromConfigList( configObject )
				self.removeConfigObjectFromAttributesList( configObject )
			except com.ibm.websphere.management.exception.ConfigServiceException, e:
				self.logIt( __name__ + ".deleteConfigData(): Unable to remove the configObject:" + str( e ) + "\n" )
				
				return False
			except com.ibm.websphere.management.exception.ConnectorException, ce:
				self.logIt( __name__ + ".deleteConfigData(): Unable to remove the configObject:" + str( ce ) + "\n" )
				
				return False
			#Endtry
		else:
			self.logIt( __name__ + ".deleteConfigData(): configObject is not an instance of javax.management.ObjectName. " + str( type( configObject ) ) + "\n" )
			return False
		#Endif
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getConfigObjectByDisplayName()
	#
	#	DESCRIPTION:
	#		Get the javax.management.ObjectName of the config object by name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getConfigObjectByDisplayName(self,name):
		"""Get the javax.management.ObjectName of the config object by name.
		   PARAMETERS:
		       name   -- name of the config object to find.
		   RETURN:
		       A javax.management.ObjectName of the config object or None.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getConfigObjectByDisplayName(): called.\n" )
		self.debug( __name__ + ".getConfigObjectByDisplayName(): name=" + str( name ) + ".\n" )
		for configObject in self.configObjects:
			myname = configObject.getKeyProperty( '_Websphere_Config_Data_Display_Name' )
			if myname == name:
				return configObject
		#Endfor
		return None
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getConfigObjectById()
	#
	#	DESCRIPTION:
	#		Get the javax.management.ObjectName of the config object by name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getConfigObjectById(self,id):
		"""Get the javax.management.ObjectName of the config object by name.
		   PARAMETERS:
		       name   -- name of the config object to find.
		   RETURN:
		       A javax.management.ObjectName of the config object or None.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getConfigObjectById(): called.\n" )
		self.debug( __name__ + ".getConfigObjectById(): id=" + str( id ) + ".\n" )
		for configObject in self.configObjects:
			myid = configObject.getKeyProperty( '_Websphere_Config_Data_Id' )
			if myid == id:
				return configObject
		#Endfor
		return None
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAttributeValueFromList()
	#
	#	DESCRIPTION:
	#		Get the attribute value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributeValueFromList(self,attributesList,key=None):
		"""Get the attribute value from the given javax.management.AttributeList.
		   PARAMETERS:
		       attributeList   -- javax.management.AttributeList to search in.
		       key             -- key to match on.
		   RETURN:
		       The value or None.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		#self.debug( __name__ + ".getAttributeValueFromList(): called.\n" )
		#self.debug( __name__ + ".getAttributeValueFromList(): attributesList type=" + str( type( attributesList ) ) + ".\n" )
		#self.debug( __name__ + ".getAttributeValueFromList(): key=" + str( key ) + ".\n" )
		if key is None: return None
		for myAttr in attributesList:
			k = myAttr.getName()
			v = myAttr.getValue()
			#self.logIt( __name__ + ".getAttributeValueFromList(): rIndex=" + str( rIndex ) + "-->" + str( k ) + "=" + str( v ) + "\n" )
			if k == key:
				#return str( v )
				return v
		#Endfor
		return None
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAttributeNamesFromList()
	#
	#	DESCRIPTION:
	#		Get the attribute names from the given list.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributeNamesFromList(self,attributesList):
		"""Get the attribute names from the given list
		   PARAMETERS:
		       attributeList   -- javax.management.AttributeList to search in.
		   RETURN:
		       The list of attribute names.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		#self.debug( __name__ + ".getAttributeNamesFromList(): called.\n" )
		self.debug( __name__ + ".getAttributeNamesFromList(): attributesList type=" + str( type( attributesList ) ) + ".\n" )

		rArr = list()
		if isinstance( attributesList, javax.management.AttributeList ):
			for myAttr in attributesList:
				k = myAttr.getName()
				#v = myAttr.getValue()
				#self.logIt( __name__ + ".getAttributeNamesFromList(): rIndex=" + str( rIndex ) + "-->" + str( k ) + "=" + str( v ) + "\n" )
				rArr.append( k )
			#Endfor
		#Endif
		return rArr
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAttributeListByNameAndContext()
	#
	#	DESCRIPTION:
	#		Get the javax.lang.AttributeList by name and context.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributeListByNameAndContext(self,name,context):
		"""Get the javax.lang.AttributeList by name and context.
		   PARAMETERS:
		       name    -- name of the attribute list
		       context -- something like "cells/ServicesA/clusters/cl_was7test_a"
		   RETURN:
		       The instance of the javax.lang.AttributeList or None.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getAttributeListByNameAndContext(): called.\n" )
		self.debug( __name__ + ".getAttributeListByNameAndContext(): name=" + str( name ) + ".\n" )
		self.debug( __name__ + ".getAttributeListByNameAndContext(): context=" + str( context ) + ".\n" )

		for rowAttrList in self.attributesList:
			#self.debug( __name__ + ".getAttributeListByNameAndContext(): rowAttrList=" + str( rowAttrList ) + "\n" )
			for myAttr in rowAttrList:
				k = myAttr.getName()
				v = myAttr.getValue()
				if k == 'name' and v == name:
					myconfigDataId	= self.configService.configServiceHelper.getConfigDataId( rowAttrList )
					mycontext 		= str( myconfigDataId.getContextUri() )
					if mycontext == context:
						return rowAttrList
				#Endif
			#Endfor
		#Endfor
		return None
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAttributeValueByNameAndContext()
	#
	#	DESCRIPTION:
	#		Get the value by name, context, attribute.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributeValueByNameAndContext(self,name,context,attribute):
		"""Get the value by name, context and attribute.
		   PARAMETERS:
		       name      -- name of the attribute list
		       context   -- something like "cells/ServicesA/clusters/cl_was7test_a"
			   attribute -- name of the attribute.
		   RETURN:
		       The value or None.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getAttributeValueByNameAndContext(): called.\n" )
		self.debug( __name__ + ".getAttributeValueByNameAndContext(): name=" + str( name ) + ".\n" )
		self.debug( __name__ + ".getAttributeValueByNameAndContext(): context=" + str( context ) + ".\n" )
		self.debug( __name__ + ".getAttributeValueByNameAndContext(): attribute=" + str( attribute ) + ".\n" )

		myAttrList = self.getAttributeListByNameAndContext( name, context )
		#self.debug( __name__ + ".getAttributeValueByNameAndContext(): myAttrList=" + str( myAttrList ) + "\n" )
		#self.debug( __name__ + ".getAttributeValueByNameAndContext(): myAttrList type=" + str( type( myAttrList ) ) + "\n" )

		for myAttr in myAttrList:
			k = myAttr.getName()
			v = myAttr.getValue()
			if k == attribute:
				return v
			#Endif
		#Endfor
		return None
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAttributesByListAndName()
	#
	#	DESCRIPTION:
	#		Get an instance of javax.management.AttributeList by list and name.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributesByListAndName(self,attributesList,name):
		"""Get an instance of javax.management.AttributeList by list and name.
		   PARAMETERS:
		       attributesList -- and instance of the javax.management.AttributeList
		       name           -- name of the list.
		   RETURN:
		       And instance of javax.management.AttributeList
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getAttributesByListAndName(): called.\n" )
		self.debug( __name__ + ".getAttributesByListAndName(): name=" + str( name ) + ".\n" )

		for myAttrList in attributesList:
			for myAttr in myAttrList:
				k = myAttr.getName()
				v = myAttr.getValue()
				if k == 'name' and v == name:
					return myAttrList
				#Endif
			#Endfor
		#Endfor
		return None
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	writeAttributes()
	#
	#	DESCRIPTION:
	#		Write the Attributes to a file.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def writeAttributes(self,fileName=None):
		"""Write the Attributes to a file.
		   PARAMETERS:
		       fileName -- file to write the data to.
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		#	myconfigDataType	= self.configService.configServiceHelper.getConfigDataType( configObject )
		#	myconfigDataId		= self.configService.configServiceHelper.getConfigDataId( myattrList )
		#	self.debug( __name__ + ".writeAttributes(): myconfigDataType=" + str( myconfigDataType ) + "\n" )
		#	self.debug( __name__ + ".writeAttributes(): myconfigDataId=" + str( myconfigDataId ) + "\n" )
		#	self.debug( __name__ + ".writeAttributes(): myconfigDataId Href=" + str( myconfigDataId.getHref() ) + "\n" )
		#	self.debug( __name__ + ".writeAttributes(): myconfigDataId ContextUri=" + str( myconfigDataId.getContextUri() ) + "\n" )
		################################################################
		self.debug( __name__ + ".writeAttributes(): called.\n" )
		self.debug( __name__ + ".writeAttributes(): fileName=" + str( fileName ) + ".\n" )
		try:
			if fileName is None:
				random.seed( time.localtime() )
				myrand = random.randint( 1, 100 )
				fileName = "/tmp/AttributeUtils." + str( myrand ) + ".tsv"
			#Endif
			FH = open( fileName, "w" )
			ostr = str( "requested_scope" ) + "\t"
			FH.write( ostr )
			ostr = str( "scope" ) + "\t"
			FH.write( ostr )
			numKeys = len( self.attributes )
			i = 0
			for name in self.attributes:
				#self.debug( __name__ + ".writeAttributes(): name type=" + str( type( name ) ) + "\n" )
				#self.debug( __name__ + ".writeAttributes(): name=" + str( name ) + "\n" )
				ostr = ""
				if i < numKeys - 1:
					ostr = str( name ) + "\t"
				else:
					ostr = str( name ) + "\n"
				#Endif
				FH.write( ostr )
				i += 1
			#Endif
			rIndex	= 0
			for rowAttrList in self.attributesList:
				ostr = str( self.scope ) + "\t"
				FH.write( ostr )
				myconfigDataId	= self.configService.configServiceHelper.getConfigDataId( rowAttrList )
				ostr 			= str( myconfigDataId.getContextUri() ) + "\t"
				FH.write( ostr )
				cols	= 0
				#self.logIt( __name__ + ".writeAttributes(): rowAttrList=" + str( rowAttrList ) + "\n" )
				for myAttr in rowAttrList:
					k = myAttr.getName()
					v = myAttr.getValue()
					#self.logIt( __name__ + ".writeAttributes(): rIndex=" + str( rIndex ) + "-->" + str( k ) + "=" + str( v ) + "\n" )
					#self.logIt( __name__ + ".writeAttributes(): rIndex=" + str( rIndex ) + "-->value type=" +  str( type( v ) ) + "\n" )
					ostr = ""
					if cols < numKeys - 1:
						ostr = str( v ) + "\t"
					else:
						ostr = str( v ) + "\n"
					FH.write( ostr )
					cols += 1
				#Endfor
				rIndex += 1
			#Endfor
			FH.close()
		except Exception, e:
			self.logIt( __name__ + ".writeAttributes(): " + str( e ) + "\n" )
			raise
		#Endtry
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	printTabFormattedAttributes()
	#
	#	DESCRIPTION:
	#		Print the Attributes to standard out.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def printTabFormattedAttributes(self):
		"""Print the Attributes to standard out.
		   PARAMETERS:
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".printTabFormattedAttributes(): called.\n" )
		numKeys = len( self.attributes )
		i = 0
		#ostr = str( "scope" ) + "\t"
		#print ostr,
		ostr = str( "requested_scope" ) + "\t"
		print ostr,
		ostr = str( "scope" ) + "\t"
		print ostr,
		for name in self.attributes:
			#self.debug( __name__ + ".printTabFormattedAttributes(): name type=" + str( type( name ) ) + "\n" )
			#self.debug( __name__ + ".printTabFormattedAttributes(): name=" + str( name ) + "\n" )
			ostr = ""
			if i < numKeys - 1:
				ostr = str( name ) + "\t"
			else:
				ostr = str( name ) + "\n"
			#Endif
			print ostr,
			i += 1
		#Endif
		rIndex	= 0
		for rowAttrList in self.attributesList:
			ostr = str( self.scope ) + "\t"
			print ostr,
			myconfigDataId	= self.configService.configServiceHelper.getConfigDataId( rowAttrList )
			ostr 			= str( myconfigDataId.getContextUri() ) + "\t"
			print ostr,
			cols	= 0
			#self.logIt( __name__ + ".printTabFormattedAttributes(): rowAttrList=" + str( rowAttrList ) + "\n" )
			for myAttr in rowAttrList:
				k = myAttr.getName()
				v = myAttr.getValue()
				#self.logIt( __name__ + ".printTabFormattedAttributes(): rIndex=" + str( rIndex ) + "-->" + str( k ) + "=" + str( v ) + "\n" )
				#self.logIt( __name__ + ".printTabFormattedAttributes(): rIndex=" + str( rIndex ) + "-->value type=" +  str( type( v ) ) + "\n" )
				ostr = ""
				if cols < numKeys - 1:
					ostr = str( v ) + "\t"
				else:
					ostr = str( v ) + "\n"
				print ostr,
				cols += 1
			#Endfor
			rIndex += 1
		#Endfor
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	printAttributes()
	#
	#	DESCRIPTION:
	#		Print the Attributes to standard out.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def printAttributes(self):
		"""Print the Attributes to standard out.
		   PARAMETERS:
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".printAttributes(): called.\n" )
		rIndex	= 0
		for rowAttrList in self.attributesList:
			#self.logIt( __name__ + ".printAttributes(): rowAttrList=" + str( rowAttrList ) + "\n" )
			for myAttr in rowAttrList:
				k = myAttr.getName()
				v = myAttr.getValue()
				myconfigDataId	= self.configService.configServiceHelper.getConfigDataId( rowAttrList )
				myRealScope		= str( myconfigDataId.getContextUri() )
				#self.logIt( __name__ + ".printAttributes(): rIndex=" + str( rIndex ) + "-->" + str( k ) + "=" + str( v ) + "\n" )
				#self.logIt( __name__ + ".printAttributes(): rIndex=" + str( rIndex ) + "-->value type=" +  str( type( v ) ) + "\n" )
				ostr = str( self.scope ) + "=>" + str( myRealScope ) + "=>" + str( rIndex ) + "-->" + str( k ) + "=" + str( v )
				print ostr
			#Endfor
			rIndex += 1
		#Endfor
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	deepLogOfAttributes()
	#
	#	DESCRIPTION:
	#		Recursively log the given javax.management.AttributeList which may
	#		contain javax.management.AttributesList's.	
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deepLogOfAttributes(self,attributeList,indentString="=>"):
		"""
           Recursively log the given javax.management.AttributeList which may 
		   contain javax.management.AttributesList's.
		   PARAMETERS:
		       attributeList -- instance of the javax.management.AttributeList class.
		       indentString  -- the caller should not set this, so don't.
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		#self.debug( __name__ + ".deepLogOfAttributes(): called.\n" )
		self.debug( __name__ + ".deepLogOfAttributes(): attributeList type=" + str( type( attributeList ) ) + ".\n" )

		###############################################################
		#	This logic is necessarily complex.  Sorry.
		###############################################################
		if isinstance( attributeList, javax.management.AttributeList ):
			###########################################################
			#	We are either an Attribute instance or another
			#	AttributeList instance, so recurse on each item
			#	and find out.
			###########################################################
			for item in attributeList:
				self.deepLogOfAttributes( item, indentString )
			#Endfor
		elif isinstance( attributeList, java.util.ArrayList ):
			#############################################################
			#	Deal with arrays and possibly arrays of arrays
			#	recursively.
			#############################################################
			for item in attributeList:
				#self.debug( __name__ + ".deepLogOfAttributes(): item=" + str( item ) + ".\n" )
				#self.debug( __name__ + ".deepLogOfAttributes(): item type=" + str( type( item ) ) + ".\n" )
				if isinstance( item, javax.management.AttributeList ):
					self.deepLogOfAttributes( item, indentString )
				else:
					if str( attributeList ) != '[]':
						for element in attributeList:
							#self.debug( __name__ + ".deepLogOfAttributes(): element type=" + str( type( element ) ) + ".\n" )
							if isinstance( element, unicode ):
								##################################################################
								#	We are at the bottom of the tree so print and unwind the
								#	stack.
								##################################################################
								self.logIt( __name__ + ".deepLogOfAttributes(): " + str( indentString ) + str( element ) + "\n" )
							else:
								###################################################################
								#	Since we are list we recurse with another indent
								#	level.
								###################################################################
								self.deepLogOfAttributes( element, "=" + indentString )
						#Endfor	
					#Endif
				#Endif
			#Endfor
		elif isinstance( attributeList, javax.management.Attribute ):
			##########################################################
			#	We are an instance of an Attribute so get the name
			#	and value.
			##########################################################
			myname = attributeList.getName()
			myvalue= attributeList.getValue()

			#########################################################
			#	Check to see if myvalue is another list of some
			#	type.
			#########################################################
			if isinstance( myvalue, javax.management.AttributeList ) or isinstance( myvalue, java.util.ArrayList ):
				#######################################################################
				#	We are a list of some type so print the "See the following message.
				#######################################################################
				#self.debug( __name__ + ".deepLogOfAttributes(): myvalue=" + str( myvalue ) + ".\n" )
				#self.debug( __name__ + ".deepLogOfAttributes(): myvalue type=" + str( type( myvalue ) ) + ".\n" )
				if str( myvalue ) == '' or str( myvalue ) == 'None' or str( myvalue ) == '[]':
					###################################################################
					#	If we are any of the above conditions, we at the bottom
					#	so we will unwind back up the stack after the next recurse.
					###################################################################
					self.logIt( __name__ + ".deepLogOfAttributes(): " + str( indentString ) + str( myname ) + "= See the following: '=" +  str( indentString ) + "'\n" )
					self.logIt( __name__ + ".deepLogOfAttributes(): =" + str( indentString ) + str( myvalue ) + "\n" )
				else:
					###################################################################
					#	Since we are list of some type we recurse with another indent
					#	level.
					###################################################################
					self.logIt( __name__ + ".deepLogOfAttributes(): " + str( indentString ) + str( myname ) + "= See the following: '=" +  str( indentString ) + "'\n" )
					self.deepLogOfAttributes( myvalue, "=" + indentString )
				#Endif
			else:
				##########################################################
				#	print and then unwind the stack.
				##########################################################
				self.logIt( __name__ + ".deepLogOfAttributes(): " + str( indentString ) + str( myname ) + "=" + str( myvalue ) + "\n" )
			#Endif
			#self.deepLogOfAttributes( myvalue, "=" + indentString )
		#Endif
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	deepPrintOfAttributes()
	#
	#	DESCRIPTION:
	#		Recursively print the given javax.management.AttributeList which may
	#		contain javax.management.AttributesList's.	
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deepPrintOfAttributes(self,attributeList,indentString="=>"):
		"""
           Recursively print the given javax.management.AttributeList which may 
		   contain javax.management.AttributesList's.
		   PARAMETERS:
		       attributeList -- instance of the javax.management.AttributeList class.
		       indentString  -- the caller should not set this, so don't.
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		#self.debug( __name__ + ".deepPrintOfAttributes(): called.\n" )
		#self.debug( __name__ + ".deepPrintOfAttributes(): attributeList type=" + str( type( attributeList ) ) + ".\n" )

		###############################################################
		#	This logic is necessarily complex.  Sorry.
		###############################################################
		if isinstance( attributeList, javax.management.AttributeList ):
			###########################################################
			#	We are either an Attribute instance or another
			#	AttributeList instance, so recurse on each item
			#	and find out.
			###########################################################
			for item in attributeList:
				self.deepPrintOfAttributes( item, indentString )
			#Endfor
		elif isinstance( attributeList, java.util.ArrayList ):
			#############################################################
			#	Deal with arrays and possibly arrays of arrays
			#	recursively.
			#############################################################
			for item in attributeList:
				#self.debug( __name__ + ".deepPrintOfAttributes(): item=" + str( item ) + ".\n" )
				#self.debug( __name__ + ".deepPrintOfAttributes(): item type=" + str( type( item ) ) + ".\n" )
				if isinstance( item, javax.management.AttributeList ):
					self.deepPrintOfAttributes( item, indentString )
				else:
					if str( attributeList ) != '[]':
						for element in attributeList:
							#self.debug( __name__ + ".deepPrintOfAttributes(): element type=" + str( type( element ) ) + ".\n" )
							if isinstance( element, unicode ):
								##################################################################
								#	We are at the bottom of the tree so print and unwind the
								#	stack.
								##################################################################
								print str( indentString ) + str( element )
							else:
								###################################################################
								#	Since we are list we recurse with another indent
								#	level.
								###################################################################
								self.deepPrintOfAttributes( element, "=" + indentString )
						#Endfor	
					#Endif
				#Endif
			#Endfor
		elif isinstance( attributeList, javax.management.Attribute ):
			##########################################################
			#	We are an instance of an Attribute so get the name
			#	and value.
			##########################################################
			myname = attributeList.getName()
			myvalue= attributeList.getValue()

			#########################################################
			#	Check to see if myvalue is another list of some
			#	type.
			#########################################################
			if isinstance( myvalue, javax.management.AttributeList ) or isinstance( myvalue, java.util.ArrayList ):
				#######################################################################
				#	We are a list of some type so print the "See the following message.
				#######################################################################
				#self.debug( __name__ + ".deepPrintOfAttributes(): myvalue=" + str( myvalue ) + ".\n" )
				#self.debug( __name__ + ".deepPrintOfAttributes(): myvalue type=" + str( type( myvalue ) ) + ".\n" )
				if str( myvalue ) == '' or str( myvalue ) == 'None' or str( myvalue ) == '[]':
					###################################################################
					#	If we are any of the above conditions, we at the bottom
					#	so we will unwind back up the stack after the next recurse.
					###################################################################
					print str( indentString ) + str( myname ) + "= See the following: '=" +  str( indentString ) + "'"
					print "=" + indentString + str( myvalue )
				else:
					###################################################################
					#	Since we are list of some type we recurse with another indent
					#	level.
					###################################################################
					print str( indentString ) + str( myname ) + "= See the following: '=" +  str( indentString ) + "'"
					self.deepPrintOfAttributes( myvalue, "=" + indentString )
				#Endif
			else:
				##########################################################
				#	print and then unwind the stack.
				##########################################################
				print str( indentString ) + str( myname ) + "=" + str( myvalue )
			#Endif
			#self.deepPrintOfAttributes( myvalue, "=" + indentString )
		#Endif
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	deepWriteOfAttributes()
	#
	#	DESCRIPTION:
	#		Recursively write the given javax.management.AttributeList which may
	#		contain javax.management.AttributesList's.	
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def deepWriteOfAttributes(self,attributeList,fileHandle,indentString="=>"):
		"""
           Recursively write the given javax.management.AttributeList which may 
		   contain javax.management.AttributesList's.
		   PARAMETERS:
		       attributeList -- instance of the javax.management.AttributeList class.
		       fileHandle    -- handle to be written to.
		       indentString  -- the caller should not set this, so don't.
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		#self.debug( __name__ + ".deepWriteOfAttributes(): called.\n" )
		#self.debug( __name__ + ".deepWriteOfAttributes(): attributeList type=" + str( type( attributeList ) ) + ".\n" )
		#fileHandle.write( __name__ + ".deepWriteOfAttributes(): attributeList type=" + str( type( attributeList ) ) + ".\n" )
		#self.debug( __name__ + ".deepWriteOfAttributes(): fileHandle type=" + str( type( fileHandle ) ) + ".\n" )

		###############################################################
		#	This logic is necessarily complex.  Sorry.
		###############################################################
		if isinstance( attributeList, javax.management.AttributeList ):
			###########################################################
			#	We are either an Attribute instance or another
			#	AttributeList instance, so recurse on each item
			#	and find out.
			###########################################################
			for item in attributeList:
				self.deepWriteOfAttributes( item, fileHandle, indentString )
			#Endfor
		elif isinstance( attributeList, java.util.ArrayList ):
			#############################################################
			#	Deal with arrays and possibly arrays of arrays
			#	recursively.
			#############################################################
			for item in attributeList:
				#self.debug( __name__ + ".deepWriteOfAttributes(): item=" + str( item ) + ".\n" )
				#self.debug( __name__ + ".deepWriteOfAttributes(): item type=" + str( type( item ) ) + ".\n" )
				if isinstance( item, javax.management.AttributeList ):
					self.deepWriteOfAttributes( item, fileHandle, indentString )
				else:
					if str( attributeList ) != '[]':
						for element in attributeList:
							#self.debug( __name__ + ".deepWriteOfAttributes(): element type=" + str( type( element ) ) + ".\n" )
							if isinstance( element, unicode ):
								##################################################################
								#	We are at the bottom of the tree so print and unwind the
								#	stack.
								##################################################################
								fileHandle.write( str( indentString ) + str( element ) + '\n' )
							else:
								###################################################################
								#	Since we are list we recurse with another indent
								#	level.
								###################################################################
								self.deepWriteOfAttributes( element, fileHandle, "=" + indentString )
						#Endfor	
					#Endif
				#Endif
			#Endfor
		elif isinstance( attributeList, javax.management.Attribute ):
			##########################################################
			#	We are an instance of an Attribute so get the name
			#	and value.
			##########################################################
			myname = attributeList.getName()
			myvalue= attributeList.getValue()

			#########################################################
			#	Check to see if myvalue is another list of some
			#	type.
			#########################################################
			if isinstance( myvalue, javax.management.AttributeList ) or isinstance( myvalue, java.util.ArrayList ):
				#######################################################################
				#	We are a list of some type so print the "See the following message.
				#######################################################################
				#self.debug( __name__ + ".deepWriteOfAttributes(): myvalue=" + str( myvalue ) + ".\n" )
				#self.debug( __name__ + ".deepWriteOfAttributes(): myvalue type=" + str( type( myvalue ) ) + ".\n" )
				if str( myvalue ) == '' or str( myvalue ) == 'None' or str( myvalue ) == '[]':
					###################################################################
					#	If we are any of the above conditions, we at the bottom
					#	so we will unwind back up the stack after the next recurse.
					###################################################################
					fileHandle.write( str( indentString ) + str( myname ) + "= See the following: '=" +  str( indentString ) + "'\n" )

					fileHandle.write( "=" + indentString + str( myvalue ) + "\n" )
				else:
					###################################################################
					#	Since we are list of some type we recurse with another indent
					#	level.
					###################################################################
					fileHandle.write( str( indentString ) + str( myname ) + "= See the following: '=" +  str( indentString ) + "'\n" )
					self.deepWriteOfAttributes( myvalue, fileHandle, "=" + indentString )
				#Endif
			else:
				##########################################################
				#	print and then unwind the stack.
				##########################################################
				ostr = str( indentString ) + str( myname ) + "=" + str( myvalue ) + "\n"
				fileHandle.write( ostr )
			#Endif
			#self.deepWriteOfAttributes( myvalue, fileHandle, "=" + indentString )
		#Endif
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createConfigDataWithTemplate()
	#
	#	DESCRIPTION:
	#		Create the given configuration data in WebSphere
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createConfigDataWithTemplate(self,templateId,configType,attributeList,myparent=None):
		"""Create the given configuration data in WebSphere.
		   PARAMETERS:
			   templateId    -- template id.  Something like 'JDBCProvider_3'
			   configType    -- configuration type.  Something like 'JDBCProvider' or 'DataSource'
			   attributeList -- javax.management.AttributeList.  List of attributes to be created for the attributeName and configType.
			   myparent      -- optional javax.management.ObjectName instance to be used as the parent object.
		   RETURN:
		       True if successful or False.
		"""

		parent		= self.rootObjectName
		if myparent is not None:
			parent	= myparent

		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createConfigDataWithTemplate(): called.\n" )
		self.debug( __name__ + ".createConfigDataWithTemplate(): templateId=" + str( templateId ) + ".\n" )
		self.debug( __name__ + ".createConfigDataWithTemplate(): configType=" + str( configType ) + ".\n" )
		self.debug( __name__ + ".createConfigDataWithTemplate(): attributeList type=" + str( type( attributeList ) ) + ".\n" )
		if not isinstance( parent, javax.management.ObjectName ):
			self.logIt( __name__ + ".createConfigDataWithTemplate(): parent is not an instance of javax.management.ObjectName. " + str( type( parent ) ) + "\n" )
			return False
		#Endif
		if not isinstance( attributeList, javax.management.AttributeList ):
			self.logIt( __name__ + ".createConfigDataWithTemplate(): attributeList is not an instance of javax.management.AttributeList. " + str( type( attributeList ) ) + "\n" )
			return False
		#Endif
		#template = self.configService.queryTemplates( this.configService.session, configType )[0]
		template = self.templateListManager.getTemplateObject( templateId )
		self.debug( __name__ + ".createConfigDataWithTemplate(): template=" + str( template ) + "\n" )
		self.debug( __name__ + ".createConfigDataWithTemplate(): template type=" + str( type( template ) ) + "\n" )
		if template is None:
			self.logIt( __name__ + ".createConfigDataWithTemplate(): Unable to find the configuration template for " + str( configType ) + "\n" )
			return False
		else:
			try:
				if parent is None:
					parent = self.configService.createObjectName( attributeList )
				self.myLastConfiguredObject = self.configService.createConfigDataByTemplate( self.configService.session, parent, configType, attributeList, template )
				self.refresh()
				##self.configObjects.append( self.myLastConfiguredObject )
			except com.ibm.websphere.management.exception.ConfigServiceException, e:
				self.logIt( __name__ + ".createConfigDataWithTemplate(): Unable to create the resource for " + str( templateId ) + ":" + str( e ) + "\n" )
				return False
			except com.ibm.websphere.management.exception.ConnectorException, ce:
				self.logIt( __name__ + ".createConfigDataWithTemplate(): Unable to create the resource for " + str( templateId ) + ":" + str( ce ) + "\n" )
				return False
			#Endtry
		#Endif
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createConfigData()
	#
	#	DESCRIPTION:
	#		Create the given configuration data in WebSphere
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def createConfigData(self,attributeName,configType,attributeList,myparent=None):
		"""Create the given configuration data in WebSphere.
		   PARAMETERS:
			   attributeName -- configuration type.  Something like 'JDBCProvider' or 'DataSource'
			   configType    -- configuration type.  Something like 'JDBCProvider' or 'DataSource'
			   attributeList -- javax.management.AttributeList.  List of attributes to be created for the attributeName and configType.
			   myparent      -- optional javax.management.ObjectName instance to be used as the parent object.
		   RETURN:
		       True if successful or False.
		"""
		parent		= self.rootObjectName
		if myparent is not None:
			parent = myparent
		#Endif
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".createConfigData(): called.\n" )
		self.debug( __name__ + ".createConfigData(): attributeName=" + str( attributeName ) + ".\n" )
		self.debug( __name__ + ".createConfigData(): configType=" + str( configType ) + ".\n" )
		self.debug( __name__ + ".createConfigData(): attributeList type=" + str( type( attributeList ) ) + ".\n" )
		self.debug( __name__ + ".createConfigData(): parent=" + str( parent ) + ".\n" )
		if not isinstance( parent, javax.management.ObjectName ):
			self.logIt( __name__ + ".createConfigData(): parent is not an instance of javax.management.ObjectName. " + str( type( parent ) ) + "\n" )
			return False
		#Endif
		if not isinstance( attributeList, javax.management.AttributeList ):
			self.logIt( __name__ + ".createConfigData(): attributeList is not an instance of javax.management.AttributeList. " + str( type( attributeList ) ) + "\n" )
			return False
		#Endif
		try:
			#################################################################################################
			#metaAttributes = self.configService.getAttributesMetaInfo( configType )
			#self.logIt( __name__ + ".createConfigData(): parent meta info=" + str( metaAttributes ) + "\n" )
			#supportedTypes = self.configService.getSupportedConfigObjectTypes()
			#for supportedType in supportedTypes:
			#	self.logIt( __name__ + ".createConfigData(): parent supported type=" + str( supportedType ) + "\n" )
			#################################################################################################
			self.myLastConfiguredObject = self.configService.createConfigData( self.configService.session, parent, attributeName, configType, attributeList )
			self.refresh()
		except com.ibm.websphere.management.exception.ConfigServiceException, e:
			self.logIt( __name__ + ".createConfigData(): Unable to create the resource for " + str( attributeName ) + ":" + str( e ) + "\n" )
			return False
		except com.ibm.websphere.management.exception.ConnectorException, ce:
			self.logIt( __name__ + ".createConfigData(): Unable to create the resource for " + str( attributeName ) + ":" + str( ce ) + "\n" )
			return False
		#Endtry
		return True
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
	myLogger	= MyLogger( LOGFILE="/tmp/AttributeUtils.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/AttributeUtils.log", STDOUT=True, DEBUG=False )
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
	myAttributeUtils = AttributeUtils( configService, scope="Cell=ServicesA", type="DataSource", logger=myLogger)
	#myAttributeUtils = AttributeUtils( configService, scope="Cell=ServicesA", type="JDBCProvider", logger=myLogger)

	attrNames = myAttributeUtils.getAttributeNames()
	myAttributeUtils.writeAttributes( fileName="/nfs/home4/dmpapp/appd4ec/tmp/denis.tsv" )
	myAttributeUtils.printTabFormattedAttributes()
	myAttributeUtils.printAttributes()

	name = "DefaultEJBTimerDataSource"
	context = "cells/ServicesA/nodes/node_ServicesA_01/servers/as_was7test_01"
	myAttrList = myAttributeUtils.getAttributeListByNameAndContext( name, context )
	#myAttributeUtils.deepLogOfAttributes( myAttrList )
	
	for mylist in myAttributeUtils.attributesList:
		myAttributeUtils.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myAttributeUtils.attributesList:
		myAttributeUtils.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myAttributeUtils.attributesList:
			myAttributeUtils.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
			myLogger.logIt( "main(): " + str( e ) + "\n" )
			raise
	#Endtry

	#myValue = myAttributeUtils.getAttributeValueByNameAndContext( name, context, "propertySet" )
	#myLogger.logIt( "main(): myValue=" + str( myValue ) + ".\n" )
	#myLogger.logIt( "main(): myValue type=" + str( type( myValue ) ) + ".\n" )

	#for myAttr in myValue:
		#myLogger.logIt( "main(): myAttr=" + str( myAttr ) + ".\n" )
		#myLogger.logIt( "main(): myAttr type=" + str( type( myAttr ) ) + ".\n" )
		#myName = myAttr.getName()
		#myValue = myAttr.getValue()
		#myLogger.logIt( "main(): myName=" + str( myName ) + ".\n" )
		#myLogger.logIt( "main(): myValue=" + str( myValue ) + ".\n" )
		#if myName == "resourceProperties":
		#	myAttrList = myAttributeUtils.getAttributesByListAndName( myValue, "databaseName" )
		#	myLogger.logIt( "main(): myAttrList=" + str( myAttrList ) + ".\n" )
		#	myLogger.logIt( "main(): myAttrList type=" + str( type( myAttrList ) ) + ".\n" )
		#	mydes = myAttributeUtils.getAttributeValueFromList( myAttrList, key="description" )
		#	myLogger.logIt( "main(): mydes=" + str( mydes ) + "\n" )

		#	myNames = myAttributeUtils.getAttributeNamesFromList( myAttrList )
		#	for name in myNames:
		#		value = myAttributeUtils.getAttributeValueFromList( myAttrList, key=name )
		#		myLogger.logIt( "main(): name=" + name + " value=" + str( value ) + "\n" )
		#	#Endfor
		##Endif
	##Endfor

	configService.discard( configService.session )

	configService.closeMe()
	myAttributeUtils.closeMe()
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
