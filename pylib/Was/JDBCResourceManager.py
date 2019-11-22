#!/usr/bin/env jython
######################################################################################
##	JDBCResourceManager.py
##
##	Python module replaces some of the functions in the 
##	/nfs/dist/dmp/amp/wdt/_resources.jacl 
##	file and makes JDBC resource management object oriented.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	12/28/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
import random
import time
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
from java.util import ArrayList

import com.ibm.websphere.security.WebSphereRuntimePermission as WebSphereRuntimePermission
import com.ibm.websphere.security.auth.WSLoginFailedException as WSLoginFailedException
import com.ibm.ws.security.util.InvalidPasswordDecodingException as InvalidPasswordDecodingException
import com.ibm.websphere.management.exception.ConnectorException as ConnectorException

class JDBCResourceManager():
	"""
    JDBCResourceManager class that contains VirtualHost management methods.
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

		self.adminClient		= adminClient
		self.configService		= configService
		self.logger				= logger
		self.aliasNamesList		= list()
		self.jdbcAttributesList	= list()
		self.rootObjectName		= None
		self.scope				= scope
		#self.attributes 		= array( ['name', 'description', 'classpath', 'nativepath', 'providerType', 'isolatedClassLoader', 'implementationClassName', 'xa', 'propertySet'], String )
		self.attributes 		= None
		self.rowCount			= 0
		self.getRootObjectName()
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
		self.configService.closeMe()
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
	#	getRootObjectName()
	#
	#	DESCRIPTION:
	#		Get the JDBC resource Root ObjectName
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getRootObjectName(self):
		"""Get the JDBC resource Root ObjectName.
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
			myObjectName = myresults[0]
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
			self.debug( __name__ + ".getRootObjectName(): No javax.management.ObjectName's found.\n" )
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
	#	getJDBCAttributesList()
	#
	#	DESCRIPTION:
	#		Get the JDBC providers attributes list.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getJDBCAttributesList(self):
		"""Get the JDBC providers attributes list.
		   PARAMETERS:
		   RETURN:
		       The list of dictionary values of name/value attributes.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getJDBCAttributesList(): called.\n" )

		################################################################
		#	Query for the root object name
		################################################################
		#myObjectName = self.getRootObjectName()
		myObjectName = self.rootObjectName

		###########################################################
		#	Return None if we didn't find the rootObjectName.
		###########################################################
		if myObjectName is None: return None

		#pattern = self.configService.configServiceHelper.createObjectName( None, "DataSource" )
		pattern = self.configService.configServiceHelper.createObjectName( None, "JDBCProvider" )
		#self.debug( __name__ + ".getJDBCAttributesList(): pattern=" + str( pattern ) + "\n" )
		configObjects = self.configService.queryConfigObjects( self.configService.session, myObjectName, pattern, None )
		for configObject in configObjects:
			self.debug( __name__ + ".getJDBCAttributesList(): configObject=" + str( configObject ) + "\n" )
		#Endfor

		###########################################################
		#	List the supportedConfigObjectTypes.
		###########################################################
		#supportedConfigTypes = self.configService.getSupportedConfigObjectTypes()
		##self.debug( __name__ + ".getJDBCAttributesList(): supportedConfigTypes type=" + str( type( supportedConfigTypes ) ) + ".\n" )
		##self.debug( __name__ + ".getJDBCAttributesList(): supportedConfigTypes=" + str( supportedConfigTypes ) + ".\n" )
		#for ctype in supportedConfigTypes:
		#	self.debug( __name__ + ".getJDBCAttributesList(): ctype=" + str( ctype ) + "\n" )
		##Endfor
		
		################################################################
		#	Get the attributes for configOjects and build the
		#	return list.
		################################################################
		myAttrsList		= list()			# The list that gets returned.
		myAttributes	= AttributeList()	# Used to get the list of attributes.
		self.rowCount	= 0
		for configObject in configObjects:
			myattrList 			=  self.configService.getAttributes( self.configService.session, configObject, self.attributes, True )
			#myattrList 		=  self.configService.getAttributes( self.configService.session, configObject, None, True )
			myAttributes.addAll( myattrList )
			myAttrsList.append( myattrList )	# append each javax.management.AttributeList return list.
			self.rowCount += 1
			myconfigDataType	= self.configService.configServiceHelper.getConfigDataType( configObject )
			myconfigDataId		= self.configService.configServiceHelper.getConfigDataId( myattrList )
			self.debug( __name__ + ".getJDBCAttributesList(): myconfigDataType=" + str( myconfigDataType ) + "\n" )
			self.debug( __name__ + ".getJDBCAttributesList(): myconfigDataId=" + str( myconfigDataId ) + "\n" )
			self.debug( __name__ + ".getJDBCAttributesList(): myconfigDataId Href=" + str( myconfigDataId.getHref() ) + "\n" )
			self.debug( __name__ + ".getJDBCAttributesList(): myconfigDataId ContextUri=" + str( myconfigDataId.getContextUri() ) + "\n" )
			self.debug( __name__ + ".getJDBCAttributesList(): myattrList type=" + str( type( myattrList ) ) + "\n" )
			self.debug( __name__ + ".getJDBCAttributesList(): myattrList=" + str( myattrList ) + "\n" )
		#Endfor

		################################################################
		#self.debug( __name__ + ".getJDBCAttributesList(): myAttributes=" + str( myAttributes ) + "\n" )
		#self.debug( __name__ + ".getJDBCAttributesList(): myAttributes length=" + str( len( myAttributes ) ) + "\n" )
		#self.debug( __name__ + ".getJDBCAttributesList(): myAttributes type=" + str( type( myAttributes ) ) + "\n" )
		################################################################

		#################################################################
		#	Dynamically build the self.attributes list from myAttributes.
		#################################################################
		attrNames = list()
		for myattr in myAttributes:
			myname = myattr.getName()
			attrNames.append( myname )
		#	self.debug( __name__ + ".getJDBCAttributesList(): myattr name=" + str( myname ) + "\n" )
		#	#self.debug( __name__ + ".getJDBCAttributesList(): myattr value type=" + str( type( myattr.getValue() ) ) + "\n" )
			value = myattr.getValue()
			self.logAttributes( myname, value )
		#Endfor
		myutils			= MyUtils()
		attrNames		= myutils.uniquer( attrNames )	# Make the names unique.
		self.attributes = array( attrNames, String )
		self.jdbcAttributesList = myAttrsList			# set the class instance variable.

		return self.jdbcAttributesList
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAttributeValue()
	#
	#	DESCRIPTION:
	#		Get the jdbc attribute value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributeValue(self,index=0,key=None):
		"""Get the jdbc attribute value.
		   PARAMETERS:
		       index -- row number index into the jdbcAttributeList
		       key   -- key to match on.
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".getAttributeValue(): called.\n" )
		self.debug( __name__ + ".getAttributeValue(): index=" + str( index ) + ".\n" )
		self.debug( __name__ + ".getAttributeValue(): key=" + str( key ) + ".\n" )
		if key is None: return None
		rIndex = 0
		for rowAttrList in self.jdbcAttributesList:
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
	#	writeAttributes()
	#
	#	DESCRIPTION:
	#		Write the JDBCAttributes to a file.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def writeAttributes(self,fileName=None):
		"""Write the JDBCAttributes to a file.
		   PARAMETERS:
		       fileName -- file to write the data to.
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		#	myconfigDataType	= self.configService.configServiceHelper.getConfigDataType( configObject )
		#	myconfigDataId		= self.configService.configServiceHelper.getConfigDataId( myattrList )
		#	self.debug( __name__ + ".getJDBCAttributesList(): myconfigDataType=" + str( myconfigDataType ) + "\n" )
		#	self.debug( __name__ + ".getJDBCAttributesList(): myconfigDataId=" + str( myconfigDataId ) + "\n" )
		#	self.debug( __name__ + ".getJDBCAttributesList(): myconfigDataId Href=" + str( myconfigDataId.getHref() ) + "\n" )
		#	self.debug( __name__ + ".getJDBCAttributesList(): myconfigDataId ContextUri=" + str( myconfigDataId.getContextUri() ) + "\n" )
		self.debug( __name__ + ".writeAttributes(): called.\n" )
		self.debug( __name__ + ".writeAttributes(): fileName=" + str( fileName ) + ".\n" )
		try:
			if fileName is None:
				random.seed( time.localtime() )
				myrand = random.randint( 1, 100 )
				fileName = "/tmp/JDBCResourceManager." + str( myrand ) + ".tsv"
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
			for rowAttrList in self.jdbcAttributesList:
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
	#		Print the JDBCAttributes to standard out.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def printTabFormattedAttributes(self):
		"""Print the JDBCAttributes to standard out.
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
		for rowAttrList in self.jdbcAttributesList:
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
	#		Print the JDBCAttributes to standard out.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def printAttributes(self):
		"""Print the JDBCAttributes to standard out.
		   PARAMETERS:
		   RETURN:
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".printAttributes(): called.\n" )
		rIndex	= 0
		for rowAttrList in self.jdbcAttributesList:
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
	myLogger	= MyLogger( LOGFILE="/tmp/JDBCResourceManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/JDBCResourceManager.log", STDOUT=True, DEBUG=False )
	adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1" )
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
	myJDBCResourceManager = JDBCResourceManager( adminObject, configService, scope="Cell=ServicesA", logger=myLogger)

	attrNames = myJDBCResourceManager.getAttributeNames()
	myresults = myJDBCResourceManager.getJDBCAttributesList()
	#rIndex = 0
	#for rowAttrList in myresults:
	#	#myLogger.logIt( "main(): rowAttrList=" + str( rowAttrList ) + "\n" )
	#	for myAttr in rowAttrList:
	#		k = myAttr.getName()
	#		v = myAttr.getValue()
	#		myLogger.logIt( "main(): rIndex=" + str( rIndex ) + "-->" + str( k ) + "=" + str( v ) + "\n" )
	#	#Endfor
	#	rIndex += 1
	##Endfor
	myJDBCResourceManager.writeAttributes( fileName="/nfs/home4/dmpapp/appd4ec/tmp/denis.tsv" )
	myJDBCResourceManager.printTabFormattedAttributes()
	myJDBCResourceManager.printAttributes()

	#myJDBCResourceManager.saveSession( False )

	myJDBCResourceManager.closeMe()
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

