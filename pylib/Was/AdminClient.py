#!/usr/bin/env jython
######################################################################################
##	AdminClient.py
##
##	Python module deals with WAS AdminClient.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	09/21/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.NotificationListener import *
import java.lang.NullPointerException as NullPointerException
import java.lang.NoClassDefFoundError as NoClassDefFoundError
from javax.management import ObjectName
import javax.management.ObjectName
from jarray import array
from java.lang import String
from java.lang import Object

try:
	import com.dmp.was.admin.service.WASAdminClient as WASAdminClient
except ImportError, ie:
	print "Unable to import the WASAdminClient.  Please verify the CLASSPATH."
	exit( 1 )
except NoClassDefFoundError, nce:
	print "Unable to import the WASAdminClient.  Most likely you are not on a WebSphere host. " + str( nce )
	exit( 1 )
#Endtry
import com.ibm.websphere.security.WebSphereRuntimePermission as WebSphereRuntimePermission
import com.ibm.websphere.security.auth.WSLoginFailedException as WSLoginFailedException
import com.ibm.ws.security.util.InvalidPasswordDecodingException as InvalidPasswordDecodingException
import com.ibm.websphere.management.exception.ConnectorException as ConnectorException

class AdminClient():
	"""AdminClient class that contains admin client connection utilities."""

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
				logger=None,
				hostname=None,
				cellName=None,
				port=None,
				username=None,
				password=None,
				type="SOAP"
		):
		"""Class Initializer.
           PARAMETERS:
               logger      - instance of the MyLogger class.
               hostname    - connection host.
               cellName    - connection cell name.
               port        - connection port.
               username    - something like was7admin
               password    - secret
               type        - connection type of either RMI or SOAP.

           RETURN:
               An instance of this class
		"""
		if logger is None: raise Exception, "Please specify the logger instance."
		if hostname is None: 
			self.hostname = socket.gethostname()
		else:
			self.hostname = hostname

		self.logger				= logger
		self.port				= port
		self.username			= username
		self.cellName			= cellName
		self.password			= password
		self.connection_type 	= type
		self.wasAdminClient		= None
		self.connection			= None
		self.logMySelf()
		self.validate()

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createRMIDefault()
	#
	#	DESCRIPTION:
	#		Connect with the RMI protocol using the default WAS values.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		connection
	##################################################################################
	def createRMIDefault(self):
		"""Connect with the RMI protocol using the default WAS values.
           PARAMETERS:

           RETURN:
               connection - AdminClient object returned from the call to createRMIDefault().
		"""
		wasAdminClient	= None
		results			= None
		try:
			wasAdminClient		= WASAdminClient( self.hostname, self.cellName, self.username, self.password, self.port )
			self.connection		= wasAdminClient.createRMIDefault()
			#results			= self.getResults()
			self.wasAdminClient = wasAdminClient
		except ConnectorException, ce:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( ce ) + ".  Make sure that the WAS Manager is running.  Make sure that the WAS Manager is running."
			self.logIt( __name__ + ".createRMIDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		except Exception, e:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( e ) + "."
			self.logIt( __name__ + ".createRMIDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		except NoClassDefFoundError, ne:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( ne ) + "."
			self.logIt( __name__ + ".createRMIDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		except WSLoginFailedException, le:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( le ) + "."
			self.logIt( __name__ + ".createRMIDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		except InvalidPasswordDecodingException, ipe:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( ipe ) + "."
			self.logIt( __name__ + ".createRMIDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		except WebSphereRuntimePermission, wpe:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( wpe ) + "."
			self.logIt( __name__ + ".createRMIDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		#Endtry
		#self.logResults( results )
		return self.connection

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createSOAPDefault()
	#
	#	DESCRIPTION:
	#		Connect with the SOAP protocol using the default WAS values.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		connection
	##################################################################################
	def createSOAPDefault(self):
		"""Connect with the SOAP protocol using the default WAS values.
           PARAMETERS:

           RETURN:
               connection - AdminClient object returned from the call to createSOAPDefault().
		"""
		wasAdminClient	= None
		results			= None
		try:
			wasAdminClient		= WASAdminClient( self.hostname, self.cellName, self.username, self.password, self.port )
			#wasAdminClient.setSoapConnectorSecurityEnabled( "false" )
			self.connection		= wasAdminClient.createSOAPDefault()
			#results			= self.getResults()
			self.wasAdminClient = wasAdminClient
		except ConnectorException, ce:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( ce ) + ".  Make sure that the WAS Manager is running."
			self.logIt( __name__ + ".createSOAPDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		except Exception, e:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( e ) + "."
			self.logIt( __name__ + ".createSOAPDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		except NoClassDefFoundError, ne:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( ne ) + "."
			self.logIt( __name__ + ".createSOAPDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		except WSLoginFailedException, le:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( le ) + "."
			self.logIt( __name__ + ".createSOAPDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		except InvalidPasswordDecodingException, ipe:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( ipe ) + "."
			self.logIt( __name__ + ".createSOAPDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		except WebSphereRuntimePermission, wpe:
			results				= self.getResults()
			self.logResults( results )
			estr = "Unable to connect to WebSphere => " + str( wpe ) + "."
			self.logIt( __name__ + ".createSOAPDefault(): " + str(estr) + "\n" )
			raise Exception( estr ) 
		#Endtry
		#self.logResults( results )
		return self.connection

	##################################################################################
	#Enddef
	##################################################################################

	#######################################################
	#	invoke()
	#
	#	DESCRIPTION:
	#		Invoke the requested cluster operation
	#
	#	PARAMETERS:
	#		See comments.
	#
	#	RETURN:
	#		The return value of the invoked operation.
	#######################################################
	def invoke(self,objectName,operation,parmsArray=None,signatureArray=None):
		"""
		Invoke the requested cluster operation.  Valid operations
		are not checked ahead of the call.
		PARAMETERS:
		    objectName - an instance of javax.management.ObjectName
            operation  - the method to be invoked on objectName
			parmsArray - an array of the parameters to the operation method.
			             Something like [ parmValue1, parmValue2 ]
			signatureArray - an array of the java types of the parameters specified in the parmsArray.
			             Something like [ 'java.lang.String', 'java.lang.Boolean' ]
		RETURN:
		    The return value of the invoked operation.
		"""
		if not isinstance( objectName, javax.management.ObjectName ):
			self.logIt( __name__ + ".invoke(): objectName is not an javax.management.ObjectName type.\n" )
			raise Exception( __name__ + ".invoke(): objectName is not an javax.management.ObjectName type" )
		#Endif
		myparms	= None
		mysigs	= None

		#print type( parmsArray[0] )
		if parmsArray is not None: myparms = array( parmsArray, Object )
		if signatureArray is not None: mysigs	= array( signatureArray, String )
		self.debug( __name__ + ".invoke(): myparms=" + str( myparms ) + '\n' )
		self.debug( __name__ + ".invoke(): mysigs=" + str( mysigs ) + '\n' )
		#print myparms
		#print mysigs
		try:
			return self.connection.invoke( objectName, operation, myparms, mysigs )
		except javax.management.RuntimeMBeanException, e:
			self.logIt( __name__ + ".invoke(): " + str( e ) + '\n' )
			raise Exception( e )
		#Endtry
	#######################################################
	#	Enddef
	#######################################################

	#######################################################
	#	registerListener()
	#
	#	DESCRIPTION:
	#		Register a listener for the given objectName
	#
	#	PARAMETERS:
	#		See comments.
	#
	#	RETURN:
	#		An instance of pylib.Was.NotificationListener.
	#######################################################
	def registerListener(self,objectName,filter=None,handback=None,etype=None):
		"""
		Register a pylib.Was.NotificationListener with WebSphere.  This should
		be done before the invoke() call if you wish to handle notifications.
		Be sure to call <mynotifier>.closeMe() when you are finished with it
		to remove it from WebSphere.
		PARAMETERS:
		    objectName - an instance of javax.management.ObjectName
            filter     - an instance of javax.management.NotificationFilter
			handback   - an instance of java.lang.Object
		RETURN:
		    An instance of pylib.Was.NotificationListener.
		"""
		if not isinstance( objectName, javax.management.ObjectName ):
			self.logIt( __name__ + ".registerListener(): objectName is not an javax.management.ObjectName type.\n" )
			raise Exception( __name__ + ".registerListener(): objectName is not an javax.management.ObjectName type" )
		#Endif
		myNotifier	= NotificationListener()
		if etype is None:
			myNotifier.registerNotificationListener( self.connection, objectName, myNotifier, filter, handback )
		else:
			myNotifier.registerNotificationListener( self.connection, objectName, myNotifier, filter, handback, etype )
		return myNotifier
	#######################################################
	#	Enddef
	#######################################################

	##################################################################################
	#	getResults()
	#
	#	DESCRIPTION:
	#		Get the results of the connection attempt.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		results array
	##################################################################################
	def getResults(self):
		"""Log the results of the connection attempt.
           PARAMETERS:

           RETURN:
               results - array returned from the WASAdminClient()
		"""
		if self.wasAdminClient != None:
			return self.wasAdminClient.getResults()
		else:
			return ""

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	logResults()
	#
	#	DESCRIPTION:
	#		Validate the parameters and calculated values.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		True for valid.
	##################################################################################
	def logResults(self, results):
		"""Log the results of the connection attempt.
           PARAMETERS:
               results - array returned from the WASAdminClient()

           RETURN:
		"""
		for value in results:
			self.logIt( __name__ + ".logResults(): " + str( value ) + "\n" ) 
		#Endfor

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
	myLogger	= MyLogger( LOGFILE="/tmp/AdminClient.log", STDOUT=True, DEBUG=True )
	myObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1", cellName='cellA' )
	try:
		myclient	= myObject.createSOAPDefault()
		results		= myObject.getResults()
		myObject.logResults( results )
		myObject.closeMe()
	except:
		myLogger.logIt( "main(): Unable to connect to the AdminClient().  Make sure that the WebSphere Server Manager is running.\n" )
	#Endfi
	##################################################################################
	#Enddef
	##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
	main()

