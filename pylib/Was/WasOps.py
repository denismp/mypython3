#!/usr/bin/env jython
######################################################################################
##	WasOps.py
##
##	Python module deals with WAS WasOps.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	09/21/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
import shutil
from datetime import *
import time
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.Was.WasProperties import *
from pylib.Was.Utils import *
##import com.dmp.wdt.scripts.ant.WSTInit
#import com.dmp.wdt.scripts.ant as ant
#import org.apache.tools.ant.BuildException
##import org.apache.tools.ant.Project as antToolsProject
#import org.apache.tools.ant as antTools
import java.lang.NullPointerException
import java.lang.UnsupportedClassVersionError
import com.dmp.wdt.common.property.PropertyFileNotFoundException
import com.dmp.wdt.scripts.services.ScriptServiceException

class WasOps( Utils ):
	"""WasOps class that contains with the WAS operations."""

	##################################################################################
	#	__init__()
	#
	#	DESCRIPTION:
	#		Class initializer.
	#
	#	PARAMETERS:
	#		domain	        - something like "V6_DEV|LAB|QUAL|PROD"
	#		properties_file - name of the properties file.  something like: '/nfs/dist/dmp/WDT/PROD/bin/v6/ant/build_v6.properties'
	#		processCallBack - function callback reference.
	#		mnemonic        - entity mmemonic.
	#		entity          - typically the application name, but it could be a cluster.
	#
	#	RETURN:
	#		An instance of this class
	##################################################################################
	def __init__(
				self, 
				logger=None,
				properties_file=None,
				processCallBack=None,
				domain=None,
				mnemonic=None,
				entity=None
		):
		"""Class Initializer.
           PARAMETERS:
               logger          - instance of the MyLogger class.
               properties_file - name of the properties file.  something like: '/dmp/WDT/bin/v6/ant/build_v6.properties'
               processCallBack - function callback reference.
               domain          - something like V6_PROD
               mnemonic        - entity mnemonic.
               entity          - typically the application name, but it could be a cluster.

           RETURN:
               An instance of this class
		"""
		if logger is None: raise Exception, "Please specify the logger instance."
		if domain is None: raise Exception, "Please specify the domain."
		if entity is None: raise Exception, "Please specify the entity."

		self.mnemonic 	= mnemonic
		self.entity		= entity
		properties		= WasProperties( domain=domain, logger=logger, properties_file=properties_file )
		Utils.__init__( self, logger=logger, env=properties, processCallBack=processCallBack )
		setattr( self.env, "install_mnemonic", mnemonic )
		setattr( self.env, "install_domain", domain )
		setattr( self.env, "install_entity_name", entity )
		setattr( self.env, "install_type", "INSTALL" )
		setattr( self.env, "install_serviceType", None )
		setattr( self.env, "install_hostName", self.hostname )

		myres = re.match( '^(\D)(\d)', str( self.env.getDomainVersion() ) )
		myversion = str( myres.group(2) )
		if myversion != '6' and myversion != '5':
			self.userid = "was" + myversion + "0"
			self.cell_type = "CELL_V" + myversion
			self.node_type = "NODE_V" + myversion
		elif self.env.getDomainVersion() == 'v6':
			self.userid = 'was60'
			self.cell_type = 'CELL_V6'
			self.node_type = 'NODE_V6'
		elif self.env.getDomainVersion() == 'v5':
			self.userid = 'was5'
			self.cell_type = 'CELL'
			self.node_type = 'NODE'
		else:
			self.logIt( __name__ + ".__init__(): Unsupported WAS domain=>" + str( self.env.getDomainVersion() ) + "\n" )
			raise Exception, "Unsupported WAS domain=>" + str( self.env.getDomainVersion() )
		#Endif
		setattr( self.env, "install_userid", self.userid )
		setattr( self.env, "install_cell_type", self.cell_type )
		setattr( self.env, "install_node_type", self.node_type )
		self.global_init()
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
			if re.search( '__doc__',  attr ): continue
			#if re.search( '__module__',  attr ): continue
			if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
			#if re.search( 'instance', str( getattr( self, attr ) ) ): continue
			if( debugOnly == True ):
				self.debug( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
			else:
				self.logIt( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
			#Endif
		#Endfor
		#self.env.logMySelf( debugOnly=debugOnly )

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	global_init()
	#
	#	DESCRIPTION:
	#		Initialize the global build variables.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def global_init(self):
		"""
        Initialize the global build variables.
        PARAMETERS:
        RETURN:
		"""
		mymsg = """
        In the following needs to be accomplished:
            1.    Evalutate the serviceType
                  Service type for all was config operations would be CELL which means
                  that the configuration can happen only from the deployment manager host.
                  Service type for all control operations would be CELL,NODE which means
                  that the configuration can happen either on the deployment manager host or any
                  node that belongs to the cell.
            2.    The ant task would essentially determine if the host is valid for the
                  operation in the domain specified.
            3.    We are no longer using ant, but the above tasks still need to be done
                  by this class.
		"""
		self.logIt( __name__ + ".global_init(): " + mymsg + "\n" )
		setattr( self.env, "version", "1.0" )
		setattr( self.env, "was_deploymentManagerDown", self.env.DEPLOYMENT_MANAGER_DOWN )
		setattr( self.env, "build_debug", "on" )
		setattr( self.env, "build_optimize", "off" )
		setattr( self.env, "ant-contrib-jar", "lib/ant-contrib-0.1.jar" )
		setattr( self.env, "taskdef_resource", "net/sf/antcontrib/antcontrib.properties" )
		setattr( self.env, "taskdef_resource_classpath", self.env.dmp_custom_tasks_classpath )
		
		setattr( self.env, "taskdef_deploymentLogger", "deploymentLogger" )
		setattr( self.env, "taskdef_deploymentLogger_classname", "com.dmp.wdt.scripts.ant.DeploymentLogger" )
		setattr( self.env, "taskdef_deploymentLogger_classpath", self.env.dmp_custom_tasks_classpath )
		
		setattr( self.env, "taskdef_configurationGenerator", "configurationGenerator" )
		setattr( self.env, "taskdef_configurationGenerator_classname", "com.dmp.wdt.scripts.ant.DeploymentConfigurationGenerator" )
		setattr( self.env, "taskdef_configurationGenerator_classpath", self.env.dmp_custom_tasks_classpath )

		setattr( self.env, "taskdef_initWst", "initWst" )
		setattr( self.env, "taskdef_initWst_classname", "com.dmp.wdt.scripts.ant.WSTInit" )
		setattr( self.env, "taskdef_initWst_classpath", self.env.dmp_custom_tasks_classpath )

		setattr( self.env, "taskdef_queryControl", "queryControl" )
		setattr( self.env, "taskdef_queryControl_classname", "com.dmp.wdt.scripts.ant.GenericReportingTask" )
		setattr( self.env, "taskdef_queryControl_classpath", self.env.dmp_custom_tasks_classpath )

		setattr( self.env, "taskdef_lockUtil", "lockUtil" )
		setattr( self.env, "taskdef_lockUtil_classname", "com.dmp.wdt.scripts.ant.LockTask" )
		setattr( self.env, "taskdef_lockUtil_classpath", self.env.dmp_custom_tasks_classpath )

		setattr( self.env, "taskdef_cssUtil", "cssUtil" )
		setattr( self.env, "taskdef_cssUtil_classname", "com.dmp.wdt.scripts.ant.LockTask" )
		setattr( self.env, "taskdef_cssUtil_classpath", self.env.dmp_custom_tasks_classpath )

		setattr( self.env, "taskdef_webServerPluginUtil", "webServerPluginUtil" )
		setattr( self.env, "taskdef_webServerPluginUtil_classname", "com.dmp.wdt.scripts.ant.WebServerPluginLevel" )
		setattr( self.env, "taskdef_webServerPluginUtil_classpath", self.env.dmp_custom_tasks_classpath )

		setattr( self.env, "was_initReturnCode", "0" )
		setattr( self.env, "was_deploymentId", "NULL" )
		setattr( self.env, "was_hostServiceType", "NULL" )
		try:
			if self.env.was_mnemonic is None:
				setattr( self.env, "was_mnemonic", "" )
		except AttributeError, e:
			setattr( self.env, "was_mnemonic", "" )
		#Endtry
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	init()
	#
	#	DESCRIPTION:
	#		Initialize the build.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		True for success or False
	##################################################################################
	def init(self):
		"""
        Initialize the build.  This method is called by each 'action'
        PARAMETERS:
        RETURN:
            True for success or False
		"""
		setattr( self.env, "was_domain", self.env.install_domain )
		setattr( self.env, "was_entityName", self.env.install_entity_name )
		setattr( self.env, "was_mnemonic", self.env.install_mnemonic )
		try:
			if self.env.was_mnemonic is None:
				setattr( self.env, "was_mnemonic", "" )
		except AttributeError, e:
			setattr( self.env, "was_mnemonic", "" )
		#Endtry
		setattr( self.env, "was_mnemonicLowerCase", str( self.env.install_mnemonic ).lower() )
		setattr( self.env, "was_installTypeName", self.env.install_type )
		setattr( self.env, "was_serviceType", self.env.install_serviceType )
		setattr( self.env, "was_hostName", self.env.install_hostName )
		setattr( self.env, "was_hostServiceType", self.node_type )
		setattr( self.env, "was_isProcessAppMgmtUpdate", self.env.UPDATE_PROCESS_RUNNING )
		setattr( self.env, "was_mneServerConfigDir", "/dmp/logs/" + str( self.env.was_mnemonic ) )
		setattr( self.env, "was_isEmergency", str( self.env.USE_DB ) )
		setattr( self.env, "was_useDBRepositoryForAppInstall", self.env.GENERATE_XML  )
		setattr( self.env, "was_updatekey", self.env.UPDATEKEY  )
		setattr( self.env, "was_wdtHome", self.env.WDT_HOME  )
		setattr( self.env, "was_wdtEnvironment", self.env.WDT_ENVIRONMENT.lower() )
		setattr( self.env, "was_statusCodeFile", self.env.STATUS_TMP_FILE )
		setattr( self.env, "was_domainVersion", self.env.DOMAIN_VERSION )
		setattr( self.env, "was_dmpscripts_home", self.env.was_wdtHome + "/bin/" + self.env.was_domainVersion + "/jacl" )

		setattr( self.env, "was_dbErrorMessageUpdateEntry", 'false' )
		setattr( self.env, "was_dbErrorMessageCreateEntry", 'false' )
		setattr( self.env, "was_dbErrorFlagUpdateEntry", 'false' )
		setattr( self.env, "was_dbErrorFlagCreateEntry", 'false' )
		setattr( self.env, "was_runDeployment", 'true' )
		setattr( self.env, "was_lockEnable", 'true' )
		setattr( self.env, "was_cellname", 'BOGUS' )
		setattr( self.env, "was_dbErrorMessageUpdateEntry", 'Empty' )
		setattr( self.env, "was_deploymentStatus", '' )
		setattr( self.env, "was_deploymentHasError", 'false' )
		setattr( self.env, "was_wsadminHostName", self.env.install_hostName )
		setattr( self.env, "was_nodeSpecificOperation", 'false' )
		setattr( self.env, "was_wsadminRMIConnectorPort", '' )
		setattr( self.env, "was_configGenerationReturnCode", '0' )
		setattr( self.env, "was_clusterName", 'MY_CLUSTER_NAME' )
		setattr( self.env, "was_wsadminSoapConnectoryPort", '9999' )
		setattr( self.env, "was_wsadminRMIConnectoryPort", '8888' )
		setattr( self.env, "was_deploymentManagerHomeDirectory", '/dmp/WDT' )
		setattr( self.env, "was_nodeNameToDeploy", 'MY_NODE' )
		setattr( self.env, "was_entityStatus", '0' )
		setattr( self.env, "was_deploymentConfigFile", '' )
		setattr( self.env, "was_deployableApplication", 'false' )
		setattr( self.env, "was_handleGeneratedConfigFile", 'NO_ACTION' )

		self.logIt( __name__ + ".init(): Initializing the build.\n" )
		self.logIt( __name__ + ".init(): Mnemonic=" + str( self.env.install_mnemonic ) + "\n" )
		self.logIt( __name__ + ".init(): Domain=" + str( self.env.install_domain ) + "\n" )
		self.logIt( __name__ + ".init(): Entity Name=" + str( self.env.install_entity_name ) + "\n" )
		self.logIt( __name__ + ".init(): Install Type=" + str( self.env.install_type ) + "\n" )
		self.logIt( __name__ + ".init(): Install Host Name=" + str( self.env.install_hostName ) + "\n" )
		self.logIt( __name__ + ".init(): was_wdtEnvironment=" + str( self.env.was_wdtEnvironment ) + "\n" )
		self.logIt( __name__ + ".init(): was_dmpscripts_home=" + str( self.env.was_dmpscripts_home ) + "\n" )

		if self.env.was_wdtEnvironment.lower() == 'prod':
			self.env.was_wsadminCustomClasspath = self.env.was_wsadminCustomClasspathProd
			self.env.was_clustertemplate = self.env.was_clustertemplateProd
		elif self.env.was_wdtEnvironment.lower() == "dev":
			self.env.was_wsadminCustomClasspath = self.env.was_wsadminCustomClasspathDev
			self.env.was_clustertemplate = self.env.was_clustertemplateDev
		else:
			self.debug( __name__ + ".init(): Do not currently have a wsadminCustomClasspathQual\n" )	
		#Endif
		self.logIt( __name__ + ".init(): was_wsadminCustomClasspath=" + str( self.env.was_wsadminCustomClasspath ) + "\n" )
		self.logIt( __name__ + ".init(): was_clustertemplate=" + str( self.env.was_clustertemplate ) + "\n" )

		#setattr( self.env, "was_applicationConfigFile", '/dmp/' + str( self.env.was_mnemonic ) + "/admin/" + self.env.was_entityName + "." + self.env.was_domain + ".xml" )
		#self.logIt( __name__ + ".init(): Config file=" + str( self.env.was_applicationConfigFile ) + "\n" )
		self.logIt( __name__ + ".init(): Generate XML=" + str( self.env.was_useDBRepositoryForAppInstall ) + "\n" )

		#######################################################
		#	Determine the service type.
		#	NOTE: Logically this is reduced to the last
		#	first level else.  The current if/else is
		#	faithful to what is in the build.xml file, but it 
		#	should be reduced.
		#######################################################
		if self.env.was_mnemonic == "WDT":
			self.env.was_loggerServiceImpl = self.env.was_deploymentServiceDAOImpl
			self.env.was_scriptServiceImpl = self.env.was_deploymentServiceDAOImpl
		elif self.env.was_serviceType == "WEB_SERVER":
			self.env.was_loggerServiceImpl = self.env.was_deploymentServiceDAOImpl
			self.env.was_scriptServiceImpl = self.env.was_deploymentServiceDAOImpl
		elif self.env.was_entityName == "cl_mtstools":
			self.env.was_loggerServiceImpl = self.env.was_deploymentServiceDAOImpl
			self.env.was_scriptServiceImpl = self.env.was_deploymentServiceDAOImpl
		elif self.env.was_entityName == "cl_mtstools_lab":
			self.env.was_loggerServiceImpl = self.env.was_deploymentServiceDAOImpl
			self.env.was_scriptServiceImpl = self.env.was_deploymentServiceDAOImpl
		else:
			##################################################
			#	This is what really ever happens.
			##################################################
			if self.env.was_isEmergency == 'TRUE':
				self.logIt( __name__ + ".init(): Emergency Flag High...\n" )

				self.env.was_loggerServiceImpl = self.env.was_deploymentServiceDAOImpl
				self.env.was_scriptServiceImpl = self.env.was_deploymentServiceDAOImpl
			else:
				self.env.was_loggerServiceImpl = self.env.was_deploymentServiceEJBImpl
				self.env.was_scriptServiceImpl = self.env.was_deploymentServiceEJBImpl
			#Endif
		#Endif
		self.env.was_loggerServiceImpl = self.env.was_deploymentServiceDAOImpl
		self.env.was_scriptServiceImpl = self.env.was_deploymentServiceDAOImpl

		self.logIt( __name__ + ".init(): Logger Service Implementation=" + str( self.env.was_loggerServiceImpl ) + "\n" )
		self.logIt( __name__ + ".init(): Script Service Implementation=" + str( self.env.was_scriptServiceImpl ) + "\n" )
		value = self.initWst()
		return value
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	initWst()
	#
	#	DESCRIPTION:
	#		Initialize the Wst.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		True for success or False
	##################################################################################
	def initWst(self):
		"""
        Initialize the Wst.  This method is called by each 'action'
        In the init procedure the following needs to be accomplished:
            1.    evalutate the serviceType
                  Service type for all was config operations would be CELL which means
                  that the configuration can happen only from the deployment manager host.
                  Service type for all control operations would be CELL,NODE which means
                  that the configuration can happen either on the deployment manager host or any
                  node that belongs to the cell.
            2.    the ant task would essentially determine if the host is valid for the
                  operation in the domain specified.
        PARAMETERS:
        RETURN:
            True for success or False
		"""
		
		###########################################################################
		#	Call the initWst java class to do the comments above.
		###########################################################################
		self.logIt( __name__ + ".initWst(): was_serviceType=" + str( self.env.was_serviceType ) + ".\n" )
		self.logIt( __name__ + ".initWst(): Call the initWst java class to determine if this a node specific operation.\n" )
		self.env.initWst_domain 					= self.env.was_domain
		self.env.initWst_serviceType 				= self.env.was_serviceType
		#self.env.initWst_serviceType 				= "APP_SERVER_V6"
		self.env.initWst_scriptServiceImpl 			= self.env.was_scriptServiceImpl
		#self.env.initWst_hostName 					= "dapp41"
		self.env.initWst_hostName 					= self.env.was_hostName
		self.env.initWst_processReturnCodeProperty	= "was.initReturnCode"
		self.env.initWst_processResultProperty 		= "was.initResult"
		self.env.initWst_deploymentIdProperty 		= "was.deploymentId"
		self.env.initWst_hostServiceTypeProperty	= "was.hostServiceType"

		if True:
			######################################################################
			#	Set up the WSTInit() class instance.
			######################################################################
			initWst = ant.WSTInit()
			initWst.setDomain( self.env.was_domain )
			initWst.setServiceType( self.env.initWst_serviceType )
			initWst.setScriptServiceImpl( self.env.initWst_scriptServiceImpl )
			initWst.setHostName( self.env.initWst_hostName )
			initWst.setProcessReturnCodeProperty( self.env.initWst_processReturnCodeProperty )
			initWst.setProcessResultProperty( self.env.initWst_processResultProperty )
			initWst.setDeploymentIdProperty( self.env.initWst_deploymentIdProperty )
			initWst.setHostServiceTypeProperty( self.env.initWst_hostServiceTypeProperty )

			######################################################################
			#	Set up the ant project needed by Task() class.
			######################################################################
			#antProject = org.apache.tools.ant.Project()
			antProject	= antTools.Project()
			antProject.setName( "wsad" )
			initWst.setProject( antProject )

			try:
				##################################################################
				#	Execute the ant Task.
				##################################################################
				initWst.execute()

				##################################################################
				#	Get the 'return' properties.
				##################################################################
				self.env.was_deploymentId		= antProject.getProperty( self.env.initWst_deploymentIdProperty )
				self.env.was_hostServiceType	= antProject.getProperty( self.env.initWst_hostServiceTypeProperty )
				self.env.was_initReturnCode		= antProject.getProperty( self.env.initWst_processReturnCodeProperty )
				self.env.was_initResult			= antProject.getProperty( self.env.initWst_processResultProperty )
			except org.apache.tools.ant.BuildException, be:
				self.logIt( __name__ + ".initWst(): " + str( be ) + "\n" )
				self.env.was_initReturnCode		= '1'
				self.env.was_initResult			=  __name__ + ".initWst(): " + str( be )
				self.env.was_deploymentId		= 'NULL'
				self.env.was_hostServiceType	= 'NULL'
			except com.dmp.wdt.common.property.PropertyFileNotFoundException, pnfe:
				self.logIt( __name__ + ".initWst(): " + str( pnfe ) + "\n" )
				self.env.was_initReturnCode		= '1'
				self.env.was_initResult			=  __name__ + ".initWst(): " + str( pnfe )
				self.env.was_deploymentId		= 'NULL'
				self.env.was_hostServiceType	= 'NULL'
			except com.dmp.wdt.scripts.services.ScriptServiceException, sse:
				self.logIt( __name__ + ".initWst(): " + str( sse ) + "\n" )
				self.env.was_initReturnCode		= '1'
				self.env.was_initResult			=  __name__ + ".initWst(): " + str( sse )
				self.env.was_deploymentId		= 'NULL'
				self.env.was_hostServiceType	= 'NULL'
			except java.lang.NullPointerException, ne:
				self.logIt( __name__ + ".initWst(): " + str( ne ) + "\n" )
				self.env.was_initReturnCode		= '1'
				self.env.was_initResult			=  __name__ + ".initWst(): " + str( ne )
				self.env.was_deploymentId		= 'NULL'
				self.env.was_hostServiceType	= 'NULL'
			except java.lang.Exception, e:
				self.logIt( __name__ + ".initWst(): " + str( e ) + "\n" )
				self.env.was_initReturnCode		= '1'
				self.env.was_initResult			=  __name__ + ".initWst(): " + str( e )
				self.env.was_deploymentId		= 'NULL'
				self.env.was_hostServiceType	= 'NULL'
			#Endtry
		else:
			###########################################################################
			#	Fake the results.
			###########################################################################
			self.env.was_initReturnCode = '0'
			self.env.was_initResult		= 'This was faked in the initWst() function.'
			self.env.was_deploymentId	= 'MYID set in initWst()'
			self.env.was_hostServiceType= 'NODE_V6'
		#Endif

		if self.env.was_initReturnCode == "0":
			self.env.was_initSuccess = "true"
			self.logIt( __name__ + ".initWst(): Initialization successfull.....Deployment Id = " + str( self.env.was_deploymentId ) + " ...Host Type = " + str( self.env.was_hostServiceType ) + "\n" )
			################################################################
			#	SET isoperationNodeSpecific to true for all nodes in which
			#	a cell is defined.  Eventually this code will be replaced
			#	since it is an emergency fix.
			################################################################
			if self.env.was_hostName.lower() == 'tpdwpsutil11':
				self.env.was_isOperationNodeSpecific = 'true'
			elif self.env.was_hostName.lower() == 'dwpsutil11':
				self.env.was_isOperationNodeSpecific = 'true'
			elif self.env.was_hostServiceType == 'NODE':
				self.env.was_isOperationNodeSpecific = 'true'
			elif self.env.was_hostServiceType == 'NODE_V6':
				self.env.was_isOperationNodeSpecific = 'true'
			else:
				self.env.was_isOperationNodeSpecific = 'false'
			#Endif
		else:
			self.logIt( __name__ + ".initWst(): Return Code=" + str( self.env.was_initReturnCode )  + "\n" )
			self.logIt( __name__ + ".initWst(): Initialization failed due to :" + str( self.env.was_initResult )  + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".initWst(): Initialization failed due to :" + str( self.env.was_initResult )
			return False
		#Endif
		self.logIt( __name__ + ".initWst(): was_isOperationNodeSpecific=" + str( self.env.was_isOperationNodeSpecific )  + "\n" )
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	evaluateInstallType()
	#
	#	DESCRIPTION:
	#		Initialize the Wst.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		True for success or False
	##################################################################################
	def evaluateInstallType(self):
		"""
        Evaluate the install type.  This method is called by each 'action'
        and sets up all the variables for the actions to carry out their work.
        PARAMETERS:
        RETURN:
            True for success or False
		"""
		result = self.init()
		if not result:
			self.logIt( __name__ + ".evaluateInstallType(): init() failed.\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".evaluateInstallType(): failed."
			return False
		#Endif
		self.logIt( __name__ + ".evaluateInstallType(): Install type is " + str( self.env.was_installTypeName ) + "\n" )
		self.logIt( __name__ + ".evaluateInstallType(): was_isProcessAppMgmtUpdate=" + str( self.env.was_isProcessAppMgmtUpdate ) + "\n" )
		
		if self.env.was_isOperationNodeSpecific.lower() == 'true':
			if self.env.was_isProcessAppMgmtUpdate.lower() == 'true':
				self.env.was_stopDeploymentProcess = 'true'
			else:
				self.env.was_stopDeploymentProcess = 'false'
			#Endif
		else:
			self.env.was_stopDeploymentProcess = 'false'
		#Endif
		if self.env.was_stopDeploymentProcess.lower() == 'true':
			self.logIt( __name__ + ".evaluateInstallType(): --------------Summary-------------\n" )
			self.logIt( __name__ + ".evaluateInstallType(): Deployment of " + str( self.was_entityName ) + " stopped because the host " + str( self.env.was_hostName ) + " is not valid.\n" )
			self.logIt( __name__ + ".evaluateInstallType(): ----------------------------------\n" )
		elif self.env.was_installTypeName == 'INSTALL_APPLICATION':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'INSTALL_APPLICATION'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'APPLICATION'
			self.env.was_generatePlugin					= 'TRUE'
			if self.env.was_useDBRepositoryForAppInstall.lower() == 'true':
				self.env.was_generateConfigurationFile	= 'true'
				self.env.was_handleGenerateConfigFile	= 'SAVE_TO_APP_LOCATION'
			else:
				self.env.was_generateConfigurationFile	= 'false'
				self.env.was_handleGenerateConfigFile	= 'NO_ACTION'
			#Endif
			self.env.ant_call_target 					= 'configureApplication'
		elif self.env.was_installTypeName == 'DELETE_DATASOURCES':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'DELETE_DATASOURCES'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'APPLICATION'
			self.env.was_generatePlugin					= 'FALSE'
			if self.env.was_useDBRepositoryForAppInstall.lower() == 'true':
				self.env.was_generateConfigurationFile	= 'false'
				self.env.was_handleGenerateConfigFile	= 'SAVE_TO_APP_LOCATION'
			else:
				self.env.was_generateConfigurationFile	= 'false'
				self.env.was_handleGenerateConfigFile	= 'NO_ACTION'
			#Endif
			self.env.ant_call_target 					= 'deleteDataSources'
		elif self.env.was_installTypeName == 'UNINSTALL_APPLICATION':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'UNINSTALL_APPLICATION'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'APPLICATION'
			self.env.was_generatePlugin					= 'TRUE'
			if self.env.was_useDBRepositoryForAppInstall.lower() == 'true':
				self.env.was_generateConfigurationFile	= 'true'
				self.env.was_handleGenerateConfigFile	= 'KEEP'
			else:
				self.env.was_generateConfigurationFile	= 'false'
				self.env.was_handleGenerateConfigFile	= 'NO_ACTION'
			#Endif
			self.env.ant_call_target 					= 'configureApplication'
		elif self.env.was_installTypeName == 'RECREATE_CLUSTER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'RECREATE_CLUSTER'
			self.env.was_deploymentApplication			= 'NULL'
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'TRUE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'KEEP'
			self.env.ant_call_target 					= 'configureCluster'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'CREATE_CLUSTER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'CREATE_CLUSTER'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'KEEP'
			self.env.ant_call_target 					= 'configureCluster'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'UPDATE_CLUSTER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'UPDATE_CLUSTER'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'KEEP'
			self.env.ant_call_target 					= 'configureCluster'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'ADD_JDBC_PROVIDER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'ADD_JDBC_PROVIDER'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'KEEP'
			self.env.ant_call_target 					= 'configureCluster'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'RECREATE_JDBC_PROVIDER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'RECREATE_JDBC_PROVIDER'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'KEEP'
			self.env.ant_call_target 					= 'configureCluster'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'REMOVE_CLUSTER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'REMOVE_CLUSTER'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'KEEP'
			self.env.ant_call_target 					= 'configureCluster'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'REMOVE_CLUSTER_HISTORY':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'REMOVE_CLUSTER_HISTORY'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'KEEP'
			self.env.ant_call_target 					= 'configureCluster'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'CREATE_CLUSTER_FROM_HISTORY':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'CREATE_CLUSTER_FROM_HISTORY'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'KEEP'
			self.env.ant_call_target 					= 'processCreateClusterConfiguration'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'STOP_CLUSTER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'STOP_CLUSTER'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'DELETE'
			self.env.ant_call_target 					= 'controlCluster'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'START_CLUSTER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'START_CLUSTER'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'DELETE'
			self.env.ant_call_target 					= 'controlCluster'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'RESTART_CLUSTER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'RESTART_CLUSTER'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'DELETE'
			self.env.ant_call_target 					= 'controlCluster'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'RESTART_CLUSTER_RIPPLE':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'RESTART_CLUSTER_RIPPLE'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'CLUSTER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'true'
			self.env.was_handleGenerateConfigFile		= 'DELETE'
			self.env.ant_call_target 					= 'controlCluster'
			self.env.was_mnemonic						= 'WDT' 
		elif self.env.was_installTypeName == 'STOP_APPLICATION':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'STOP_APPLICATION'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'APPLICATION'
			self.env.was_generatePlugin					= 'FALSE'
			if self.env.was_useDBRepositoryForAppInstall.lower() == 'true':
				self.env.was_generateConfigurationFile	= 'true'
				self.env.was_handleGenerateConfigFile	= 'DELETE'
			else:
				self.env.was_generateConfigurationFile	= 'false'
				self.env.was_handleGenerateConfigFile	= 'NO_ACTION'
			#Endif
			self.env.ant_call_target 					= 'controlApplication'
		elif self.env.was_installTypeName == 'START_APPLICATION':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'START_APPLICATION'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'APPLICATION'
			self.env.was_generatePlugin					= 'FALSE'
			if self.env.was_useDBRepositoryForAppInstall.lower() == 'true':
				self.env.was_generateConfigurationFile	= 'true'
				self.env.was_handleGenerateConfigFile	= 'DELETE'
			else:
				self.env.was_generateConfigurationFile	= 'false'
				self.env.was_handleGenerateConfigFile	= 'NO_ACTION'
			#Endif
			self.env.ant_call_target 					= 'controlApplication'
		elif self.env.was_installTypeName == 'CHECK_APPLICATION':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'CHECK_APPLICATION'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'APPLICATION'
			self.env.was_generatePlugin					= 'FALSE'
			if self.env.was_useDBRepositoryForAppInstall.lower() == 'true':
				self.env.was_generateConfigurationFile	= 'true'
				self.env.was_handleGenerateConfigFile	= 'DELETE'
			else:
				self.env.was_generateConfigurationFile	= 'false'
				self.env.was_handleGenerateConfigFile	= 'NO_ACTION'
			#Endif
			self.env.ant_call_target 					= 'controlApplication'
		elif self.env.was_installTypeName == 'RESTART_APPLICATION':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'RESTART_APPLICATION'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'APPLICATION'
			self.env.was_generatePlugin					= 'TRUE'
			if self.env.was_useDBRepositoryForAppInstall.lower() == 'true':
				self.env.was_generateConfigurationFile	= 'true'
				self.env.was_handleGenerateConfigFile	= 'DELETE'
			else:
				self.env.was_generateConfigurationFile	= 'false'
				self.env.was_handleGenerateConfigFile	= 'NO_ACTION'
			#Endif
			self.env.ant_call_target 					= 'controlApplication'
		elif self.env.was_installTypeName == 'CONFIGURE_WEB_SERVER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'CONFIGURE_WEB_SERVER'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'WEB_SERVER'
			self.env.was_webServerAction				= 'start'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'false'
			self.env.was_handleGenerateConfigFile		= 'NO_ACTION'
			self.env.ant_call_target 					= 'controlWebserver'
		elif self.env.was_installTypeName == 'START_WEB_SERVER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'START_WEB_SERVER'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'WEB_SERVER'
			self.env.was_webServerAction				= 'start'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'false'
			self.env.was_handleGenerateConfigFile		= 'NO_ACTION'
			self.env.ant_call_target 					= 'controlWebserver'
		elif self.env.was_installTypeName == 'STOP_WEB_SERVER':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'STOP_WEB_SERVER'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'WEB_SERVER'
			self.env.was_webServerAction				= 'stop'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'false'
			self.env.was_handleGenerateConfigFile		= 'NO_ACTION'
			self.env.ant_call_target 					= 'controlWebserver'
		elif self.env.was_installTypeName == 'UPDATE_WPS_PLUGIN':
			self.logIt( __name__ + ".evaluateInstallType(): Case Install Type Name=" + str( self.env.was_installTypeName ) + "\n" )
			self.env.was_deploymentType					= 'UPDATE_WPS_PLUGIN'
			self.env.was_deploymentApplication			= self.env.was_entityName
			self.env.was_entityType						= 'WEB_SERVER'
			self.env.was_generatePlugin					= 'FALSE'
			self.env.was_generateConfigurationFile		= 'false'
			self.env.was_handleGenerateConfigFile		= 'NO_ACTION'
			self.env.ant_call_target 					= 'updatePortalWebServerPlugin'
		else:
			self.logIt( __name__ + ".evaluateInstallType(): " + str( self.env.was_installTypeName ) + " is not supported.\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".evaluteInstallType(): " + str( self.env.was_installTypeName ) + " is not supported."
			return False
		#Endif
		setattr( self.env, "was_applicationConfigFile", '/dmp/' + str( self.env.was_mnemonic ) + "/admin/" + self.env.was_entityName + "." + self.env.was_domain + ".xml" )
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	sedFile()
	#
	#	DESCRIPTION:
	#		Change the contents of a file.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def sedFile(self, file=None, originalToken=None, replacementToken=None):
		"""
        Change the contents of the given file.
        PARAMETERS:
            file              -- The file to be edited.
            originalToken     -- The string to be replaced.
            replacementToken  -- The replacement value string.
        RETURN:
            True if successful, or False
		"""
		if file is None:
			self.logIt( __name__ + ".sedFile(): Please provide the file name.\n" )
			return False
		#Endif
		if originalToken is None:
			self.logIt( __name__ + ".sedFile(): Please provide the originalToken value.\n" )
			return False
		#Endif
		if replacementToken is None:
			self.logIt( __name__ + ".sedFile(): Please provide the replacementToken value.\n" )
			return False
		#Endif
		self.logIt( __name__ + ".sedFile(): Attempting to edit " + str( file ) + "\n" )
		if not os.access( file, os.F_OK ):
			self.logIt( __name__ + ".sedFile(): '" + str( file ) + "' does not exist.\n" )
			return False
		#Endif
		if not os.access( file, os.R_OK ):
			self.logIt( __name__ + ".sedFile(): '" + str( file ) + "' is not readable.\n" )
			return False
		#Endif
		if not os.access( file, os.W_OK ):
			self.logIt( __name__ + ".sedFile(): '" + str( file ) + "' is not writable.\n" )
			return False
		#Endif
		try:
			FH = open( file, "rw" )
			for line in FH.readline():
				line = re.sub( originalToken, replacementToken, line )
				FH.write( line )
			#Endfor
			FH.close()
		except IOError, e:
			self.logIt( __name__ + ".sedFile(): Failed to edit " + str( file ) + " ==> " + str( e ) + ".\n" )
			return False
		#Endtry
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getClusterByClusterName()
	#
	#	DESCRIPTION:
	#		Run a report for the cluster.
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def getClusterByClusterName(self, type='QUERY_BY_CLUSTER', serviceType='JAVA', target='getClusterByClusterName'):
		"""
        Run a report for the cluster.
        PARAMETERS:
            type        - the install type.  something like 'QUERY_BY_CLUSTER'
            serviceType - the install service type.  something like 'JAVA'
            target      - the install target.  typically 'getClusterByClusterName'
        RETURN:
            True if successful, or False
		"""
		rc = True
		self.logIt( __name__ + ".getClusterByClusterName(): Entered...\n" )
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )

		self.env.getClusterByClusterName_was_scriptServiceImpl = self.env.was_deploymentServiceEJBImpl
		self.env.getClusterByClusterName_queryControl_scriptServiceImpl = "com.dmp.wdt.scripts.services.impl.ScriptServiceDAOImpl"
		self.env.getClusterByClusterName_queryControl_queryImpl = "com.dmp.wdt.scripts.ant.ClusterByClusterNameReport"
		self.env.getClusterByClusterName_queryControl_arg1 = self.env.install_entity_name
		self.env.getClusterByClusterName_queryControl_arg2 = self.env.install_domain
		self.env.getClusterByClusterName_queryControl_arg3 = 'BY_CLUSTER'
		self.logIt( __name__ + ".getClusterByClusterName(): Calling the " + str(self.env.getClusterByClusterName_queryControl_queryImpl) + " java class.\n" )

		########################################################
		#	Instantiate the ClusterByClusterNameReport().
		########################################################
		try:
			myClusterReport = ant.ClusterByClusterNameReport()
		except Exception, e:
			self.logIt( __name__ + ".getClusterByClusterName(): " + str( e ) + ".\n" )
			return False
		#Endtry

		#######################################################
		#	Run the report.
		#######################################################
		ar = [ self.env.getClusterByClusterName_queryControl_arg1, self.env.getClusterByClusterName_queryControl_arg2, self.env.getClusterByClusterName_queryControl_arg3 ]
		try:
			myClusterReport.processReport( self.env.getClusterByClusterName_queryControl_scriptServiceImpl, ar, None )
		except java.lang.Exception, e:
			self.logIt( __name__ + ".getClusterByClusterName(): " + str( e ) + ".\n" )
			return False
		#Endtry
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getClusterByApplicationName()
	#
	#	DESCRIPTION:
	#		Run a report for the cluster.
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def getClusterByApplicationName(self, type='QUERY_BY_APPLICATION', serviceType='JAVA', target='getClusterByApplicationName'):
		"""
        Run a report for the cluster.
        PARAMETERS:
            type        - the install type.  something like 'QUERY_BY_APPLICATION'
            serviceType - the install service type.  something like 'JAVA'
            target      - the install target.  typically 'getClusterByApplicationName'
        RETURN:
            True if successful, or False
		"""
		rc = True
		self.logIt( __name__ + ".getClusterByApplicationName(): Entered...\n" )
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )

		self.env.getClusterByApplicationName_was_scriptServiceImpl = self.env.was_deploymentServiceEJBImpl
		self.env.getClusterByApplicationName_queryControl_scriptServiceImpl = "com.dmp.wdt.scripts.services.impl.ScriptServiceDAOImpl"
		self.env.getClusterByApplicationName_queryControl_queryImpl = "com.dmp.wdt.scripts.ant.ClusterByClusterNameReport"
		self.env.getClusterByApplicationName_queryControl_arg1 = self.env.install_entity_name
		self.env.getClusterByApplicationName_queryControl_arg2 = self.env.install_domain
		self.env.getClusterByApplicationName_queryControl_arg3 = 'BY_APPLICATION'
		self.logIt( __name__ + ".getClusterByApplicationName(): Calling the " + str(self.env.getClusterByApplicationName_queryControl_queryImpl) + " java class.\n" )
		#Endif
		########################################################
		#	Instantiate the ClusterByClusterNameReport().
		########################################################
		try:
			myClusterReport = ant.ClusterByClusterNameReport()
		except Exception, e:
			self.logIt( __name__ + ".getClusterByApplicationName(): " + str( e ) + ".\n" )
			return False
		#Endtry

		#######################################################
		#	Run the report.
		#######################################################
		ar = [ self.env.getClusterByApplicationName_queryControl_arg1, self.env.getClusterByApplicationName_queryControl_arg2, self.env.getClusterByApplicationName_queryControl_arg3 ]
		try:
			myClusterReport.processReport( self.env.getClusterByApplicationName_queryControl_scriptServiceImpl, ar, None )
		except java.lang.Exception, e:
			self.logIt( __name__ + ".getClusterByApplicationName(): " + str( e ) + ".\n" )
			return False
		#Endtry

		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	updatePortalWebServerPlugin()
	#
	#	DESCRIPTION:
	#		Update the portal web server plugin.
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def updatePortalWebServerPlugin(self, type='UPDATE_WPS_PLUGIN', serviceType='WEB_SERVER', target='evaluateInstallType'):
		"""
        Update the portal web server plugin.
        PARAMETERS:
            type        - the install type.  something like 'UPDATE_WPS_PLUGIN'
            serviceType - the install service type.  something like 'WEB_SERVER'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
            True if successful, or False
		"""
		rc = True
		self.logIt( __name__ + ".updatePortalWebServerPlugin(): Entered...\n" )
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.evaluateInstallType()

		self.env.wpsPlugin_applicationName			= self.env.was_entityName
		self.env.wpsPlugin_xmlFile					= self.env.was_applicationConfigFile
		self.env.wpsPlugin_portalCellName			= "wps.portalCellName"
		self.env.wpsPlugin_portalCellNameUpperCase	= "wps.portalCellNameUpperCase"

		self.env.wps_mneAdminDir = '/dmp/' + str( self.env.wpsPlugin_portalCellNameUpperCase ) + '/admin'
		self.env.wps_appName = 'app_' + str( self.env.wpsPlugin_portalCellName ) + '_' + str( self.env.wpsPlugin_portalCellName )
		self.env.wps_pluginfile = str( self.env.wps_mneAdminDir ) + '/' + str( self.env.wps_appName ) + '_plugin-cfg.xml'

		src = str( self.env.was_pluginCopyDir ) + '/plugin-cfg.xml.' + str( self.env.was_domain ) + '.' + str( self.env.wpsPlugin_portalCellName )
		dest = str( self.env.wps_pluginfile )
		try:
			self.logIt( __name__ + ".updatePortalWebServerPlugin(): Copy " + str( src ) + " to " + str( dest ) + "\n" )
			shutil.copyfile( src, dest )
		except IOError, e:
			self.logIt( __name__ + ".updatePortalWebServerPlugin(): Unable to copy " + str( src ) + " to " + str( dest ) + " ==> " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".updatePortalWebServerPlugin(): Unable to copy " + str( src ) + " to " + str( dest ) + " ==> " + str( e )
			#return False
		#Endtry
	
		lrc = self.sedFile( file=dest, originalToken='MNE', replacementToken=self.env.wpsPlugin_portalCellNameUpperCase )
		if not lrc: 
			rc = lrc
			self.logIt( __name__ + ".updatePortalWebServerPlugin(): Unable to edit the " + str( dest ) + " file for token MNE." + "\n" )
		#Endif
		lrc = self.sedFile( file=dest, originalToken='dmpAPP', replacementToken=self.env.wps_appName )
		if not lrc: 
			rc = lrc
			self.logIt( __name__ + ".updatePortalWebServerPlugin(): Unable to edit the " + str( dest ) + " file for token dmpAPP." + "\n" )
		#Endif

		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	initWebServer()
	#
	#	DESCRIPTION:
	#		Init the web server
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def initWebServer(self):
		"""
        Initialize the web server.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".initWebServer(): Entered...\n" )
		try:
			self.logIt( __name__ + ".initWebServer(): Configuring the web server...\n" )
			self.logIt( __name__ + ".initWebServer(): Configuring apachectl_" + str( self.env.was_entityName ) + " file...\n" )

			self.env.was_apacheRuntimeTemplate	= self.env.was_wdtHome + '/templates/' + str( self.env.was_domainVersion ) + '/' + self.env.was_apacheTemplate
			self.env.was_apacheRuntimeFile		= self.env.was_ihsBinDir + '/apachectl_' + self.env.was_mnemonic + '_' + self.env.was_entityName

			self.logIt( __name__ + ".initWebServer(): was.apacheRuntimeTemplate = " + str( self.env.was_apacheRuntimeTemplate ) + "\n" )
			self.logIt( __name__ + ".initWebServer(): was.apacheRuntimeFile = " + str( self.env.was_apacheRuntimeFile ) + "\n" )

			self.env.was_apacheConfTemplate = self.env.was_wdtHome + '/templates/' + self.env.was_domainVersion + '/' + self.env.was_httpdConfTemplate
			self.env.was_apacheConfFile		= self.env.was_ihsConfDir + '/httpd_' + self.env.was_mnemonic + '_' + self.env.was_entityName + '.conf'

			self.logIt( __name__ + ".initWebServer(): was.apacheConfTemplate = " + str( self.env.was_apacheConfTemplate ) + "\n" )
			self.logIt( __name__ + ".initWebServer(): was.apacheConfFile = " + str( self.env.was_apacheConfFile ) + "\n" )

			self.env.was_mneAdminDir 		= '/dmp/' + self.env.was_mnemonic + '/admin'
			self.env.was_httpIncludeFile	= self.env.was_mneAdminDir + '/httpd_' + self.env.was_mnemonic + '_' + self.env.was_entityName + '_supp.conf'
			self.logIt( __name__ + ".initWebServer(): was.httpIncludeFile = " + str( self.env.was_httpIncludeFile ) + "\n" )
		except AttributeError, e:
			self.logIt( __name__ + ".initWebServer(): " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".initWebServer(): " + str( e )
			return False
		#Endtry
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getWebServerPort()
	#
	#	DESCRIPTION:
	#		Get web server port
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def getWebServerPort(self):
		"""
        Get the web server port.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".getWebServerPort(): Entered...\n" )
		try:
			self.logIt( __name__ + ".getWebServerPort():***********Process the entity " + str( self.env.was_entityName ) + "\n" )

			#########################################################################
			#	Call the configurationGenerator java class.
			#########################################################################
			self.logIt( __name__ + ".getWebServerPort(): Call the configureGenerator java class to determine the deployable entity type, the web server port, and the cell name.\n" )
			self.env.configurationGenerator_entityName					= self.env.was_entityName
			self.env.configurationGenerator_entityType					= self.env.was_entityType
			self.env.configurationGenerator_mnemonic					= self.env.was_mnemonic
			self.env.configurationGenerator_domain						= self.env.was_domain
			self.env.configurationGenerator_scriptServiceImpl			= self.env.was_scriptServiceImpl
			self.env.configurationGenerator_hostName					= self.env.was_hostName
			self.env.configurationGenerator_webServerPortProperty		= "was.webServerPort"
			self.env.configurationGenerator_processReturnCodeProperty	= "was.configGenerationReturnCode"
			self.env.configurationGenerator_processResultProperty		= "was.configGenerationResult"
			self.env.configurationGenerator_cellNameProperty			= "was.cellname"
			self.env.configurationGenerator_deploymentId				= self.env.was_deploymentId

			#########################################################################
			#	Log the variables.
			#########################################################################
			self.logIt( __name__ + ".getWebServerPort(): was_entityName=" + str(self.env.was_entityName) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): was_entityType=" + str(self.env.was_entityType) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): was_mnemonic=" + str(self.env.was_mnemonic) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): was_domain=" + str(self.env.was_domain) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): was_hostName=" + str(self.env.was_hostName) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): was_deploymentId=" + str(self.env.was_deploymentId) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): was_scriptServiceImpl=" + str(self.env.was_scriptServiceImpl) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): configurationGenerator_entityName=" + str(self.env.configurationGenerator_entityName) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): configurationGenerator_entityType=" + str(self.env.configurationGenerator_entityType) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): configurationGenerator_mnemonic=" + str(self.env.configurationGenerator_mnemonic) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): configurationGenerator_domain=" + str(self.env.configurationGenerator_domain) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): configurationGenerator_hostName=" + str(self.env.configurationGenerator_hostName) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): configurationGenerator_deploymentId=" + str(self.env.configurationGenerator_deploymentId) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): configurationGenerator_scriptServiceImpl=" + str(self.env.configurationGenerator_scriptServiceImpl) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): configurationGenerator_webServerPortProperty=" + str(self.env.configurationGenerator_webServerPortProperty) + "\n" )

			##################################################################
			#	Instantiate the DeploymentConfigurationGenerator() object.
			##################################################################
			deploymentConfigurationGenerator = ant.DeploymentConfigurationGenerator()

			##################################################################
			#	Call the setXXX() methods on the object.
			##################################################################
			deploymentConfigurationGenerator.setEntityName( self.env.configurationGenerator_entityName )
			deploymentConfigurationGenerator.setEntityType( self.env.configurationGenerator_entityType )
			deploymentConfigurationGenerator.setMnemonic( self.env.configurationGenerator_mnemonic )
			deploymentConfigurationGenerator.setDomain( self.env.configurationGenerator_domain )
			deploymentConfigurationGenerator.setScriptServiceImpl( self.env.configurationGenerator_scriptServiceImpl )
			deploymentConfigurationGenerator.setHostName( self.env.configurationGenerator_hostName )
			deploymentConfigurationGenerator.setDeploymentId( self.env.configurationGenerator_deploymentId )

			##################################################################
			#	Set the properties that we want to look at after.
			##################################################################
			deploymentConfigurationGenerator.setProcessReturnCodeProperty( self.env.configurationGenerator_processReturnCodeProperty )
			deploymentConfigurationGenerator.setProcessResultProperty( self.env.configurationGenerator_processResultProperty )
			deploymentConfigurationGenerator.setCellNameProperty( self.env.configurationGenerator_cellNameProperty )
			deploymentConfigurationGenerator.setWebServerPortProperty( self.env.configurationGenerator_webServerPortProperty )

			#####################################################################
			#	Create and set the ant project object for the ant Task().
			#####################################################################
			antProject	= antTools.Project()
			antProject.setName( "wsad" )
			deploymentConfigurationGenerator.setProject( antProject )

			############################################################################################################
			# Invoke the configurationGenerator java class here with above arguments.
			############################################################################################################
			try:
				deploymentConfigurationGenerator.execute()

				######################################################################
				# Collect the return data from the called class.
				######################################################################
				self.env.was_configGenerationReturnCode = deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_processReturnCodeProperty )
				self.env.was_cellname					= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_cellNameProperty )
				self.env.was_webServerPort				= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_webServerPortProperty ) 
				self.env.was_configGenerationResult		= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_processResultProperty ) + ". Entity name=" + str( self.entity )
			except org.apache.tools.ant.BuildException, be:
				self.logIt( __name__ + ".getWebServerPort(): Call to DeploymentConfigurationGenerator.execute() failed. => " + str( be ) + "\n" )
				self.env.was_configGenerationReturnCode = "1"
				self.env.was_configGenerationResult		= "Failed to get the web server ports => " + str( be )
			except java.lang.NullPointerException, npe:
				self.logIt( __name__ + ".getWebServerPort(): Call to DeploymentConfigurationGenerator.execute() failed. => " + str( npe ) + "\n" )
				self.env.was_configGenerationReturnCode = "1"
				self.env.was_configGenerationResult		= "Failed to get the web server ports => " + str( npe )
			except java.lang.Exception, e:
				self.logIt( __name__ + ".getWebServerPort(): Call to DeploymentConfigurationGenerator.execute() failed. => " + str( e ) + "\n" )
				self.env.was_configGenerationReturnCode = "1"
				self.env.was_configGenerationResult		= "Failed to get the web server ports => " + str( e )
			#Endtry

			####################################################################################
			#	Log what we got.
			####################################################################################
			self.logIt( __name__ + ".getWebServerPort(): was.configGenerationReturnCode  = " + str( self.env.was_configGenerationReturnCode ) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): was.cellname  = " + str( self.env.was_cellname ) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): was.webServerPort  = " + str( self.env.was_webServerPort ) + "\n" )
			self.logIt( __name__ + ".getWebServerPort(): was.configGenerationResult  = " + str( self.env.was_configGenerationResult ) + "\n" )

			#################################################################################
			#	Check the return code of the object.
			#################################################################################
			if self.env.was_configGenerationReturnCode == '0':
				self.env.was_runDeployment = 'true'
				self.logIt( __name__ + ".getWebServerPort(): Deployable Entity Type=" + str( self.env.was_entityType ) + ".\n" )
				self.logIt( __name__ + ".getWebServerPort(): Web Server Port=" + str( self.env.was_webServerPort ) + ".\n" )
				self.logIt( __name__ + ".getWebServerPort(): Cell Name=" + str( self.env.was_cellname ) + ".\n" )
			else:
				self.env.was_runDeployment = 'false'
				self.logIt( __name__ + ".getWebServerPort(): Return Code " + str( self.env.was_configGenerationReturnCode ) + ".\n" )
				self.logIt( __name__ + ".getWebServerPort(): Generation Result " + str( self.env.was_configGenerationResult ) + ".\n" )
				self.env.was_deploymentCompletionMessage = __name__ + ".getWebServerPort(): " + str( self.env.was_configGenerationResult )
				self.env.was_deploymentStatus = 'F'
				self.env.was_entityStatus = 'X'
				self.logIt( __name__ + ".getWebServerPort(): " + str( self.env.was_deploymentCompletionMessage ) + "\n" )
				return False
			#Endif
		except AttributeError, e:
			self.logIt( __name__ + ".getWebServerPort(): " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".getWebServerPort(): " + str( e )
			return False
		except java.lang.UnsupportedClassVersionError, ue:
			self.logIt( __name__ + ".getWebServerPort(): " + str( ue ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".getWebServerPort(): " + str( ue )
			return False
		#Endtry
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	startStopWebServer()
	#
	#	DESCRIPTION:
	#		Start or stop the web server.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def startStopWebServer(self):
		"""
        Start or stop the web server.
        Only copy and update the plugin file when start web server command is invoked.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".startStopWebServer(): Entered...\n" )
		try:
			if self.env.was_webServerAction == 'start':
				######################################################################
				#	Stubbed:  Call the webServerPluginUtil java class to check the 
				#	plugin generation level.
				######################################################################
				self.logIt( __name__ + ".startStopWebServer(): STUBBED: Call the webWebServerPluginUtil java class to determine the cluster name and plugin level.\n" )
				self.env.webServerPluginUtil_domainName		= self.env.was_domain
				self.env.webServerPluginUtil_appConfigXML	= self.env.was_applicationConfigFile
				self.env.webServerPluginUtil_clusterName	= 'was.clusterName'
				self.env.webServerPluginUtil_pluginLevel	= 'was.pluginLevel'
				self.env.webServerPluginUtil_pluginMessageProperty	= 'was.pluginMessage'

				#####################################################################
				#	Fake out the responses for now.
				#####################################################################
				self.env.was_PluginMessage	= 'This response is faked in startStopWebServer()...'
				self.env.was_pluginLevel	= 'CLUSTER'
				self.env.was_clusterName	= 'MY_CLUSTER_set_in_startStopWebServer'
				self.logIt( __name__ + ".startStopWebServer(): " + str( self.env.was_PluginMessage ) + "\n" )
				if self.env.was_pluginLevel.lower() == 'cluster':
					self.env.tmp_plugin_file = self.env.was_pluginCopyDir + '/plugin-cfg.xml.' + self.env.was_domain + '.' + self.env.was_cellname + '.' + self.env.was_clusterName
				else:
					self.env.tmp_plugin_file = self.env.was_pluginCopyDir + '/plugin-cfg.xml.' + self.env.was_domain + '.' + self.env.was_cellname
				#Endif

				try:
					shutil.copyfile( self.env.tmp_plugin_file, self.env.was_mneAdminDir + '/' + self.env.was_entityName + '_plugin-cfg.xml' )
				except IOError, e:
					self.logIt( __name__ + ".startStopWebServer(): Unable to copy " + str(self.env.tmp_plugin_file) + " to " + str(self.env.was_mneAdminDir + '/' + self.env.was_entityName + '_plugin-cfg.xml') + " : " + str( e ) + "\n" )
					self.env.was_deploymentStatus = 'F'
					self.env.was_deploymentCompletionMessage = __name__ + ".startStopWebServer(): " + "Unable to copy " + str(self.env.tmp_plugin_file) + " to " + str(self.env.was_mneAdminDir + '/' + self.env.was_entityName + '_plugin-cfg.xml') + " : " + str( e ) + "\n" 
					return False
				#Endtry
				self.sedFile( file=self.env.was_mneAdminDir + '/' + self.env.was_entityName, originalToken='MNE', replacementToken=self.env.was_mnemonic )
				self.sedFile( file=self.env.was_mneAdminDir + '/' + self.env.was_entityName, originalToken='dmpAPP', replacementToken=self.env.was_entityName )

				####################################################################
				#	Stubbed:  call the cssUtil java class with css cluster info.
				####################################################################
				self.logIt( __name__ + ".startStopWebServer(): STUBBED: Call the cssUtil java class to determine the plugin status message.\n" )
				self.env.cssUtil_pluginFile = self.env.was_mneAdminDir + '/' + self.env.was_entityName + '_plugin-cfg.xml'
				self.env.cssUtil_xmlFile = self.env.was_applicationConfigFile
				self.env.cssUtil_statusMsgProperty = 'plugin.statusMessage'

				####################################################################
				#	Fake out the responses.
				####################################################################
				self.env.plugin_statusMessage = 'This has been faked in the startStopWebServer()'
				self.logIt( __name__ + ".startStopWebServer(): " + str( self.env.plugin_statusMessage ) + "\n" )

				###################################################################
				#	Sleep for 5 seconds.
				###################################################################
				self.logIt( __name__ + ".startStopWebServer(): Sleeping for 5 seconds...\n" )
				time.sleep( 5 )
			#Endif

			####################################################################
			#	Stubbed:  call web server command.
			####################################################################
			self.logIt( __name__ + ".startStopWebServer(): STUBBED: Run the " + str( self.env.was_apacheRuntimeFile ) + "(" + str( self.env.was_webServerAction ) + ") to execute the wsControlCommand.\n" )
			self.logIt( __name__ + ".startStopWebServer(): Performing WebServer Command : " + str( self.env.was_webServerAction ) + "\n" )
			self.env.was_apacheRuntimeFile_executable		= self.env.was_apacheRuntimeFile
			self.env.was_apacheRuntimeFile_resultproperty	= "was.wsControlCommandResult"
			self.env.was_apacheRuntimeFile_webServerAction	= self.env.was_webServerAction

			####################################################################
			#	Fake out the responses.
			####################################################################
			self.env.was_wsControlCommandResult	= '0'

			if self.env.was_wsControlCommandResult == '0':
				self.env.was_completedDeployment	= 'true'
				self.env.was_deploymentStatus 		= 'S'
				self.env.was_deploymentHasError 	= 'false'
				self.env.was_deploymentCompletionMessage 	= 'Successfully deployed Web Server for ' + str( self.env.was_entityName )
			else:
				self.logIt( __name__ + ".startStopWebServer(): Return Code : " + str( self.env.was_wsControlCommandResult ) + "\n" )
				self.env.was_deploymentHasError = 'true'
				self.env.was_deploymentStatus = 'F'
				self.logIt( __name__ + ".startStopWebServer(): status = " + str( self.env.was_deploymentStatus ) + "\n" )
				self.env.was_deploymentCompletionMessage 	= 'Failed when running the web server control command.  Check the log for details...'
			#Endif
		except AttributeError, e:
			self.logIt( __name__ + ".startStopWebServer(): " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".startStopWebServer(): " + str( e )
			return False
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createWebServer()
	#
	#	DESCRIPTION:
	#		Create web server
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def createWebServer(self):
		"""
        Create web server.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".createWebServer(): Entered...\n" )
		try:
			self.logIt( __name__ + ".createWebServer(): Configuring the web server on host " + str( self.env.was_hostName ) + " and port " + str( self.env.was_webServerPort ) + "\n" )
			self.logIt( __name__ + ".createWebServer(): Configuring apachectl_" + str( self.env.was_entityName ) + "...\n" )
			try:
				shutil.copyfile( self.env.was_apacheRuntimeTemplate, self.env.was_apacheRuntimeFile )
			except IOError, e:
				self.logIt( __name__ + ".createWebServer(): " + str( e ) + "\n" )
			#Endtry
			self.sedFile( file=self.env.was_apacheRuntimeFile, originalToken='MNE', replacementToken=self.env.was_mnemonic )
			self.sedFile( file=self.env.was_apacheRuntimeFile, originalToken='APPNAME', replacementToken=self.env.was_entityName )
			
			try:
				shutil.copyfile( self.env.was_apacheConfTemplate, self.env.was_apacheConfFile )
			except IOError, e:
				self.logIt( __name__ + ".createWebServer(): " + str( e ) + "\n" )
			#Endtry
			self.sedFile( file=self.env.was_apacheConfFile, originalToken='99999', replacementToken=self.env.was_webServerPort )
			self.sedFile( file=self.env.was_apacheConfFile, originalToken='HOSTNAME', replacementToken=self.env.was_hostName )
			self.sedFile( file=self.env.was_apacheConfFile, originalToken='APPNAME', replacementToken=self.env.was_entityName )
			self.sedFile( file=self.env.was_apacheConfFile, originalToken='MNE', replacementToken=self.env.was_mnemonic )
			self.sedFile( file=self.env.was_apacheConfFile, originalToken='mne', replacementToken=self.env.was_mnemonicLowerCase )

			try:
				os.chmod( self.env.was_apacheConfFile, 0655 )
			except OSError, e:
				self.logIt( __name__ + ".createWebServer(): " + str( e ) + "\n" )
			#Endtry
			try:
				os.chmod( self.env.was_apacheRuntimeFile, 0655 )
			except OSError, e:
				self.logIt( __name__ + ".createWebServer(): " + str( e ) + "\n" )
			#Endtry

			if os.access( self.env.was_httpIncludeFile, os.F_OK ):
				self.env.was_httpIncludeExists = 'true'
				self.logIt( __name__ + ".createWebServer(): Include file exists.... " + str( self.env.was_httpIncludeExists ) + "...\n" )

				#####################################################################
				#	Stubbed:  Call the webServerPlugUtil java class to check the
				#	plugin generation level.
				#####################################################################
				self.logIt( __name__ + ".createWebServer(): STUBBED: Call the webServerPluginUtil java class to get the cluster name and the plugin level.\n" )
				self.env.webServerPluginUtil_domainName		= self.env.was_domain
				self.env.webServerPluginUtil_appConfigXML	= self.env.was_applicationConfigFile
				self.env.webServerPluginUtil_clusterName	= "was.clusterName"
				self.env.webServerPluginUtil_pluginLevel	= "was.pluginLevel"
				self.env.webServerPluginUtil_pluginMessageProperty		= "was.pluginMessageProperty"
				
				####################################################################
				#	Fake out the responses.
				####################################################################
				self.env.was_PluginMessage	= "Faked in createWebServer..."
				self.env.was_pluginLevel	= 'CLUSTER'
				self.env.was_clusterName	= 'MY CLUSTER set in createWebServer()'
				self.logIt( __name__ + ".createWebServer(): " + str( self.env.was_PluginMessage ) + "\n" )
				if self.env.was_pluginLevel == 'CLUSTER':
					self.env.tmp_plugin_file = self.env.was_pluginCopyDir + '/plug-cfg.xml.' + self.env.was_domain + '.' + self.env.was_cellname + '.' + self.env.was_clusterName
				else:
					self.env.tmp_plugin_file = self.env.was_pluginCopyDir + '/plug-cfg.xml.' + self.env.was_domain + '.' + self.env.was_cellname
				#Endif
				shutil.copyfile( self.env.tmp_plugin_file, self.env.was_mneAdminDir + '/' + self.env.was_entityName + '_plugin-cfg.xml' )
				self.sedFile( file=self.env.was_mneAdminDir + '/' + self.env.was_entityName + '_plugin-cfg.xml', originalToken='MNE', replacementToken=self.env.was_mnemonic )
				self.sedFile( file=self.env.was_mneAdminDir + '/' + self.env.was_entityName + '_plugin-cfg.xml', originalToken='dmpAPP', replacementToken=self.env.was_entityName )

				##################################################################
				#	Stubbed:  Call the cssUtil java class to modify the plugin
				#	with the css cluster info.
				##################################################################
				self.logIt( __name__ + ".createWebServer(): STUBBED: Call the cssUtil(" + str( self.env.was_applicationConfigFile ) + ") java class to modify the plugin with the css cluster info.\n" )
				self.env.cssUtil_pluginFile = self.env.was_mneAdminDir + '/' + self.env.was_entityName + '_plugin-cfg.xml'
				self.env.cssUtil_xmlFile = self.env.was_applicationConfigFile
				self.env.cssUtil_statusMsgProperty = 'plugin.statusMessage'

				####################################################################
				#	Fake out the responses.
				####################################################################
				self.env.plugin_statusMessage = 'This has been faked in the createWebServer()'
				self.logIt( __name__ + ".createWebServer(): " + str( self.env.plugin_statusMessage ) + "\n" )
				self.env.was_deploymentStatus = 'S'
			else:
				self.env.plugin_statusMessage = self.env.was_httpIncludeFile + ' does not exist.'
				self.env.was_deploymentCompletionMessage = __name__ + ".createWebServer(): Could not access " + str( self.env.was_httpIncludeFile )
				self.logIt( __name__ + ".createWebServer(): " + str( self.env.plugin_statusMessage ) + "\n" )
				self.env.was_deploymentStatus = 'F'
				return False
			#Endif
		except AttributeError, e:
			self.logIt( __name__ + ".createWebServer(): " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".createWebServer(): " + str( e )
			return False
		#Endif
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	printWebServerSummary()
	#
	#	DESCRIPTION:
	#		Print web server deployment summary.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def printWebServerSummary(self):
		"""
        Print web server deployment summary.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".printWebServerSummary(): Entered...\n" )
		try:
			self.logIt( __name__ + ".printWebServerSummary():----------------------------------------Summary---------------------------------------\n" )
			self.logIt( __name__ + ".printWebServerSummary(): Deployment Status (S - success / F - Fail) : " + str( self.env.was_deploymentStatus ) + ".\n" )
			if self.env.was_deploymentStatus == 'S':
				self.logIt( __name__ + ".printWebServerSummary(): Deployment of " + str( self.env.was_entityName ) + "(" + str( self.env.was_entityType ) + ") completed successfully.\n" )
			else:
				self.logIt( __name__ + ".printWebServerSummary(): Deployment of " + str( self.env.was_entityName ) + " was unsuccessful (please refer to the log for details).\n" )
				self.logIt( __name__ + ".printWebServerSummary(): Error Message : " + str( self.env.was_deploymentCompletionMessage ) + ".\n" )
			#Endif
			self.logIt( __name__ + ".printWebServerSummary():--------------------------------------------------------------------------------------\n" )
		except AttributeError, e:
			self.logIt( __name__ + ".printWebServerSummary(): " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".printWebServerSummary(): " + str( e )
			return False
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	createDeploymentEntry()
	#
	#	DESCRIPTION:
	#		Create the deployment entry, whatever that means.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def createDeploymentEntry(self):
		"""
        Create the deployment entry, whatever that means.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".createDeploymentEntry(): Entered...\n" )
		self.logIt( __name__ + ".createDeploymentEntry(): deploymentId=" + str( self.env.was_deploymentId ) + "\n" )
		self.logIt( __name__ + ".createDeploymentEntry(): updatedUser='SYSTEM' action='CREATE'\n" )
		self.logIt( __name__ + ".createDeploymentEntry(): entityName=" + str( self.env.install_entity_name ) + "\n" )
		self.logIt( __name__ + ".createDeploymentEntry(): deploymentType=" + str( self.env.was_deploymentType ) + "\n" )
		self.logIt( __name__ + ".createDeploymentEntry(): domain=" + str( self.env.was_domain ) + "\n" )
		self.logIt( __name__ + ".createDeploymentEntry(): hasErrorProperty=" + str( self.env.was_dbErrorFlagCreateEntry ) + "\n" )
		self.logIt( __name__ + ".createDeploymentEntry(): errorMessageProperty=" + str( self.env.was_dbErrorMessageCreateEntry ) + "\n" )
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	generateConfigurationFile()
	#
	#	DESCRIPTION:
	#		Generate the configuration file.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def generateConfigurationFile(self):
		"""
        The configuration generator determines the cluster information given an app
        name or cluster name.  If the xmlconfig node hostname == the hostname the
        command has been initiated on the "was.nodeNameToDeploy" and is set to the
        node name and nodeSpecificOperationProperty is set to "TRUE".  If
        nodeSpecificOperationProperty is false then was.nodeNameToDeploy = "ALL_NODES".
        If the operation is node specific then:
        
        New properties
        - nodeNameToDeployProperty
        - nodeSpecificOperationProperty
        - rename dmgrHostNameProperty to wsadminHostNameProperty
        - rename dmgrSoapConnectorPortProperty to wsadminSoapConnectorPortProperty
        - rename dmgrRMIConnectorPortProperty to wsadminRMIConnectorPortProperty
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""

		self.logIt( __name__ + ".generateConfigurationFile(): Entered...\n" )
		myMsg = """
        The configuration generator determines the cluster information given an app
        name or cluster name.  If the xmlconfig node hostname == the hostname the
        command has been initiated on the "was.nodeNameToDeploy" and is set to the
        node name and nodeSpecificOperationProperty is set to "TRUE".  If
        nodeSpecificOperationProperty is false then was.nodeNameToDeploy = "ALL_NODES".
        If the operation is node specific then:
        
        New properties
        - nodeNameToDeployProperty
        - nodeSpecificOperationProperty
        - rename dmgrHostNameProperty to wsadminHostNameProperty
        - rename dmgrSoapConnectorPortProperty to wsadminSoapConnectorPortProperty
        - rename dmgrRMIConnectorPortProperty to wsadminRMIConnectorPortProperty
		"""
		self.logIt( __name__ + ".generateConfigurationFile(): " + myMsg + "\n" )
		self.env.was_configGenerationReturnCode = None
		self.env.was_cellname                   = None
		self.env.was_nodeSpecificOperation      = None
		self.env.was_clusterName                = None
		self.env.was_wsadminSoapConnectorPort	= None
		self.env.was_wsadminRMIConnectorPort   	= None
		self.env.was_deploymentManagerHomeDirectory = None
		self.env.was_deploymentConfigFileGenerated  = None
		self.env.was_nodeNameToDeploy           = None
		self.env.was_entityStatus               = None
		self.env.was_configGenerationResult     = None

		self.logIt( __name__ + ".generateConfigurationFile(): was_generateConfigurationFile=" + self.env.was_generateConfigurationFile + "\n" )
		try:
			if self.env.was_generateConfigurationFile == 'false':
				#################################################################
				#	Check to see if the file exists.
				#################################################################
				self.env.available_file = self.env.was_applicationConfigFile
				self.env.available_file_type = 'file'
				#self.env.was_okToProceed = 'false'
				if os.access( self.env.available_file, os.F_OK ) and os.access( self.env.available_file, os.R_OK ):
					self.env.was_okToProceed = 'true'
				else:
					self.env.was_okToProceed = 'false'
				#Endif
			else:
				self.env.was_okToProceed = 'true'
			#Endif
			if self.env.was_okToProceed == 'true':
				self.logIt( __name__ + ".generateConfigurationFile(): Call the DeploymentConfigurationGenerator java class to determine:\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.cellname\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.wsadminHostName\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.wsadminSoapConnectorPort\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.wsadminRMIConnectorPort\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.clusterName\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.deploymentConfigFileGenerated\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.deploymentManagerHomeDirectory\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.entityStatus\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.nodeNameToDeploy\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.configureGenerationReturnCode\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.configureGenerationResult\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.nodeSpecificOperation\n" )

				self.logIt( __name__ + ".generateConfigurationFile(): Using template file=" + str( self.env.was_clustertemplate ) + "\n" )
				self.env.configurationGenerator_entityName 					= self.env.was_entityName	
				self.env.configurationGenerator_entityType 					= self.env.was_entityType	
				self.env.configurationGenerator_mnemonic 					= self.env.was_mnemonic	
				self.env.configurationGenerator_domain 						= self.env.was_domain	
				self.env.configurationGenerator_hostName 					= self.env.was_hostName	
				self.env.configurationGenerator_deploymentId 				= self.env.was_deploymentId	
				self.env.configurationGenerator_scriptServiceImpl 			= self.env.was_scriptServiceImpl	
				self.env.configurationGenerator_clusterTemplate 			= self.env.was_clustertemplate	
				self.env.configurationGenerator_clusterAdminBaseDirectory 	= self.env.was_cluster_basedirectory	
				self.env.configurationGenerator_clusterXMLPropertyFileName 	= self.env.was_clusterxmlpropfile	

				self.logIt( __name__ + ".generateConfigurationFile(): was_entityName=" + str(self.env.was_entityName) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was_entityType=" + str(self.env.was_entityType) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was_mnemonic=" + str(self.env.was_mnemonic) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was_domain=" + str(self.env.was_domain) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was_hostName=" + str(self.env.was_hostName) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was_deploymentId=" + str(self.env.was_deploymentId) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was_scriptServiceImpl=" + str(self.env.was_scriptServiceImpl) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was_clustertemplate=" + str(self.env.was_clustertemplate) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was_cluster_basedirectory=" + str(self.env.was_cluster_basedirectory) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was_clusterxmlpropfile=" + str(self.env.was_clusterxmlpropfile) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): configurationGenerator_entityName=" + str(self.env.configurationGenerator_entityName) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): configurationGenerator_entityType=" + str(self.env.configurationGenerator_entityType) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): configurationGenerator_mnemonic=" + str(self.env.configurationGenerator_mnemonic) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): configurationGenerator_domain=" + str(self.env.configurationGenerator_domain) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): configurationGenerator_hostName=" + str(self.env.configurationGenerator_hostName) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): configurationGenerator_deploymentId=" + str(self.env.configurationGenerator_deploymentId) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): configurationGenerator_scriptServiceImpl=" + str(self.env.configurationGenerator_scriptServiceImpl) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): configurationGenerator_clusterTemplate=" + str(self.env.configurationGenerator_clusterTemplate) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): configurationGenerator_clusterAdminBaseDirectory=" + str(self.env.configurationGenerator_clusterAdminBaseDirectory) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): configurationGenerator_clusterXMLPropertyFileName=" + str(self.env.configurationGenerator_clusterXMLPropertyFileName) + "\n" )

				if self.env.was_generateConfigurationFile.lower() == 'true':
					self.env.configurationGenerator_savePrevious = True
				else:
					self.env.configurationGenerator_savePrevious = False
				#Endif

				self.env.configurationGenerator_cellNameProperty 				= "was.cellname"	
				self.env.configurationGenerator_dmgrHostNameProperty 			= "was.wsadminHostName"	
				self.env.configurationGenerator_dmgrSoapConnectorPortProperty 	= "was.wsadminSoapConnectorPort"	
				self.env.configurationGenerator_dmgrRMIConnectorPortProperty 	= "was.wsadminRMIConnectorPort"	
				self.env.configurationGenerator_clusterNameProperty 			= "was.clusterName"	
				self.env.configurationGenerator_deploymentConfigFileProperty 	= "was.deploymentConfigFileGenerated"	
				self.env.configurationGenerator_deploymentManagerHomeDirectoryProperty = "was.deploymentManagerHomeDirectory"	
				self.env.configurationGenerator_entityStatusProperty 			= "was.entityStatus"	
				self.env.configurationGenerator_nodeNameToDeployProperty 		= "was.nodeNameToDeploy"	
				self.env.configurationGenerator_processReturnCodeProperty 		= "was.configGenerationReturnCode"	
				self.env.configurationGenerator_processResultProperty 			= "was.configGenerationResult"	
				self.env.configurationGenerator_nodeSpecificOperationProperty 	= "was.nodeSpecificOperation"	

				##################################################################
				#	Instantiate the DeploymentConfigurationGenerator() object.
				##################################################################
				deploymentConfigurationGenerator = ant.DeploymentConfigurationGenerator()

				##################################################################
				#	Call the setXXX() methods on the object.
				##################################################################
				deploymentConfigurationGenerator.setEntityName( self.env.configurationGenerator_entityName )
				deploymentConfigurationGenerator.setEntityType( self.env.configurationGenerator_entityType )
				deploymentConfigurationGenerator.setMnemonic( self.env.configurationGenerator_mnemonic )
				deploymentConfigurationGenerator.setDomain( self.env.configurationGenerator_domain )
				deploymentConfigurationGenerator.setHostName( self.env.configurationGenerator_hostName )
				deploymentConfigurationGenerator.setDeploymentId( self.env.configurationGenerator_deploymentId )
				deploymentConfigurationGenerator.setScriptServiceImpl( self.env.configurationGenerator_scriptServiceImpl )
				deploymentConfigurationGenerator.setClusterTemplate( self.env.configurationGenerator_clusterTemplate )
				deploymentConfigurationGenerator.setClusterAdminBaseDirectory( self.env.configurationGenerator_clusterAdminBaseDirectory )
				deploymentConfigurationGenerator.setSavePrevious( self.env.configurationGenerator_savePrevious )
				deploymentConfigurationGenerator.setCellNameProperty( self.env.configurationGenerator_cellNameProperty )
				deploymentConfigurationGenerator.setDmgrHostNameProperty( self.env.configurationGenerator_dmgrHostNameProperty )
				deploymentConfigurationGenerator.setDmgrSoapConnectorPortProperty( self.env.configurationGenerator_dmgrSoapConnectorPortProperty )
				deploymentConfigurationGenerator.setDmgrRMIConnectorPortProperty( self.env.configurationGenerator_dmgrRMIConnectorPortProperty )
				deploymentConfigurationGenerator.setClusterNameProperty( self.env.configurationGenerator_clusterNameProperty )
				deploymentConfigurationGenerator.setDeploymentConfigFileProperty( self.env.configurationGenerator_deploymentConfigFileProperty )
				deploymentConfigurationGenerator.setDeploymentManagerHomeDirectoryProperty( self.env.configurationGenerator_deploymentManagerHomeDirectoryProperty )
				deploymentConfigurationGenerator.setClusterXMLPropertyFileName( self.env.configurationGenerator_clusterXMLPropertyFileName )
				deploymentConfigurationGenerator.setEntityStatusProperty( self.env.configurationGenerator_entityStatusProperty )
				deploymentConfigurationGenerator.setNodeNameToDeployProperty( self.env.configurationGenerator_nodeNameToDeployProperty )
				deploymentConfigurationGenerator.setProcessReturnCodeProperty( self.env.configurationGenerator_processReturnCodeProperty )
				deploymentConfigurationGenerator.setProcessResultProperty( self.env.configurationGenerator_processResultProperty )
				deploymentConfigurationGenerator.setNodeSpecificOperationProperty( self.env.configurationGenerator_nodeSpecificOperationProperty )

				#####################################################################
				#	Create and set the ant project object for the ant Task().
				#####################################################################
				antProject	= antTools.Project()
				antProject.setName( "wsad" )
				deploymentConfigurationGenerator.setProject( antProject )

				############################################################################################################
				# Invoke the configurationGenerator java class here with above arguments.
				############################################################################################################
				try:
					deploymentConfigurationGenerator.execute()

					######################################################################
					# Collect the return data from the called class.
					######################################################################
					self.env.was_configGenerationReturnCode = deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_processReturnCodeProperty )
					self.env.was_cellname					= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_cellNameProperty )
					self.env.was_nodeSpecificOperation		= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_nodeSpecificOperationProperty )
					self.env.was_clusterName				= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_clusterNameProperty )
					self.env.was_wsadminSoapConnectorPort	= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_dmgrSoapConnectorPortProperty )
					self.env.was_wsadminRMIConnectorPort	= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_dmgrRMIConnectorPortProperty )
					self.env.was_deploymentManagerHomeDirectory	= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_deploymentManagerHomeDirectoryProperty )
					self.env.was_deploymentConfigFileGenerated	= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_deploymentConfigFileProperty )
					self.env.was_deploymentConfigFile 		= self.env.was_deploymentConfigFileGenerated
					self.env.was_nodeNameToDeploy			= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_nodeNameToDeployProperty )
					self.env.was_entityStatus				= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_entityStatusProperty )
					self.env.was_configGenerationResult		= deploymentConfigurationGenerator.getProject().getProperty( self.env.configurationGenerator_processResultProperty ) + ". Entity name=" + str( self.entity )
				except org.apache.tools.ant.BuildException, be:
					self.logIt( __name__ + ".generateConfigurationFile(): Call to DeploymentConfigurationGenerator.execute() failed. => " + str( be ) + "\n" )
					self.env.was_configGenerationReturnCode = "1"
					self.env.was_configGenerationResult		= "Generate Configuration File failed => " + str( be )
				except java.lang.NullPointerException, npe:
					self.logIt( __name__ + ".generateConfigurationFile(): Call to DeploymentConfigurationGenerator.execute() failed. => " + str( npe ) + "\n" )
					self.env.was_configGenerationReturnCode = "1"
					self.env.was_configGenerationResult		= "Generate Configuration File failed => " + str( npe )
				except java.lang.Exception, e:
					self.logIt( __name__ + ".generateConfigurationFile(): Call to DeploymentConfigurationGenerator.execute() failed. => " + str( e ) + "\n" )
					self.env.was_configGenerationReturnCode = "1"
					self.env.was_configGenerationResult		= "Generate Configuration File failed => " + str( e )
				#Endtry

				self.env.was_wsadminHostName = self.env.install_hostName

				####################################################################################
				#	Log what we got.
				####################################################################################
				self.logIt( __name__ + ".generateConfigurationFile(): was.configGenerationReturnCode  = " + str( self.env.was_configGenerationReturnCode ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.cellname  = " + str( self.env.was_cellname ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.nodeSpecificOperation  = " + str( self.env.was_nodeSpecificOperation ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.clusterName  = " + str( self.env.was_clusterName ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.wsadminSoapConnectorPort  = " + str( self.env.was_wsadminSoapConnectorPort ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.wsadminRMIConnectorPort  = " + str( self.env.was_wsadminRMIConnectorPort ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.deploymentManagerHomeDirectory  = " + str( self.env.was_deploymentManagerHomeDirectory ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.deploymentConfigFileGenerated  = " + str( self.env.was_deploymentConfigFileGenerated ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.nodeNameToDeploy  = " + str( self.env.was_nodeNameToDeploy ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.entityStatus  = " + str( self.env.was_entityStatus ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.configGenerationResult  = " + str( self.env.was_configGenerationResult ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.wsadminHostName  = " + str( self.env.was_wsadminHostName ) + "\n" )
				self.logIt( __name__ + ".generateConfigurationFile(): was.applicationConfigFile  = " + str( self.env.was_applicationConfigFile ) + "\n" )

				#################################################################################
				#	Check the return code of the object.
				#################################################################################
				if self.env.was_configGenerationReturnCode == '0':
					self.env.was_runDeployment = 'true'
					self.logIt( __name__ + ".generateConfigurationFile(): Is the operation node specific? = " + str( self.env.was_nodeSpecificOperation ) + "\n" )
					self.logIt( __name__ + ".generateConfigurationFile(): Cell Name = " + str( self.env.was_cellname ) + "\n" )
					self.logIt( __name__ + ".generateConfigurationFile(): Cluster Name = " + str( self.env.was_clusterName ) + "\n" )
					self.logIt( __name__ + ".generateConfigurationFile(): DMGR Host Name = " + str( self.env.was_wsadminHostName ) + "\n" )
					self.logIt( __name__ + ".generateConfigurationFile(): DMGR SOAP Port = " + str( self.env.was_wsadminSoapConnectorPort ) + "\n" )
					self.logIt( __name__ + ".generateConfigurationFile(): DMGR ORB  Port = " + str( self.env.was_wsadminRMIConnectorPort ) + "\n" )
					self.logIt( __name__ + ".generateConfigurationFile(): DMGR Home = " + str( self.env.was_deploymentManagerHomeDirectory ) + "\n" )
					self.logIt( __name__ + ".generateConfigurationFile(): Deployable Entity Type = " + str( self.env.was_entityType ) + "\n" )
					self.logIt( __name__ + ".generateConfigurationFile(): Node name to deploy = " + str( self.env.was_nodeNameToDeploy ) + "\n" )
					self.logIt( __name__ + ".generateConfigurationFile(): Deployable Entity Status = " + str( self.env.was_entityStatus ) + "\n" )
					if self.env.was_generateConfigurationFile == 'false':
						self.env.was_deploymentConfigFile = self.env.was_applicationConfigFile
				else:
					self.env.was_runDeployment = 'false'
					self.env.was_deploymentConfigFile = 'false'
					self.logIt( __name__ + ".generateConfigurationFile(): Return Code = " + str( self.env.was_configGenerationReturnCode ) + "\n" )
					self.logIt( __name__ + ".generateConfigurationFile(): Generation Result = " + str( self.env.was_configGenerationResult ) + ". Entity name=" + str( self.entity ) + "\n" )
					self.env.was_deploymentStatus 	= 'F'
					self.env.was_entityStatus		= 'X'
					#self.env.was_deploymentCompletionMessage = "Failed when getting configuration file from WDT repository.  Check the log for details..."
					self.env.was_deploymentCompletionMessage = "Failed when getting configuration file from WDT repository.  " + str( self.env.was_configGenerationResult )
					return False
				#Endif
			else:
				self.env.was_deploymentStatus 	= 'F'
				self.env.was_entityStatus		= 'X'
				self.env.was_deploymentCompletionMessage = "The deployment xml file " + str( self.env.was_applicationConfigFile ) + " is not accessible.  Use the WebSphere Toolset to generate the file"
				return False
			#Endif
		except AttributeError, e:
			self.logIt( __name__ + ".generateConfigurationFile(): " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".generateConfigurationFile(): " + str( e )
			return False
		except java.lang.UnsupportedClassVersionError, ue:
			self.logIt( __name__ + ".generateConfigurationFile(): " + str( ue ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".generateConfigurationFile(): " + str( ue )
			return False
		#Endtry

		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	lockUtil()
	#
	#	DESCRIPTION:
	#		Lock utility to create or remove the given lock file.
	#
	#	PARAMETERS:
	#		See below.
	#
	#	RETURN:
	#       A dictionary with something like: { 'lockReturnCodeProperty': '0', 'lockResultProperty': 'T' }
	##################################################################################
	def lockUtil( self, lockFile=None, sleepInterval=None, waitTime=None, lockFileContent=None, action='LOCK' ):
		"""
        Lock utility to create or remove the given lock file.
        PARAMETERS:
            lockFile       -- the lock file.
            sleepInterval  -- the interval in seconds to sleep between checks.
            waitTime       -- the maximum time to wait in seconds.
            lockFileContent-- what to write into the file.
            action         -- 'LOCK' or 'UNLOCK'
        RETURN:
            A dictionary with something like: { 'lockReturnCodeProperty': '0', 'lockResultProperty': 'T' }
		"""
		#######################################
		#	Assume a failure.
		#######################################
		myResult = { 'lockReturnCodeProperty': '1', 'lockResultProperty': 'F' }

		if lockFile is None:
			self.logIt( __name__ + ".lockUtil(): Please specify the lockFile.\n" )
			myResult['lockReturnCodeProperty']	= '1'
			myResult['lockResultProperty']		= 'F'
			return myResult
		#Endif
		if action is None or action != 'LOCK' and action != 'UNLOCK':
			self.logIt( __name__ + ".lockUtil(): Please specify the action as either 'LOCK' or 'UNLOCK'.\n" )
			myResult['lockReturnCodeProperty']	= '1'
			myResult['lockResultProperty']		= 'F'
			return myResult
		#Endif
		if action == 'LOCK' and sleepInterval is None:
			self.logIt( __name__ + ".lockUtil(): Please specify the sleepInterval.\n" )
			myResult['lockReturnCodeProperty']	= '1'
			myResult['lockResultProperty']		= 'F'
			return myResult
		#Endif
		if action == 'LOCK' and lockFileContent is None:
			self.logIt( __name__ + ".lockUtil(): Please specify the lockResultProperty.\n" )
			myResult['lockReturnCodeProperty']	= '1'
			myResult['lockResultProperty']		= 'F'
			return myResult
		#Endif
		self.logIt( __name__ + ".lockUtil(): lockFile=" + str( lockFile ) + "\n" )
		self.logIt( __name__ + ".lockUtil(): action=" + str( action ) + "\n" )
		self.logIt( __name__ + ".lockUtil(): sleepInterval=" + str( sleepInterval ) + "\n" )
		self.logIt( __name__ + ".lockUtil(): waitTime=" + str( waitTime ) + "\n" )
		self.logIt( __name__ + ".lockUtil(): lockFileContent=" + str( lockFileContent ) + "\n" )

		if os.access( lockFile, os.F_OK ) and not os.access( lockFile, os.W_OK ):
			self.logIt( __name__ + ".lockUtil(): Access to " + str( lockFile ) + " is denied.  Perhaps you are the wrong user ==> " + str( os.getlogin() ) + ".  Contact MTS.\n" )
			myResult['lockReturnCodeProperty']	= '1'
			myResult['lockResultProperty']		= 'F'
			return myResult
		#Endif

		if action == 'UNLOCK':
			try:
				os.remove( lockFile )
				self.logIt( __name__ + ".lockUtil(): Unlock of lockFile " + str( lockFile ) + " successful.\n" )
				myResult['lockReturnCodeProperty']	= '0'
				myResult['lockResultProperty']		= 'T'
			except OSError, e:
				self.logIt( __name__ + ".lockUtil(): Unable to remove " + str( lockFile ) + " ==> " + str( e ) + ".\n" )
				myResult['lockReturnCodeProperty']	= '1'
				myResult['lockResultProperty']		= 'F'
				return myResult
			#Endtry
		else:
			currentTimeInSeconds	= int( time.time() )
			maxTimeInSeconds		= currentTimeInSeconds + waitTime
			self.logIt( __name__ + ".lockUtil(): currentTimeInSeconds=" + str( currentTimeInSeconds ) + ".\n" )
			self.logIt( __name__ + ".lockUtil(): maxTimeInSeconds=" + str( maxTimeInSeconds ) + ".\n" )
			while currentTimeInSeconds < int( maxTimeInSeconds ):
				if not os.access( lockFile, os.F_OK ):
					try:
						FH = open( lockFile, "w" )
						FH.write( lockFileContent + "\n" )
						FH.close()
						myResult['lockReturnCodeProperty']	= '0'
						myResult['lockResultProperty']		= 'T'
						self.logIt( __name__ + ".lockUtil(): Creation of lockFile " + str( lockFile ) + " successful.\n" )
						return myResult
					except IOError, e:
						self.logIt( __name__ + ".lockUtil(): Unable to create lockFile " + str( lockFile ) + " ==> " + str( e ) + ".\n" )
						self.logIt( __name__ + ".lockUtil(): Access to " + str( lockFile ) + " is denied.  Perhaps you are the wrong user ==> " + str( os.getlogin() ) + ".  Contact MTS.\n" )
						myResult['lockReturnCodeProperty']	= '1'
						myResult['lockResultProperty']		= 'F'
						return myResult
					#Endtry
				else:
					self.logIt( __name__ + ".lockUtil(): Retrying the creation of the lockFile " + str( lockFile ) + " in " + str( sleepInterval ) +  " seconds.\n" )
					time.sleep( sleepInterval )
					currentTimeInSeconds = int( time.time() )
					deltaTime = maxTimeInSeconds - currentTimeInSeconds
					self.logIt( __name__ + ".lockUtil(): currentTimeInSeconds=" + str( currentTimeInSeconds ) + ".\n" )
					self.logIt( __name__ + ".lockUtil(): Remaining time=" + str( deltaTime ) + ".\n" )
				#Endif
			#Endwhile
			self.logIt( __name__ + ".lockUtil(): Unable to create lockFile " + str( lockFile ) + ".  Time elapsed.\n" )
			myResult['lockReturnCodeProperty']	= '1'
			myResult['lockResultProperty']		= 'F'
		#Endif
		return myResult
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	lockDeployment()
	#
	#	DESCRIPTION:
	#		Lock the deployment.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def lockDeployment(self):
		"""
        Lock the deployment.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		myResults = { 'lockReturnCodeProperty': '0', 'lockResultProperty': 'T' }
		self.logIt( __name__ + ".lockDeployment(): Entered...\n" )
		try:
			if self.env.was_runDeployment == 'true':
				if self.env.was_lockEnable == 'true':
					self.logIt( __name__ + ".lockDeployment(): Trying to get the lock...\n" )
					self.env.was_deploymentLockFile = str( self.env.was_deploymentLockDir ) + '/' + str( self.env.was_domain ) + '.' + str( self.env.was_cellname ) + '.lck'
					self.env.was_lockFileMessage = 'Mnemonic = ' + str( self.env.was_mnemonic ) + ' Install Type = ' + str( self.env.was_deploymentType ) + ' Name = ' + str( self.env.was_entityName )
					myResults = self.lockUtil( lockFile=self.env.was_deploymentLockFile, sleepInterval=int( self.env.was_sleepInterval ), waitTime=int( self.env.was_waitTime ), lockFileContent=self.env.was_lockFileMessage, action='LOCK' )
					self.env.was_lockReturnCodeProperty	= myResults['lockReturnCodeProperty']
					self.env.was_lockResultProperty		= myResults['lockResultProperty']
					if myResults['lockReturnCodeProperty'] == '1':
						self.logIt( __name__ + ".lockDeployment(): Lock failed...\n" )
						self.env.was_deploymentStatus = 'F'
						self.env.was_deploymentCompletionMessage = __name__ + ".lockDeployment(): " + str( 'Lock failed...' )
						return False
					else:
						self.logIt( __name__ + ".lockDeployment(): ....Got the lock\n" )
						self.env.was_gotDeploymentLockFile = 'true'	
						self.logIt( __name__ + ".lockDeployment(): ********************************************************************************\n" )
						self.logIt( __name__ + ".lockDeployment(): * Do not exit this command using Control-C.  Doing so will prevent the command *\n" )
						self.logIt( __name__ + ".lockDeployment(): * from releasing a cell-level lock file upon command completion which blocks   *\n" )
						self.logIt( __name__ + ".lockDeployment(): * all further updates and the world will not be safe for democracy.            *\n" )
						self.logIt( __name__ + ".lockDeployment(): * Please contact MTS App Support if you are locked out.                        *\n" )
						self.logIt( __name__ + ".lockDeployment(): * Personally I think these things should be left to the vote of a majority,    *\n" )
						self.logIt( __name__ + ".lockDeployment(): * like two wolves and a sheep voting on what to have for lunch.                *\n" )
						self.logIt( __name__ + ".lockDeployment(): * All hail democracy where the minority lives at the tyranny of the majority!  *\n" )
						self.logIt( __name__ + ".lockDeployment(): * ....  On second thought,                                                     *\n" )
						self.logIt( __name__ + ".lockDeployment(): * I think I will just stick with liberty for all.  Yeah!  That's the ticket!   *\n" )
						self.logIt( __name__ + ".lockDeployment(): * Just go unlock your own file!  After all you made it!                        *\n" )
						self.logIt( __name__ + ".lockDeployment(): * ..............                                                               *\n" )
						self.logIt( __name__ + ".lockDeployment(): * Sigh.  Most likely you have to get MTS to do it for you, because that is the *\n" )
						self.logIt( __name__ + ".lockDeployment(): * world we live in.  Oh well.  Maybe you should not use the Control-C.  :^(    *\n" )
						self.logIt( __name__ + ".lockDeployment(): * It did look good for a while though. ;^)                                     *\n" )
						self.logIt( __name__ + ".lockDeployment(): * Remember, never be afraid to dream.  Dreamers change the world.              *\n" )
						self.logIt( __name__ + ".lockDeployment(): * I like dreaming about liberty.  Go Ron Paul!                                 *\n" )
						self.logIt( __name__ + ".lockDeployment(): ********************************************************************************\n" )
					#Endif
				#Endif
			#Endif
		except AttributeError, e:
			self.logIt( __name__ + ".lockDeployment(): " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".lockDeployment(): " + str( e )
			return False
		#Endtry
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	startWsadminShell()
	#
	#	DESCRIPTION:
	#		Do the real deployment, finally!
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def startWsadminShell(self):
		"""
        Do the real deployment.  The intent is not to really start a shell.
        Hopefully this will turn out be true.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".startWsadminShell(): Entered...\n" )
		try:
			if self.env.was_runDeployment == 'true':
				self.env.startWsadminShell_executable 				= str( self.env.was_deploymentManagerHomeDirectory ) + "/bin/wsadmin.sh"

				self.logIt( __name__ + ".startWsadminShell(): STUBBED: Execute the " + str( self.env.startWsadminShell_executable ) + " to perform the great works of the Wizard of Oz!\n" )

				self.logIt( __name__ + ".startWsadminShell(): Starting Wsadmin(maybe) on host : " + str( self.env.was_wsadminHostName ) + " port " + str( self.env.was_wsadminRMIConnectorPort )  + "............\n" )
				self.env.was_wsadminErrorLogFile = str( self.env.was_deploymentErrorTempDir ) + str( self.env.was_deploymentId ) + ".error"
				self.env.was_wsadminBootClasspath = str( self.env.was_wdtHome ) + "/" + "/lib/xml.jar"
				##############################################################################
				#	No matter what was.scriptServiceImpl is set to, it must be the value
				#	of was.deploymentServiceDAOImpl when being executed within a 
				#	wsadmin shell.  So set it to was.deploymentServiceDAOImpl here.
				#	If was.deploymentSErviceEJBImpl is desired to be used, write the data
				#	to be worked on during the wsadmin shell process to a file or files
				#	by deploymentId.  Then with the wsadmin shell processing completes,
				#	use the was.deploymentServiceEJBImpl scriptServiceImpl to process the
				#	data in the written files.
				#
				#	NOTE:
				#		We hope to be able to avoid using wsadmin here.  Our intent is to
				#		user pure jython and connect to webshpere via IBM's java libraries
				#		or to have wsadmin call this script to do its work.
				##############################################################################
				self.env.was_thisScriptServiceImpl = self.env.was_deploymentServiceDAOImpl
				self.logIt( __name__ + ".startWsadminShell(): CustomClasspath=" + str( self.env.was_wsadminCustomClasspath ) + "\n" )
				self.logIt( __name__ + ".startWsadminShell(): Bootclasspath=" + str( self.env.was_wsadminBootClasspath ) + " for " + str( self.env.was_cellname ) + "\n" )
				self.logIt( __name__ + ".startWsadminShell(): Using JACL files in " + str( self.env.was_dmpscripts_home ) + " but not really.\n" )
				self.logIt( __name__ + ".startWsadminShell(): scriptServiceImpl : " + str( self.env.was_thisScriptServiceImpl ) + ".\n" )

				self.env.startWsadminShell_javaoption_Xms4m 		= 'true'
				self.env.startWsadminShell_javaoption_Xmx256m 		= 'true'
				self.env.startWsadminShell_javaoption_Xbootclass 	= '/p:' + str( self.env.was_wsadminBootClasspath )
				self.env.startWsadminShell_conntype 				= 'RMI'
				self.env.startWsadminShell_host 					= self.env.was_wsadminHostName
				self.env.startWsadminShell_port 					= self.env.was_wsadminRMIConnectorPort
				self.env.startWsadminShell_wsadmin_classpath 		= self.env.was_wsadminCustomClasspath
				self.env.startWsadminShell_f 						= self.env.was_dmpscripts_home + "/_wasconfig.jacl"
				self.env.startWsadminShell_installType 				= self.env.was_installTypeName
				self.env.startWsadminShell_mnemonic 				= self.env.was_mnemonic
				self.env.startWsadminShell_domain 					= self.env.was_domain
				self.env.startWsadminShell_wdtHomePath 				= self.env.was_wdtHome + '/bin/' + self.env.was_domainVersion + '/jacl'
				self.env.startWsadminShell_deploymentConfigFile 	= self.env.was_deploymentConfigFile
				self.env.startWsadminShell_nodeNameToDeploy 		= self.env.was_nodeNameToDeploy
				self.env.startWsadminShell_isProcessAppMgmtUpdate 	= self.env.was_isProcessAppMgmtUpdate
				self.env.startWsadminShell_wdtHome 					= self.env.was_wdtHome
				self.env.startWsadminShell_deployableApplication 	= self.env.was_deployableApplication
				self.env.startWsadminShell_updatekey 				= self.env.was_updatekey
				self.env.startWsadminShell_thisScriptServiceImpl 	= self.env.was_thisScriptServiceImpl

				################################################################################
				#	Log the variables.
				################################################################################
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_javaoption_Xms4m: " + str( self.env.startWsadminShell_javaoption_Xms4m ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_javaoption_Xmx256m: " + str( self.env.startWsadminShell_javaoption_Xmx256m ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_javaoption_Xbootclass: " + str( self.env.startWsadminShell_javaoption_Xbootclass ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_javaoption_Xbootclass: " + str( self.env.startWsadminShell_javaoption_Xbootclass ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_conntype: " + str( self.env.startWsadminShell_conntype ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_host: " + str( self.env.startWsadminShell_host ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_port: " + str( self.env.startWsadminShell_port ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_wsadmin_classpath: " + str( self.env.startWsadminShell_wsadmin_classpath ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_f: " + str( self.env.startWsadminShell_f ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_installType: " + str( self.env.startWsadminShell_installType ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_mnemonic: " + str( self.env.startWsadminShell_mnemonic ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_domain: " + str( self.env.startWsadminShell_domain ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_wdtHomePath: " + str( self.env.startWsadminShell_wdtHomePath ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_deploymentConfigFile: " + str( self.env.startWsadminShell_deploymentConfigFile ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_nodeNameToDeploy: " + str( self.env.startWsadminShell_nodeNameToDeploy ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_isProcessAppMgmtUpdate: " + str( self.env.startWsadminShell_isProcessAppMgmtUpdate ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_wdtHome: " + str( self.env.startWsadminShell_wdtHome ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_deployableApplication: " + str( self.env.startWsadminShell_deployableApplication ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_updatekey: " + str( self.env.startWsadminShell_updatekey ) + ".\n" )
				self.logIt( __name__ + ".startWsadminShell(): self.env.startWsadminShell_thisScriptServiceImpl: " + str( self.env.startWsadminShell_thisScriptServiceImpl ) + ".\n" )

				################################################################################
				#	For now we stub the implementation of the wsadmin call.  Again our hope is
				#	to not fork another shell but to make the java class calls directly.
				################################################################################
				self.logIt( __name__ + ".startWsadminShell(): startWsadminShell : " + str( self.env.startWsadminShell_executable ) + ".\n" )
				self.env.was_wsadminCommandResult = '0'
				self.logIt( __name__ + ".startWsadminShell(): WSADMIN Command Result : " + str( self.env.was_wsadminCommandResult ) + ".\n" )

				if self.env.was_wsadminCommandResult == '0':
					self.env.was_completedDeployment			= 'true'
					self.env.was_deploymentStatus 				= 'S'
					self.env.was_deploymentHasError 			= 'false'
					self.env.was_deploymentCompletionMessage 	= 'Successfully deployed ' + str( self.env.was_entityName )
				else:
					self.logIt( __name__ + ".startWsadminShell(): Return Code : " + str( self.env.was_wsadminCommandResult ) + ".\n" )
					self.env.was_completedDeployment			= 'false'
					self.env.was_deploymentHasError 			= 'true'
					self.env.was_deploymentStatus 				= 'F'
					self.logIt( __name__ + ".startWsadminShell(): status = " + str( self.env.was_deploymentStatus ) + ".\n" )
					self.env.was_deploymentCompletionMessage 	= 'Failed when running the wsadmin jacl scripts.  Check the log for details...'
				#Endif
			#Endif
		except AttributeError, e:
			self.logIt( __name__ + ".startWsadminShell(): " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".startWsadminShell(): " + str( e )
			return False
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	logDeployment()
	#
	#	DESCRIPTION:
	#		Log deployment.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def logDeployment(self):
		"""
        Log the deployment.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".logDeployment(): Entered...\n" )
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	unlockDeployment()
	#
	#	DESCRIPTION:
	#		Unlock the deployment.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def unlockDeployment(self):
		"""
        Unlock the deployment.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".unlockDeployment(): Entered...\n" )
		if self.env.was_lockEnabled == 'true':
			self.logIt( __name__ + ".unlockDeployment(): Releasing the lock...\n" )
			myResults = self.lockUtil( lockFile=self.env.was_deploymentLockFile, action='UNLOCK' )
			if myResults['lockReturnCodeProperty'] == '1':
				self.logIt( __name__ + ".unlockDeployment(): lockResultsProperty=" + str( myResults['lockResultProperty'] ) + "\n" )
				self.env.was_deploymentStatus = 'F'
				self.env.was_deploymentCompletionMessage = __name__ + ".unlockDeployment(): lockResultsProperty=" + str( myResults['lockResultProperty'] ) 
				return False
			else:
				self.logIt( __name__ + ".unlockDeployment(): ....Released the lock.\n" )
			#Endif
		#Endif
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	completeDeployment()
	#
	#	DESCRIPTION:
	#		Complete deployment.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def completeDeployment(self):
		"""
        Complete deployment.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".completDeployment(): Entered...\n" )
		try:
			self.logIt( __name__ + ".completDeployment(): Deployment status = " + str( self.env.was_deploymentStatus ) + "\n" )
			self.logIt( __name__ + ".completDeployment(): Deployment message = " + str( self.env.was_deploymentCompletionMessage ) + "\n" )
			self.logIt( __name__ + ".completDeployment(): Domain = " + str( self.env.was_domain ) + "\n" )
			self.logIt( __name__ + ".completDeployment(): DeploymentId = " + str( self.env.was_deploymentId ) + "\n" )
			self.logIt( __name__ + ".completDeployment(): Entity Name = " + str( self.env.was_entityName ) + "\n" )
			self.logIt( __name__ + ".completDeployment(): Entity Status = " + str( self.env.was_entityStatus ) + "\n" )
			self.logIt( __name__ + ".completDeployment(): Entity Type = " + str( self.env.was_entityType ) + "\n" )
			self.logIt( __name__ + ".completDeployment(): Update User = " + 'SYSTEM' + "\n" )
			self.logIt( __name__ + ".completDeployment(): Action = " + 'UPDATE_STATUS' + "\n" )
			self.env.was_dbErrorFlagUpdateEntry = 'false'
			self.env.was_dbErrorMessageUpdateEntry = 'This has been faked out in completeDeployment() for now.'
		except AttributeError, e:
			self.logIt( __name__ + ".completeDeployment(): " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".completeDeployment(): " + str( e )
			return False
		#Endtry
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	printSummary()
	#
	#	DESCRIPTION:
	#		Print summary of deployment.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def printSummary(self):
		"""
        Print the summary of the deployment.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".printSummary(): Entered...\n" )
		try:
			self.logIt( __name__ + ".printSummary(): ------------------------------------Summary----------------------------------\n" )
			self.logIt( __name__ + ".printSummary(): Deployment Id : " + str( self.env.was_deploymentId ) + "\n" )
			self.logIt( __name__ + ".printSummary(): Deployment Type : " + str( self.env.was_installTypeName ) + "\n" )
			self.logIt( __name__ + ".printSummary(): Deployment Status (S - success / F - Fail) : " + str( self.env.was_deploymentStatus ) + "\n" )
			self.logIt( __name__ + ".printSummary(): Deployment Message : " + str( self.env.was_deploymentCompletionMessage ) + "\n" )

			self.env.displayNotice = 'no'
			if self.env.was_installTypeName.lower() == 'stop_application':
				self.env.displayNotice = 'yes'
			#Endif
			if self.env.was_installTypeName.lower() == 'install_application':
				self.env.displayNotice = 'yes'
			#Endif
			if self.env.was_dbErrorFlagCreateEntry == 'true':
				self.logIt( __name__ + ".printSummary(): Warning : 1\n" )
				self.logIt( __name__ + ".printSummary(): DB error (creating new deployment) : " + str( self.env.was_dbErrorMessageCreateEntry ) + "\n" )
			#Endif
			if self.env.was_dbErrorFlagUpdateEntry == 'true':
				self.logIt( __name__ + ".printSummary(): Warning : 2\n" )
				self.logIt( __name__ + ".printSummary(): DB error (updating deployment status) : " + str( self.env.was_dbErrorMessageUpdateEntry ) + " \n" )
			#Endif
			if self.env.was_deploymentStatus == 'S':
				self.logIt( __name__ + ".printSummary(): Deployment of " + str( self.env.was_entityName ) + " completed successfully\n" )
			else:
				if self.env.displayNotice == 'yes':
					self.logIt( __name__ + ".printSummary():****************************** IMPORTANT NOTE *****************************\n" )
					self.logIt( __name__ + ".printSummary():*    For NON-PORTLET Applications:\n" )
					self.logIt( __name__ + ".printSummary():*      If this failure is due to an attempt to stop the application, submit a\n" )
					self.logIt( __name__ + ".printSummary():*      request to restart the cluster and try deploying again.\n" )
					self.logIt( __name__ + ".printSummary():*    For PORTLET Applications:\n" )
					self.logIt( __name__ + ".printSummary():*      If this failure is due to an attempt to stop the application, do NOT\n" )
					self.logIt( __name__ + ".printSummary():*      make a request to restart the cluster.  The portlet cluster is shared\n" )
					self.logIt( __name__ + ".printSummary():*      by all PORTLET applications.  First determine which of the portlet cluster\n" )
					self.logIt( __name__ + ".printSummary():*      app servers are experiencing a problem by checking the app server logs.\n" )
					self.logIt( __name__ + ".printSummary():*      Then make a request to have these app servers restarted and try again.\n" )
					self.logIt( __name__ + ".printSummary():***************************************************************************\n" )

					self.logIt( __name__ + ".printSummary(): Error Message : " + str( self.env.was_deploymentCompletionMessage ) + "\n" )
				#Endif
			#Endif
			self.logIt( __name__ + ".printSummary(): -----------------------------------------------------------------------------\n" )
		except AttributeError, e:
			self.logIt( __name__ + ".printSummary(): " + str( e ) + "\n" )
			return False
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	generatePlugin()
	#
	#	DESCRIPTION:
	#		Generate deployment plugin.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def generatePlugin(self):
		"""
        Generate the deployment plugin.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".generatePlugin(): Entered...\n" )
		try:
			if self.env.was_deploymentHasError != 'true':
				if self.env.was_nodeSpecificOperation.lower() == 'true':	
					self.env.was_generateThePlugin = 'false'
				else:
					self.env.was_generateThePlugin = self.env.was_generatePlugin
				#Endif
			#Endif
			self.logIt( __name__ + ".generatePlugin(): was_generateThePlugin after = " + str( self.env.was_generateThePlugin ) + "\n" )

			if self.env.was_generateThePlugin.lower() == 'true':
				#######################################################################
				#	Stubbed for now, but this must call the webServerPluginUtil java
				#	class.
				#######################################################################
				self.logIt( __name__ + ".generatePlugin(): STUBBED: Call the webSeverPluginUtil class to determine the cluster name and plugin level.\n" )
				self.env.webServerPluginUtil_domainName				= self.env.was_domain	
				self.env.webServerPluginUtil_appConfigXML			= self.env.was_applicationConfigFile	
				self.env.webServerPluginUtil_clusterName			= "was.clusterName"	
				self.env.webServerPluginUtil_pluginLevel			= "was.pluginLevel"
				self.env.webServerPluginUtil_pluginMessageProperty	= "was.PluginMessage"

				###################################
				#	Fake out the results for now.
				###################################
				self.env.was_clusterName	= 'MY_CLUSTER_set_in_generatePlugin'
				self.env.was_PluginMessage	= "This message would have been returned from the webServerPluginUtil if it was actually called."
				self.env.was_pluginLevel	= "CLUSTER"
				
				self.logIt( __name__ + ".generatePlugin(): " + str( self.env.was_PluginMessage ) + "\n" )
				if self.env.was_pluginLevel == 'CLUSTER':
					self.env.was_tempPluginFile = str( self.env.was_pluginCopyDir ) + '/plugin-cfg.xml.' + str( self.env.was_domain ) + '.' + str( self.env.was_cellname ) + '.' + str( self.env.was_clusterName )
					self.env.was_regenPluginExec_executable = str( self.env.was_deploymentManagerHomeDirectory ) + '/bin/' + str( self.env.was_regenPluginExec )
					self.env.was_regenPluginExec_cluster_name = str( self.env.was_clusterName )
					self.env.was_regenPluginExec_output_file_name = str( self.env.was_tempPluginFile )

					self.logIt( __name__ + ".generatePlugin(): STUBBED: Run the " + str( self.env.was_regenPluginExec_executable ) + " to generate the plugin CLUSTER.\n" )
					self.logIt( __name__ + ".generatePlugin(): was_regenPluginExec " + str( self.env.was_regenPluginExec_executable ) + "\n" )

					###################################################
					#	Fake out the results of the executable for now.
					###################################################
					self.env.was_pluginRegenCommandResult = '0'	
					self.logIt( __name__ + ".generatePlugin(): Result = " + str( self.env.was_pluginRegenCommandResult ) + "\n" )
					self.logIt( __name__ + ".generatePlugin(): The plugin file was saved to " + str( self.env.was_tempPluginFile ) + "\n" )
					rs = self.sedFile( file=self.env.was_tempPluginFile, originalToken=r'/usr/IBM/WebSphere/Plugins/logs/http_plugin.log', replacementToken=r'/dmp/logs/MNE/http_plugin_dmpAPP.log' )
					if rs:
						rs = self.sedFile( file=self.env.was_tempPluginFile, originalToken=r'RetryInterval=&quot;60&quot;', replacementToken=r'RetryInterval=&quot;' + str( self.env.was.retryInterval ) + '&quot;' )
					if rs:
						rs = self.sedFile( file=self.env.was_tempPluginFile, originalToken=r'ConnectTimeout=&quot;0&quot;', replacementToken=r'ConnectTimeout=&quot;' + str( self.env.was_connectTimeout ) + '&quot;' )

					if not rs:
						self.env.was_deploymentStatus = 'F'
						self.env.was_deploymentCompletionMessage = __name__ + ".generatePlugin(): " + "Unable to perform the required edits to the " + str( self.env.was_tempPluginFile ) + " file."
						return False
				elif self.env.was_pluginLevel == 'CELL':

					self.env.was_regenPluginExec_executable = str( self.env.was_deploymentManagerHomeDirectory ) + '/bin/' + str( self.env.was_regenPluginExec )
					self.logIt( __name__ + ".generatePlugin(): STUBBED: Run the " + str( self.env.was_regenPluginExec_executable ) + " to generate the plugin for the CELL.\n" )
					###################################################
					#	Fake out the results of the executable for now.
					###################################################
					self.env.was_pluginRegenCommandResult = '0'	
					self.logIt( __name__ + ".generatePlugin(): Result = " + str( self.env.was_pluginRegenCommandResult ) + "\n" )
					self.env.was_tempPluginFile = str( self.env.was_pluginCopyDir ) + '/plugin-cfg.xml.' + str( self.env.was_domain ) + '.' + str( self.env.was_cellname )
					src = self.env.was_deploymentManagerHomeDirectory + '/' + self.env.was_regenPluginFile
					dest= self.env.was_tempPluginFile
					shutil.copyfile( src, dest )
					rs = self.sedFile( file=self.env.was_tempPluginFile, originalToken=self.env.was_deploymentManagerHomeDirectory + '/logs/http_plugin.log', replacementToken='/dmp/logs/MNE/http_plugin_dmpAPP.log' )
						
					if rs:
						rs = self.sedFile( file=self.env.was_tempPluginFile, originalToken='RetryInterval=&quot;60&quot;', replacementToken='RetryInterval=&quot;' + str( self.env.was.retryInterval ) + '&quot;' )
					if rs:
						rs = self.sedFile( file=self.env.was_tempPluginFile, originalToken='ConnectTimeout=&quot;0&quot;', replacementToken='ConnectTimeout=&quot;' + str( self.env.was_connectTimeout ) + '&quot;' )
					if not rs:
						self.env.was_deploymentStatus = 'F'
						self.env.was_deploymentCompletionMessage = __name__ + ".generatePlugin(): " + "Unable to perform the required edits to the " + str( self.env.was_tempPluginFile ) + " file."
						return False
				#Endif
			#Endif
		except AttributeError, e:
			self.logIt( __name__ + ".generatePlugin(): " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".generatePlugin(): " + str( e )
			return False
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	cleanUp()
	#
	#	DESCRIPTION:
	#		Clean up the deployment.
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def cleanUp(self):
		"""
        Clean up the deployment.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".cleanUp(): Entered...\n" )
		try:
			if self.env.was_deploymentStatus == 'S':
				self.logIt( __name__ + ".cleanUp(): Deployment of " + str( self.env.was_entityName ) + " completed successfully\n" )

				if self.env.was_handleGeneratedConfigFile.lower() == 'delete':
					os.remove( self.env.was_deploymentConfigFile )

				elif self.env.was_handleGeneratedConfigFile.lower() == 'save_to_app_location':
					self.env.was_appConfigFileName = str( self.env.was_mneServerConfigDir ) + '/' + str( self.env.was_entityName ) + '_serverproperties.xml'
					if os.access( self.env.was_appConfigFileName, F_OK ):
						shutil.copyfile( self.env.was_appConfigFileName, self.env.was_appConfigFileName + '.old' )
					#Endif
					shutil.copyfile( self.env.was_deploymentConfigFile, self.env.was_appConfigFileName )
					os.remove( self.env.was_deploymentConfigFile )

				elif self.env.was_handleGeneratedConfigFile.lower() == 'keep':
					self.logIt( __name__ + ".cleanUp(): Keeping the generated config file...\n" )

				elif self.env.was_handleGeneratedConfigFile.lower() == 'no_action':
					self.logIt( __name__ + ".cleanUp(): No cleanup action specified...\n" )

				else:
					self.logIt( __name__ + ".cleanUp(): No cleanup action specified...\n" )
				#Endif
			else:
				if self.env.was_handleGeneratedConfigFile.lower() == 'delete':
					os.remove( self.env.was_deploymentConfigFile )
				#Endif
			#Endif
			try:
				for file in os.listdir( './' ):
					if re.match( 'orbtrc.*\.txt', file ):
						self.logIt( __name__ + ".cleanUp(): Removing " + str( file ) + "\n" )
						os.remove( file )
					#Endif
				#Endfor
			except OSError, e:
				self.logIt( __name__ + ".cleanUp(): " + str( e ) + '\n' )
			#Endtry
			try:
				for file in os.listdir( '/home/was5/' ):
					if re.match( 'orbtrc.*\.txt', file ):
						self.logIt( __name__ + ".cleanUp(): Removing " + str( file ) + "\n" )
						os.remove( file )
					#Endif
				#Endfor
			except OSError, e:
				self.logIt( __name__ + ".cleanUp(): " + str( e ) + '\n' )
			#Endtry
		except AttributeError, e:
			self.logIt( __name__ + ".cleanUp(): " + str( e ) + "\n" )
			self.env.was_deploymentStatus = 'F'
			self.env.was_deploymentCompletionMessage = __name__ + ".cleanUp(): " + str( e )
			return False
		#Endtry
		return True
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	controlApplication()
	#
	#	DESCRIPTION:
	#		Control the application
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def controlApplication(self):
		"""
        Control the application.  The method depends on:
        generateConfigurationFile()
        generatePlugin()
        startWsadminShell()
        cleanUp()
        printSummary()
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".controlApplication(): Entered...\n" )
		rc = True
		rc = self.generateConfigurationFile()
		if rc: rc = self.generatePlugin()
		if rc: rc = self.startWsadminShell()
		if rc: rc = self.cleanUp()
		self.printSummary()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	controlCluster()
	#
	#	DESCRIPTION:
	#		Control the cluster
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def controlCluster(self):
		"""
        Control the cluster.  The method depends on:
        generateConfigurationFile()
        startWsadminShell()
        cleanUp()
        printSummary()
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".controlCluster(): Entered...\n" )
		rc = True
		rc = self.generateConfigurationFile()
		if rc: rc = self.startWsadminShell()
		if rc: rc = self.cleanUp()
		self.printSummary()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	configureApplication()
	#
	#	DESCRIPTION:
	#		Configure the application
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def configureApplication(self):
		"""
        Configure the application.  The method depends on:
        createDeploymentEntry()
        generateConfigurationFile()
        lockDeployment()
        startWsadminShell()
        unlockDeployment()
        completeDeployment()
        cleanUp()
        generatePlugin()
        printSummary()
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".configureApplication(): Entered...\n" )
		rc	= True
		rc = self.createDeploymentEntry()
		if rc: rc = self.generateConfigurationFile()
		if rc: rc = self.lockDeployment()
		if rc: rc = self.startWsadminShell()
		if rc: rc = self.unlockDeployment()
		if rc: rc = self.completeDeployment()
		if rc: rc = self.cleanUp()
		if rc: rc = self.generatePlugin()
		self.printSummary()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	deleteDataSources()
	#
	#	DESCRIPTION:
	#		Configure the application
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def deleteDataSources(self):
		"""
        Configure the application.  The method depends on:
        generateConfigurationFile()
        lockDeployment()
        startWsadminShell()
        unlockDeployment()
        completeDeployment()
        cleanUp()
        printSummary()
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".deleteDataSources(): Entered...\n" )
		rc	= True
		rc = self.generateConfigurationFile()
		if rc: rc = self.lockDeployment()
		if rc: rc = self.startWsadminShell()
		if rc: rc = self.unlockDeployment()
		if rc: rc = self.completeDeployment()
		if rc: rc = self.cleanUp()
		self.printSummary()
		return rc
	#### #############################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	processCreateClusterConfiguration()
	#
	#	DESCRIPTION:
	#		Configure the cluster
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def processCreateClusterConfiguration(self):
		"""
        Create the cluster from history.  The method depends on:
		Not implemented in the build.xml file.
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".processCreateClusterConfiguration(): Entered...\n" )
		self.logIt( __name__ + ".processCreateClusterConfiguration(): Currently not implemented.\n" )
		self.env.was_deploymentStatus = 'F'
		self.env.was_deploymentCompletionMessage = __name__ + ".processCreateClusterConfiguration(): Currently not implemented."
		return False
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	configureCluster()
	#
	#	DESCRIPTION:
	#		Configure the cluster
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def configureCluster(self):
		"""
        Configure the cluster.  The method depends on:
        createDeploymentEntry()
        generateConfigurationFile()
        logDeployment()
        startWsadminShell()
        unlockDeployment()
        completeDeployment()
        cleanUp()
        printSummary()
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".configureCluster(): Entered...\n" )
		rc = True
		rc = self.createDeploymentEntry()
		if rc: rc = self.generateConfigurationFile()
		if rc: rc = self.lockDeployment()
		if rc: rc = self.startWsadminShell()
		if rc: rc = self.unlockDeployment()
		if rc: rc = self.completeDeployment()
		if rc: rc = self.cleanUp()
		self.printSummary()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	configureWebServer()
	#
	#	DESCRIPTION:
	#		Configure the web server
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def configureWebServer(self):
		"""
        Configure the web server.  The method depends on:
        initWebServer()
        getWebServerPort()
        createWebServer()
        printWebServerSummary()
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".configureWebServer(): Entered...\n" )
		rc	= True
		rc = self.initWebServer()
		if rc: rc = self.getWebServerPort()
		if rc: rc = self.createWebServer()
		self.printWebServerSummary()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	controlWebServer()
	#
	#	DESCRIPTION:
	#		Control the web server
	#
	#	PARAMETERS:
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def controlWebServer(self):
		"""
        Control the web server.  The method depends on:
        initWebServer()
        getWebServerPort()
        startStopWebServer()
        printWebServerSummary()
        PARAMETERS:
        RETURN:
            True if successful, or False
		"""
		self.logIt( __name__ + ".controlWebServer(): Entered...\n" )
		rc	= True
		rc = self.initWebServer()
		if rc: rc = self.getWebServerPort()
		if rc: rc = self.startStopWebServer()
		self.printWebServerSummary()
		return rc
	##################################################################################
	#Enddef
	##################################################################################


	##################################################################################
	#	recreate()
	#
	#	DESCRIPTION:
	#		Perform a WAS recreate
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
    #       True if successful, or False
	##################################################################################
	def recreate(self, type='CREATE_CLUSTER', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS recreate.
        PARAMETERS:
            type        - the install type.  something like 'CREATE_CLUSTER'
            serviceType - the install service type.  something like 'CELL' or 'CELL,NODE'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
            True if successful, or False
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".recreate(): Running recreate action.\n" )
		rc = True
		rc = self.evaluateInstallType()
		if not rc: return False
		rc = self.configureCluster()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	recreateAll()
	#
	#	DESCRIPTION:
	#		Perform a WAS recreateAll
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
	##################################################################################
	def recreateAll2(self, type='CREATE_CLUSTER', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS recreate.
        PARAMETERS:
            type        - the install type.  something like 'CREATE_CLUSTER'
            serviceType - the install service type.  something like 'CELL' or 'CELL,NODE'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".recreateAll(): Running recreate action.\n" )
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	recreateAll()
	#
	#	DESCRIPTION:
	#		Perform a WAS recreateAll
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
	##################################################################################
	def recreateAll(self, type='RECREATE_CLUSTER', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS recreateAll.
        PARAMETERS:
            type        - the install type.  something like 'RECREATE_CLUSTER'
            serviceType - the install service type.  something like 'CELL' or 'CELL,NODE'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".update(): Running recreateAll action.\n" )
		rc = True
		rc = self.evaluateInstallType()
		if not rc: return rc
		rc = self.configureCluster()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	addJDBCProvider()
	#
	#	DESCRIPTION:
	#		Perform a WAS addJDBCProvider
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
	##################################################################################
	def addJDBCProvider(self, type='ADD_JDBC_PROVIDER', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS addJDBCProvider.
        PARAMETERS:
            type        - the install type.  something like 'ADD_JDBC_PROVIDER'
            serviceType - the install service type.  something like 'CELL' or 'CELL,NODE'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".update(): Running addJDBCProvider action.\n" )
		rc	= True
		rc = self.evaluateInstallType()
		if not rc: return False
		rc = self.configureCluster()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	recreateJDBCProvider()
	#
	#	DESCRIPTION:
	#		Perform a WAS recreateJDBCProvider
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
	##################################################################################
	def recreateJDBCProvider(self, type='RECREATE_JDBC_PROVIDER', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS recreateJDBCProvider.
        PARAMETERS:
            type        - the install type.  something like 'RECREATE_JDBC_PROVIDER'
            serviceType - the install service type.  something like 'CELL' or 'CELL,NODE'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".update(): Running recreateJDBCProvider action.\n" )
		rc	= True
		rc = self.evaluateInstallType()
		if not rc: return False
		rc = self.configureCluster()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	update()
	#
	#	DESCRIPTION:
	#		Perform a WAS update
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
	##################################################################################
	def update(self, type='INSTALL_APPLICATION', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS update.
        PARAMETERS:
            type        - the install type.  something like 'INSTALL_APPLICATION', 'UPDATE_CLUSTER', or 'CONFIGURE_WEB_SERVER'
            serviceType - the install service type.  something like 'CELL', 'CELL,NODE' 'WEB_SERVER'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".update(): Running update action.\n" )
		rc	= True
		rc = self.evaluateInstallType()
		if not rc: return False
		if type == 'UPDATE_CLUSTER':
			rc = self.configureCluster()
		elif type == 'CONFIGURE_WEB_SERVER':
			rc = self.configureWebServer()
		else:
			rc = self.configureApplication()
		#Endif
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	dsdelete()
	#
	#	DESCRIPTION:
	#		Perform a WAS dsdelete
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
	##################################################################################
	def dsdelete(self, type='DELETE_DATASOURCES', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS dsdelete.
        PARAMETERS:
            type        - the install type.  something like 'INSTALL_APPLICATION'
            serviceType - the install service type.  something like 'CELL' or 'CELL,NODE'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".update(): Running dsdelete action.\n" )
		rc	= True
		rc = self.evaluateInstallType()
		if not rc: return False
		rc = self.deleteDataSources()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	start()
	#
	#	DESCRIPTION:
	#		Perform a WAS start
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
	##################################################################################
	def start(self, type='START_APPLICATION', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS start.
        PARAMETERS:
            type        - the install type.  something like 'START_APPLICATION', 'START_CLUSTER' or 'START_WEB_SERVER'
            serviceType - the install service type.  something like 'CELL', 'CELL,NODE', or 'WEB_SERVER'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".start(): Running start action.\n" )
		rc	= True
		rc = self.evaluateInstallType()
		if not rc: return False
		if type == 'START_APPLICATION':
			rc = self.controlApplication()
		elif type == 'START_WEB_SERVER':
			rc = self.controlWebServer()
		else:
			rc = self.controlCluster()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	stop()
	#
	#	DESCRIPTION:
	#		Perform a WAS stop application
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
	##################################################################################
	def stop(self, type='STOP_APPLICATION', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS stop application.
        PARAMETERS:
            type        - the install type.  something like 'STOP_APPLICATION', 'STOP_CLUSTER' or 'STOP_WEB_SERVER'
            serviceType - the install service type.  something like 'CELL', 'CELL,NODE', or 'WEB_SERVER'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".stop(): Running stop action.\n" )
		rc	= True
		rc = self.evaluateInstallType()
		if not rc: return False
		if type == 'STOP_APPLICATION':
			rc = self.controlApplication()
		elif type == 'STOP_WEB_SERVER':
			rc = self.controlWebServer()
		else:
			rc = self.controlCluster()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	restart()
	#
	#	DESCRIPTION:
	#		Perform a WAS restart
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
	##################################################################################
	def restart(self, type='RESTART_APPLICATION', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS restart.
        PARAMETERS:
            type        - the install type.  something like 'RESTART_APPLICATION', 'RESTART_CLUSTER', 'RESTART_CLUSTER_RIPPLE', or RESTART_WEB_SERVER'
            serviceType - the install service type.  something like 'CELL', 'CELL,NODE', 'WEB_SERVER'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".restart(): Running restart action.\n" )
		rc	= True
		if type == 'RESTART_APPLICATION':
			rc = self.evaluateInstallType()
			if not rc: return False
			rc = self.controlApplication()
		elif type == 'RESTART_WEB_SERVER':
			self.env.install_type = 'STOP_WEB_SERVER'
			rc = self.evaluateInstallType()
			if not rc: return False
			rc = self.controlWebServer()
			if rc:
				self.env.install_type = 'START_WEB_SERVER'
				rc = self.evaluateInstallType()
				if not rc: return False
				rc = self.controlWebServer()
			else:
				self.logIt( __name__ + ".restart(): Unable to stop the web server.\n" )
				return False	
			#Endif
		else:
			rc = self.evaluateInstallType()
			if not rc: return False
			rc = self.controlCluster()
		#Endif
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	check()
	#
	#	DESCRIPTION:
	#		Perform a WAS check
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
	##################################################################################
	def check(self, type='CHECK_APPLICATION', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS check.
        PARAMETERS:
            type        - the install type.  something like 'CHECK_APPLICATION'
            serviceType - the install service type.  something like 'CELL' or 'CELL,NODE'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".check(): Running check action.\n" )
		rc	= True
		rc = self.evaluateInstallType()
		if not rc: return False
		rc = self.controlApplication()
		return rc
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	remove()
	#
	#	DESCRIPTION:
	#		Perform a WAS remove
	#
	#	PARAMETERS:
	#		type		- the install type
	#		serviceType - the install service type
	#		target		- typically 'evaluateInstallType'
	#
	#	RETURN:
	##################################################################################
	def remove(self, type='UNINSTALL_APPLICATION', serviceType=None, target='evaluateInstallType'):
		"""
        Perform a WAS remove.
        PARAMETERS:
            type        - the install type.  something like 'UNINSTALL_APPLICATION' or 'REMOVE_CLUSTER'
            serviceType - the install service type.  something like 'CELL' or 'CELL,NODE'
            target      - the install target.  typically 'evaluateInstallType'
        RETURN:
		"""
		setattr( self.env, "install_type", type )
		setattr( self.env, "install_serviceType", serviceType )
		setattr( self.env, "install_target", target )
		self.logIt( __name__ + ".check(): Running remove action.\n" )
		rc	= True
		rc = self.evaluateInstallType()
		if not rc: return False
		if type == 'UNINSTALL_APPLICATION':
			rc = self.configureApplication()
		else:
			rc = self.configureCluster()
		return rc
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
		Utils.closeMe(self)
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
def foo():
	print "Hello world."

def main():
	myLogger	= MyLogger( LOGFILE="/tmp/WasOps.log", STDOUT=True, DEBUG=False )
	#myObject	= WasOps( logger=myLogger, processCallBack=foo, mnemonic='TRR', entity='app_trr_toolsetTesterB', properties_file='/nfs/dist/dmp/WDT/PROD/bin/v6/ant/build_v6.properties', domain='V6_PROD' )
	myObject	= WasOps( logger=myLogger, processCallBack=foo, mnemonic='TRR', entity='app_trr_toolsetTesterB', domain='V6_DEV' )
	myObject.env.logMySelf( debugOnly=False )
	myObject.logMySelf( debugOnly=False )
	myObject.processRequest()
	#myObject.updatePortalWebServerPlugin( serviceType='WEB_SERVER', target='evaluateInstallType' )
	myResult 	= myObject.lockUtil( lockFile='/tmp/denis.lock', sleepInterval=2, waitTime=5, lockFileContent='This is my lock...', action='LOCK' )
	print( "myResult['lockReturnCodeProperty']=" + str( myResult['lockReturnCodeProperty'] ) )
	print( "myResult['lockResultProperty']=" + str( myResult['lockResultProperty'] ) )
	myResult 	= myObject.lockUtil( lockFile='/tmp/denis.lock', action='UNLOCK' )
	print( "myResult['lockReturnCodeProperty']=" + str( myResult['lockReturnCodeProperty'] ) )
	print( "myResult['lockResultProperty']=" + str( myResult['lockResultProperty'] ) )

	myObject.closeMe()
	##################################################################################
	#Enddef
	##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
	main()

