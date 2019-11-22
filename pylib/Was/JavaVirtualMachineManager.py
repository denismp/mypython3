#!/usr/bin/env jython
######################################################################################
##	JavaVirtualMachineManager.py
##
##	Python module for JavaVirtualMachine attributes.
##
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	01/21/2010	Denis M. Putnam		Created.
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

class JavaVirtualMachineManager( AttributeUtils ):
	"""
    JavaVirtualMachineManager class that contains JavaVirtualMachine management methods.
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
		AttributeUtils.__init__( self, configService, scope, type='JavaVirtualMachine', logger=self.logger )
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
	#	parseToJavaList()
	#
	#	DESCRIPTION:
	#		Parse the given string into a java.util.ArrayList object.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def parseToJavaList(self,myString):
		"""Parse the given string into a java.lang.List object.
		   PARAMETERS:
		       myString -- the string to be parsed.  The delimiter is either a ';' or ':'
		                   and must be homogeneous.  No mixing ';' and ':'.
		   RETURN:
		      An instance of java.util.ArrayList or None.
		"""
		################################################################
		#	Log the parameters.
		################################################################
		self.debug( __name__ + ".parseToJavaList(): called.\n" )
		self.debug( __name__ + ".parseToJavaList(): myString=" + str( myString ) + "\n" )
		rList= ArrayList()
		myAr = list()
		myAR = myString.split( ';' )
		if myAR is None:
			myAR = myString.split( ':' )
		if myAR is None: return rList
		for token in myAR:
			rList.add( token )
		#Endfor
		return rList
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	modifyJavaVirtualMachine()
	#
	#	DESCRIPTION:
	#		Modify the JavaVirtualMachine attributes.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def modifyJavaVirtualMachine( 
							self, 
							bootClasspath='',
							classpath='',
							debugArgs='-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=7777',
							debugMode=False,
							disableJIT=False,
							executableJarFileName='',
							genericJvmArguments='',
							runHProf=False,
							hprofArguments='',
							initialHeapSize=128,
							maximumHeapSize=256,
							internalClassAccessMode='ALLOW',
							osName='aix',
							verboseModeClass=False,
							verboseModeGarbageCollection=False,
							verboseModeJNI=False
							):
		"""Modify the JavaVirtualMachine attributes.
		   PARAMETERS:
		       bootClasspath                   -- Some JVMs contain an option to specify bootstrap classes and resources. 
                                                  This property can contain multiple paths separated by colons (":") or 
                                                  semicolons (";") depending on the operating system of the node.
		       classpath                       -- The standard classpath in which the Java virtual machine looks for 
                                                  classes. This property can contain multiple paths separated by 
                                                  colons (":") or semicolons (";") depending on the operating system of the node. 
		       debugArgs                       -- When Debug Mode for the Java virtual machine is enabled, this 
                                                  property allows additional debug arguments to be passed to the Java 
                                                  virtual machine.
		       debugMode                       -- Enables the JVM debug output. When the property is set, the 
                                                  application server will start with the java_g -debug argument, 
                                                  which is necessary to allow the Distributed Debugger, or any 
                                                  Java debugger, to attach to the application server. Selecting 
                                                  this setting is necessary, but not sufficient, for using the 
                                                  IBM Distributed Debugger to debug code running on this application 
                                                  server. You must also configure and enable the Object Level Trace 
                                                  settings and perform some other steps. See the InfoCenter for 
                                                  more information.
		       disableJIT                      -- Diables the Just In Time (JIT) compiler option of the JVM.
		       executableJarFileName           -- The file path to an executable JAR file.
		       genericJvmArguments             -- Additional command line arguments for the JVM.
		       runHProf                        -- Enable HProf profiler support. To use another profiler, use the 
                                                  command line property to specify settings for the custom profiler.
		       hprofArguments                  -- Additional profiler arguments to use when Run HProf is used. 
		       initialHeapSize                 -- Specifies the initial heap size available to the JVM, in megabytes.
		       maximumHeapSize                 -- The maximum heap size available to the JVM, in megabytes. 
		       internalClassAccessMode         -- This field governs the behaviour of the classloading mechanism 
                                                  of the application server in question. The applications hosted 
                                                  in this particular server will or will not be able to load the 
                                                  classes that are internal to the server, ie., are part of the 
                                                  server implementation, depending on the mode that has been set. 
		       osName                          -- JVM Settings specific to a given operating system. The process 
                                                  launcher will use the JVM settings for the os platform of the node.
		       verboseModeClass                -- Enables verbose debugging output for class loading.
		       verboseModeGarbageCollection    -- Enables verbose debug output for garbage collection.
			   verboseModeJNI                  -- Enables verbose debugging output for native method invocation.
		   RETURN:
		       True if successful, or False.
		"""
		self.debug( __name__ + ".modifyJavaVirtualMachine(): bootClasspath=" + str( bootClasspath ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): classpath=" + str( classpath ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): debugArgs=" + str( debugArgs ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): debugMode=" + str( debugMode ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): disableJIT=" + str( disableJIT ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): executableJarFileName=" + str( executableJarFileName ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): genericJvmArguments=" + str( genericJvmArguments ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): runHProf=" + str( runHProf ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): hprofArguments=" + str( hprofArguments ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): initialHeapSize=" + str( initialHeapSize ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): maximumHeapSize=" + str( maximumHeapSize ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): internalClassAccessMode=" + str( internalClassAccessMode ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): osName=" + str( osName ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): verboseModeClass=" + str( verboseModeClass ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): verboseModeGarbageCollection=" + str( verboseModeGarbageCollection ) + "\n" )
		self.debug( __name__ + ".modifyJavaVirtualMachine(): verboseModeJNI=" + str( verboseModeJNI ) + "\n" )

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
			self.debug( __name__ + ".modifyJavaVirtualMachine(): configObject=" + str( configObject ) + "\n" )
			self.debug( __name__ + ".modifyJavaVirtualMachine(): configObject type=" + str( type( configObject ) ) + "\n" )

			########################################################
			#	Get the JavaVirtualMachine AttributeList
			########################################################
			javaVirtualMachineAttributeList	= self.configService.getAttributes( self.configService.session, configObject, None, True )

			self.debug( __name__ + ".modifyJavaVirtualMachine(): BEFORE javaVirtualMachineAttributeList=" + str( javaVirtualMachineAttributeList ) + "\n" )
			self.debug( __name__ + ".modifyJavaVirtualMachine(): BEFORE javaVirtualMachineAttributeList type=" + str( type( javaVirtualMachineAttributeList ) ) + "\n" )

			#######################################################
			#	Set the scalar JavaVirtualMachine AttributeList values.
			#######################################################
			bootClassPathList = self.parseToJavaList( str( bootClasspath ) )
			classPathList = self.parseToJavaList( str( classpath ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'bootClasspath', bootClassPathList )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'classpath', classPathList )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'debugArgs', str( debugArgs ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'debugMode', java.lang.Boolean( debugMode ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'disableJIT', java.lang.Boolean( disableJIT ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'executableJarFileName', str( executableJarFileName ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'genericJvmArguments', str( genericJvmArguments ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'runHProf', java.lang.Boolean( runHProf ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'hprofArguments', str( hprofArguments ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'initialHeapSize', int( initialHeapSize ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'maximumHeapSize', int( maximumHeapSize ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'internalClassAccessMode', str( internalClassAccessMode ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'osName', str( osName ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'verboseModeClass', java.lang.Boolean( verboseModeClass ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'verboseModeGarbageCollection', java.lang.Boolean( verboseModeGarbageCollection ) )
			self.configService.configServiceHelper.setAttributeValue( javaVirtualMachineAttributeList, 'verboseModeJNI', java.lang.Boolean( verboseModeJNI ) )
			self.debug( __name__ + ".modifyJavaVirtualMachine(): AFTER javaVirtualMachineAttributeList=" + str( javaVirtualMachineAttributeList ) + "\n" )
			####################################################################
			#	Save the javaVirtualMachineAttributeList to the current session.
			####################################################################
			self.configService.setAttributes( self.configService.session, configObject, javaVirtualMachineAttributeList )
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
	myLogger	= MyLogger( LOGFILE="/tmp/JavaVirtualMachineManager.log", STDOUT=True, DEBUG=True )
	#myLogger	= MyLogger( LOGFILE="/tmp/JavaVirtualMachineManager.log", STDOUT=True, DEBUG=False )
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
	templateListManager	= TemplateListManager( configService, type="JavaVirtualMachine", logger=myLogger )
	myJavaVirtualMachineManager	= JavaVirtualMachineManager( adminObject, configService, templateListManager, scope=myscope, logger=myLogger)

	for mylist in myJavaVirtualMachineManager.attributesList:
		myJavaVirtualMachineManager.deepLogOfAttributes( mylist )
	#Endfor
	for mylist in myJavaVirtualMachineManager.attributesList:
		myJavaVirtualMachineManager.deepPrintOfAttributes( mylist )
	#Endfor
	try:
		fileName = "/tmp/denis.txt"
		FH = open( fileName, "w" )
		for mylist in myJavaVirtualMachineManager.attributesList:
			myJavaVirtualMachineManager.deepWriteOfAttributes( mylist, FH )
		#Endfor
		FH.close()
	except Exception, e:
		myLogger.logIt( "main(): " + str( e ) + "\n" )
		raise
	#Endtry

	myJavaVirtualMachineManager.writeAttributes( "/nfs/home4/dmpapp/appd4ec/tmp/JavaVirtualMachine.tsv" )

	########################################################
	#	Make changes.
	########################################################
	rc = myJavaVirtualMachineManager.modifyJavaVirtualMachine( 
							bootClasspath='path1;path2;path3',
							classpath='path1;path2;path3',
							debugArgs='-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=7777',
							debugMode=False,
							disableJIT=False,
							executableJarFileName='',
							genericJvmArguments='',
							runHProf=False,
							hprofArguments='',
							initialHeapSize=128,
							maximumHeapSize=256,
							internalClassAccessMode='ALLOW',
							osName='aix',
							verboseModeClass=False,
							verboseModeGarbageCollection=False,
							verboseModeJNI=False
							)

	if rc: myJavaVirtualMachineManager.saveSession( False )

	#for mylist in myJavaVirtualMachineManager.attributesList:
	#	myJavaVirtualMachineManager.deepLogOfAttributes( mylist )
	##Endfor
	configService.closeMe()
	myJavaVirtualMachineManager.closeMe()
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
