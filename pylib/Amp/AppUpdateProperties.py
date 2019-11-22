#!/usr/bin/env python
######################################################################################
##	AppUpdateProperties.py
##
##	Python module deals with the AMP XML PUKE file.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	08/06/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.XML.MyAttribute import *
from pylib.XML.MyElement import *
from pylib.XML.MyXML import *


class AppUpdateProperties(MyXML):
    """
    AppUpdateProperties class that deals with the AMP XML PUKE file
    NOTE:  This class was originally written in jython 2.7 and is dependant
    on pylib.XML.MyXML which has not been tested since it was converted to
    python 3.
    """

    ##################################################################################
    #	__init__()
    #
    #	DESCRIPTION:
    #		Class initializer.
    #
    #	PARAMETERS:
    #		xml_file		- something like "file:///nfs/dist/trp/amp/update/UAT/QUAL/QAMP_UAT0000000_090504130000i/QAMP_UAT0000000_090504130000i.xml"
    #		tag_version		- Version of the <applicationUpdateProperties> element
    #		max_was_version	- Version of the <componentDefinitions><websphere> elements
    #		lib_version		- Version of the <compenentDefinitions><sharedLib> elements
    #		generic_verson	- Version of the <compenentDefinitions><runablProcess> elements
    #		quasi_version	- Version of the <compenentDefinitions><quasi> elements
    #
    #	RETURN:
    #		An instance of this class
    ##################################################################################
    def __init__(
            self,
            logger=None,
            xml_file="",
            tag_version="1.0",
            max_was_version="7.0",
            lib_version="1.0",
            generic_version="1.0",
            quasi_version="1.0"
    ):
        """Class Initializer.
           PARAMETERS:
               xml_file         - something like "file:///nfs/dist/trp/amp/update/UAT/QUAL/QAMP_UAT0000000_090504130000i/QAMP_UAT0000000_090504130000i.xml"
               tag_version      - Version of the <applicationUpdateProperties> element
               max_was_version  - Version of the <componentDefinitions><websphere> elements
               lib_version      - Version of the <compenentDefinitions><sharedLib> elements
               generic_verson   - Version of the <compenentDefinitions><runablProcess> elements
               quasi_version    - Version of the <compenentDefinitions><quasi> elements

           RETURN:
               An instance of this class
        """

        self.xml_file = xml_file
        self.tag_version = tag_version
        self.max_was_version = max_was_version
        self.lib_version = lib_version
        self.generic_version = generic_version
        self.quasi_version = quasi_version
        self.logger = logger
        self.utils = MyUtils()
        self.FILES = []
        self.MISSING_FILES = []
        self.source_list_file = ""
        self.backout_list_file = ""

        self.version_filter = "[@version=" + '"' + self.tag_version + '"' + "]"
        self.root_tag = "/applicationUpdateProperties" + self.version_filter
        self.was_filter = "[@version<=" + '"' + self.max_was_version + '"' + "]"
        self.lib_filter = "[@version=" + '"' + self.lib_version + '"' + "]"
        self.generic_filter = "[@version=" + '"' + self.generic_version + '"' + "]"
        self.quasi_filter = "[@version=" + '"' + self.quasi_version + '"' + "]"

        try:
            MyXML.__init__(self, logger=self.logger, URI=self.xml_file)
        # print MyXML.getRootDocumentXML(self)
        except IOError as inst:
            print(("Unable to open " + str(self.xml_file) + " => " + str(inst.errno) + ":" + str(inst.strerror)));
            raise

    # Endif
    ##################################################################################
    # Enddef
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

        if (self.logger): self.logger.logIt(msg)

    ##################################################################################
    # Enddef
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

        if (self.logger): self.logger.debug(msg)

    ##################################################################################
    # Enddef
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
        pass

    ##################################################################################
    # Enddef
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
        self.closeMe()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	print_xml()
    #
    #	DESCRIPTION:
    #		Print the XML of the PUKE to stdout
    #
    #	PARAMETERS:
    #
    #	RETURN:
    ##################################################################################
    def print_xml(self):
        """Print the XML of the PUKE to stdout."""

        # print MyXML.getRootDocumentXML(self)
        print(self.getRootDocumentXML())

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	log_xml()
    #
    #	DESCRIPTION:
    #		Log the XML of the PUKE to the logger
    #
    #	PARAMETERS:
    #
    #	RETURN:
    ##################################################################################
    def log_xml(self):
        """Log the XML of the PUKE to the logger."""

        lFH = self.logger.getLogHandle();
        # xml_print( self.puke_dom, lFH )
        # lFH.write( MyXML.getRootDocumentXML(self) )
        lFH.write(self.getRootDocumentXML())

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	write_xml()
    #
    #	DESCRIPTION:
    #		Write the XML of the PUKE to the given file.
    #
    #	PARAMETERS:
    #		fileName
    #
    #	RETURN:
    ##################################################################################
    def write_xml(self, fileName):
        """Write the XML of the PUKE to the given file."""

        try:
            FH = open(fileName, "w")
            # xml_print( self.puke_dom, FH )

            FH.write(self.getRootDocumentXML())
            FH.close()
        except IOError as inst:
            self.logIt(
                "pylib.Amp.AppUpdateProperties.write_xml(): Unable to open " + fileName + " for write." + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
            raise

    # Endtry

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getAttributeValues()
    #
    #	DESCRIPTION:
    #		Get an array of all the given attribute values for the given name.
    #
    #	PARAMETERS:
    #		myElementsList - an array of pylib.XML.MyElement's.
    #		name           - name of the attribute desired.
    #
    #	RETURN:
    #		An array of the attribute values.
    ##################################################################################
    def getAttributeValues(self, myElementsList, name):
        """
        Get an array of all the given attribute values.
        PARAMETERS:
            myElementsList - an array of pylib.XML.MyElement's.
        	name           - name of the attribute(s) desired.
        RETURN:
            An array of the attribute values.
        """
        ar = []
        for el in myElementsList:
            myAttributes = el.getAllAttributes()
            for attr in myAttributes:
                if attr.getName() == name:
                    ar.append(attr.getValue())
        # Endif
        # Endfor
        # Endfor

        return self.utils.uniquer(ar)

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDaemonTableHostsNodeSet()
    #
    #	DESCRIPTION:
    #		Populate and return the nodeset of hosts in the
    #		/applicationUpdateProperties/runtimeHostDeploymentProperties/hostApplicationLists/hostApplicationList
    #		elements.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		An array of host names.
    ##################################################################################
    def getDaemonTableHostsNodeSet(self):
        """Return the /applicationUpdateProperties/runtimeHostDeploymentProperties/hostApplicationLists/hostApplicationList nodeset.
        RETURN:
            Nodeset.
        """

        xpath = self.root_tag + "/runtimeHostDeploymentProperties" + self.version_filter + "/hostApplicationLists/hostApplicationList"
        # hosts = self.puke_dom.xml_select( xpath )
        # self.debug( "pylib.Amp.AppUpdateProperties.getDaemonTableHostsNodeSet(): " + unicode( hosts ) )
        # results = self.getData( xpath )
        results = self.getData(xpath)
        hosts = self.getAttributeValues(results, "hostName")
        return hosts

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDaemonTableHostsArray()
    #
    #	DESCRIPTION:
    #		Populate the contents of the XML from the application update
    #		properties file from the daemon tables section to an array.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		Array hosts
    ##################################################################################
    def getDaemonTableHostsArray(self):
        """Return the /applicationUpdateProperties/runtimeHostDeploymentProperties/hostApplicationLists/hostApplicationList.
        RETURN:
            Array of hosts.
        """

        # hostArray = []
        # hostNodeSet = self.getDaemonTableHostsNodeSet()
        # for host in hostNodeSet:
        #	hostName = str( host.hostName )
        #	hostArray.append( hostName )
        # hostArray = self.utils.uniquer( hostArray )

        return self.getDaemonTableHostsNodeSet()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDaemonTableComponents()
    #
    #	DESCRIPTION:
    #		Return the /applicationUpdateProperties/runtimeHostDeploymentProperties/hostApplicationLists/hostApplicationList/hostApplications/hostApplication as a nodeset.
    #
    #	PARAMETERS:
    #		hostName - host name to filter the xpath on.
    #
    #	RETURN:
    #		An nodeset host application data.
    ##################################################################################
    def getDaemonTableComponents(self, hostName):
        """Return the /applicationUpdateProperties/runtimeHostDeploymentProperties/hostApplicationLists/hostApplicationList/hostApplications/hostApplication as a nodeset.
        PARAMETERS:
            hostName - host name to filter the xpath on.
        RETURN:
            A node_set of host application data.
        """

        myfilter = "[@hostName=" + '"' + hostName + '"' + "]"

        xpath = self.root_tag + "/runtimeHostDeploymentProperties" + self.version_filter + "/hostApplicationLists/hostApplicationList" + myfilter + "/hostApplications/hostApplication"

        self.debug("getDaemonTableComponents(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        # node_set = self.getData( xpath )
        node_set = self.getData(xpath)
        # print "DEBUG getDaemonTableComponents(): " + str( type( node_set ) )
        # print "DEBUG getDaemonTableComponents(): " + str( ( node_set ) )
        return node_set

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getHostApplicationComponentNames()
    #
    #	DESCRIPTION:
    #		Return the /applicationUpdateProperties/runtimeHostDeploymentProperties/hostApplicationLists/hostApplicationList/hostApplications/hostApplication as a nodeset.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		An array of the names.
    ##################################################################################
    def getHostApplicationComponentNames(self):
        """Return the /applicationUpdateProperties/runtimeHostDeploymentProperties/hostApplicationLists/hostApplicationList/hostApplications/hostApplication names.
        RETURN:
            An array of the component names.
        """

        names = []
        xpath = self.root_tag + "/runtimeHostDeploymentProperties" + self.version_filter + "/hostApplicationLists/hostApplicationList/hostApplications/hostApplication"

        # self.debug( "getHostAppliationComponentNames(): xpath=" + xpath )
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        for node in node_set:
            value = self.getAttribute(node, "componentName")
            names.append(str(value))
        # Endfor
        names = self.utils.uniquer(names)
        return names

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getComponentDomain()
    #
    #	DESCRIPTION:
    #		Return the /applicationUpdateProperties/componentDefinitions/websphere/deploymentProperties/cluster/domain element value
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value of the domain
    ##################################################################################
    def getComponentDomain(self, name):
        """/applicationUpdateProperties/componentDefinitions/websphere/deploymentProperties/cluster/domain element value
        PARAMETERS:
            name - name to filter the xpath on.
        RETURN:
            value of the domain.
        """

        value = None
        nameFilter = "[@version <= " + '"' + self.max_was_version + '"' + " and @name=" + '"' + name + '"' + "]"
        templateVersion = "[@templateVersion <= " + '"' + self.max_was_version + '"' + "]"
        xpath = self.root_tag + "/componentDefinitions" + self.version_filter + "/websphere" + nameFilter + "/deploymentProperties" + templateVersion + "/cluster" + "/domain"

        # self.debug( "getComponentDomain(): xpath=" + xpath )
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        for node in node_set:
            # value = str( node.domain )
            value = node.getValue()
            return value
        # Endfor
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getComponentDefinitionApplicationNames()
    #
    #	DESCRIPTION:
    #		Return the /applicationUpdateProperties/componentDefinitions/websphere
    #
    #	PARAMETERS:
    #		componentName - component name to filter the xpath on.
    #
    #	RETURN:
    #		An array of the names.
    ##################################################################################
    def getComponentDefinitionApplicationNames(self, componentName):
        """Return the /applicationUpdateProperties/componentDefinitions/websphere application attribute values.
        PARAMETERS:
            componentName - componentName to filter the xpath on.
        RETURN:
            An array of names.
        """

        names = []
        nameFilter = "[@name=" + '"' + componentName + '"' + " and @version <= " + '"' + self.max_was_version + '"' + "]"
        xpath = self.root_tag + "/componentDefinitions" + self.version_filter + "/websphere" + nameFilter

        # self.debug( "getComponentDefinitionApplicationNames(): xpath=" + xpath )
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        for node in node_set:
            value = self.getAttribute(node, "application")
            names.append(str(value))
        # Endfor
        names = self.utils.uniquer(names)
        return names

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getWASdata()
    #
    #	DESCRIPTION:
    #		Return the /applicationUpdateProperties/componentDefinitions/websphere
    #
    #	PARAMETERS:
    #		componentName	- component name to filter the xpath on.
    #		appName			- name of the application
    #
    #	RETURN:
    #		node_set of the was data
    ##################################################################################
    def getWASdata(self, componentName, appName):
        """Return the /applicationUpdateProperties/componentDefinitions/websphere application attribute values.
        RETURN:
            node_set of the was data.
        """

        nameFilter = "[@name=" + '"' + componentName + '"' + " and @version <= " + '"' + self.max_was_version + '"' + " and @application=" + '"' + appName + '"' + "]"
        xpath = self.root_tag + "/componentDefinitions" + self.version_filter + "/websphere" + nameFilter

        # self.debug( "getWASdata(): xpath=" + xpath )
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        return node_set

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getWASDeploymentProperties()
    #
    #	DESCRIPTION:
    #		Return the /applicationUpdateProperties/componentDefinitions/websphere/deploymentProperties
    #
    #	PARAMETERS:
    #		componentName	- component name to filter the xpath on.
    #		appName			- name of the application
    #
    #	RETURN:
    #		node of the xpath node_set that matches.
    ##################################################################################
    def getWASDeploymentProperties(self, componentName, appName):
        """Return the /applicationUpdateProperties/componentDefinitions/websphere application attribute values.
        PARAMETERS:
            componentName - component name to filter the xpath on.
            appName       - name of the attribute.
        RETURN:
            node of the xpath node_set that matches.
        """

        nameFilter = "[@name=" + '"' + componentName + '"' + " and @version <= " + '"' + self.max_was_version + '"' + " and @application=" + '"' + appName + '"' + "]"
        templateVersion = "[@templateVersion <= " + '"' + self.max_was_version + '"' + "]"
        xpath = self.root_tag + "/componentDefinitions" + self.version_filter + "/websphere" + nameFilter + "/deploymentProperties" + templateVersion

        self.debug("getWASDeploymentProperties(): xpath=" + xpath)
        # node_set = self.puke_dom.xml_select( xpath )
        # node_set = self.getData( xpath )
        # for node in node_set: return node
        # return self.xpathQuery( xpath )
        nodes = self.xpathQuery(xpath)
        return nodes

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getAttributeOld()
    #
    #	DESCRIPTION:
    #		Get the value of the given attribute name from the given node.
    #
    #	PARAMETERS:
    #		node			- a node from a node_set retrieved from an xpath.
    #		attributeName	- name of the attribute.
    #
    #	RETURN:
    #		The value of the name attribute
    ##################################################################################
    def getAttributeOld(self, node, attributeName):
        """Return the attribute value of the given attribute name.
        PARAMETERS:
            node          - a node from a node_set retrieved from an xpath.
            attributeName - name of the attribute.
        RETURN:
            The value of the name attribute
        """

        rValue = ""
        myAttrs = list(node.xml_attributes.items())
        for item in myAttrs:
            if (item[0][0] is None):
                mykey = item[0][1]
                myvalue = item[1]
                if (mykey == attributeName):
                    rValue = myvalue
        return rValue

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getAttribute()
    #
    #	DESCRIPTION:
    #		Get the value of the given attribute name from the given node.
    #
    #	PARAMETERS:
    #		node			- a node from a node_set retrieved from an xpath.
    #		attributeName	- name of the attribute.
    #
    #	RETURN:
    #		The value of the name attribute
    ##################################################################################
    def getAttribute(self, node, attributeName):
        """Return the attribute value of the given attribute name.
        PARAMETERS:
            node          - a node from a node_set retrieved from an xpath.
            attributeName - name of the attribute.
        RETURN:
            The value of the name attribute
        """

        rValue = ""
        # print "attributeName=" + str( attributeName )
        for attr in node.getAllAttributes():
            if attr.getName() == attributeName:
                rValue = attr.getValue()
                # print "rValue=" + '"' + str( rValue ) + '"'
                return rValue
        return rValue

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getComponentDefinitionStatusByName()
    #
    #	DESCRIPTION:
    #		Get the status of DEPLOY or KEEP based on the existence of the attribute
    #		'name' in the /applicationUpdateProperties/applicationsToUpdate/AppComponent.
    #
    #	PARAMETERS:
    #		node			- a node from a node_set retrieved from an xpath.
    #		attributeName	- name of the attribute.
    #
    #	RETURN:
    #		The value of the name attribute
    ##################################################################################
    def getComponentDefinitionStatusByName(self, name):
        """Get the status of DEPLOY or KEEP based on the existence of the attribute 'name' in the /applicationUpdateProperties/applicationsToUpdate/AppComponent.
        PARAMETERS:
            name      - the name to filter the xpath on.
        RETURN:
            The value of the deploy status.
        """

        filter = "[@name=" + '"' + name + '"' + "]"
        rValue = ""
        xpath = self.root_tag + "/applicationsToUpdate/AppComponent" + filter
        # self.debug( "getComponentDefinitionStatusByName(): xpath=" + xpath + "\n" )
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        if (node_set is None): return "KEEP"
        if (node_set is not None): return "DEPLOY"
        return rValue

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getOtherHosts()
    #
    #	DESCRIPTION:
    #		Get the non-runtime hosts.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		Array of hosts
    ##################################################################################
    def getOtherHosts(self):
        """Get the non-runtime hosts.
        PARAMETERS:
            NONE
        RETURN:
            Array of hosts.
        """

        myArr = []
        xpath = self.root_tag + "/mnemonicFileDeploymentProperties" + self.version_filter + "/otherHosts/host"
        self.debug("getOtherHosts(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        for node in node_set:
            # host = self.getAttribute( node, "name" )
            myAttr = node.getAttributeByName("name")
            # myArr.append( host.lower() )
            myArr.append(myAttr.getValue().lower())
        return myArr

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getRuntimeHosts()
    #
    #	DESCRIPTION:
    #		Get the runtime hosts
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		Array of hosts
    ##################################################################################
    def getRuntimeHosts(self):
        """Get the runtime hosts.
        PARAMETERS:
            NONE
        RETURN:
            Array of hosts.
        """

        myArr = []
        xpath = self.root_tag + "/mnemonicFileDeploymentProperties" + self.version_filter + "/runtimeHosts/host"
        self.debug("getOtherHosts(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        for node in node_set:
            # host = self.getAttribute( node, "name" )
            myAttr = node.getAttributeByName("name")
            myArr.append(myAttr.getValue().lower())
        return myArr

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getAllHosts()
    #
    #	DESCRIPTION:
    #		Get the all hosts
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		Array of hosts
    ##################################################################################
    def getAllHosts(self):
        """Get the all hosts.
        PARAMETERS:
            NONE
        RETURN:
            Array of hosts.
        """

        rAR = []
        rth = self.getRuntimeHosts()
        oth = self.getOtherHosts()
        for host in rth: rAR.append(host)
        for host in oth: rAR.append(host)
        rAR = self.utils.uniquer(rAR)
        return rAR

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getFilePermissions()
    #
    #	DESCRIPTION:
    #		Get the node_set of files from the
    #		../mnemonicFileDeploymentProperties/fileDeploymentProperties/file/permissionsText
    #		value.
    #
    #	PARAMETERS:
    #		fileName
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getFilePermissions(self, fileName):
        """Get the array of files from the ../mnemonicFileDeploymentProperties/fileDeploymentProperties/file/permissionsText value.
        PARAMETERS:
            fileName - name of the file to filter on.
        RETURN:
            The permissions, something like "0777".
        """
        filter = "[@name=" + '"' + fileName + '"' + "]"
        xpath = self.root_tag + "/mnemonicFileDeploymentProperties" + self.version_filter + "/fileDeploymentProperties/file" + filter + "/permissionsText"
        self.debug("getFilePermisions(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.permissionsText )
            value = node.getValue()
        # Endfor
        # print "value=" + '"' + str( value ) + '"'
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getTargetPath()
    #
    #	DESCRIPTION:
    #		Get the
    #		../mnemonicFileDeploymentProperties/fileDeploymentProperties/file/targetPath
    #		value.
    #
    #	PARAMETERS:
    #		fileName
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getTargetPath(self, fileName):
        """Get the ../mnemonicFileDeploymentProperties/fileDeploymentProperties/file/targetPath value.
        PARAMETERS:
            fileName - name of the file to filter on.
        RETURN:
            The value.
        """
        filter = "[@name=" + '"' + fileName + '"' + "]"
        xpath = self.root_tag + "/mnemonicFileDeploymentProperties" + self.version_filter + "/fileDeploymentProperties/file" + filter + "/targetPath"
        self.debug("getTargetPath(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.targetPath )
            value = node.getValue()
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getSourcePath()
    #
    #	DESCRIPTION:
    #		Get the
    #		../mnemonicFileDeploymentProperties/fileDeploymentProperties/file/sourcePath
    #		value.
    #
    #	PARAMETERS:
    #		fileName
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getSourcePath(self, fileName):
        """Get the ../mnemonicFileDeploymentProperties/fileDeploymentProperties/file/sourcePath value.
        PARAMETERS:
            fileName - name of the file to filter on.
        RETURN:
            The value.
        """
        filter = "[@name=" + '"' + fileName + '"' + "]"
        xpath = self.root_tag + "/mnemonicFileDeploymentProperties" + self.version_filter + "/fileDeploymentProperties/file" + filter + "/sourcePath"
        self.debug("getSourcePath(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.sourcePath )
            value = node.getValue()
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getTargetBase()
    #
    #	DESCRIPTION:
    #		Get the
    #		../mnemonicFileDeploymentProperties/fileDeploymentProperties/file/targetBase
    #		value.
    #
    #	PARAMETERS:
    #		fileName
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getTargetBase(self, fileName):
        """Get the array of files from the ../mnemonicFileDeploymentProperties/fileDeploymentProperties/file/targetBase value.
        PARAMETERS:
            fileName - name of the file to filter on.
        RETURN:
            The value.
        """
        filter = "[@name=" + '"' + fileName + '"' + "]"
        xpath = self.root_tag + "/mnemonicFileDeploymentProperties" + self.version_filter + "/fileDeploymentProperties/file" + filter + "/targetBase"
        self.debug("getTargetBase(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.targetBase )
            value = node.getValue()
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDeployableComponentDefinitionTypeByName()
    #
    #	DESCRIPTION:
    #		Get the typeCode attribute value of the
    #		../applicationComponentConfigurations/applicationConfigurations/domainApplicationComponentConfiguration
    #		element.
    #
    #	PARAMETERS:
    #		componentName
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getDeployableComponentDefinitionTypeByName(self, componentName):
        """Get the typeCode attribute value of the ../applicationComponentConfigurations/applicationConfigurations/domainApplicationComponentConfiguration element.
        PARAMETERS:
            componentName - componentName to filter on.
        RETURN:
            The value.
        """
        filter = "[@appComponentName=" + '"' + componentName + '"' + "]"
        xpath = self.root_tag + "/applicationComponentConfigurations" + self.version_filter + "/applicationConfigurations/domainApplicationComponentConfiguration" + filter
        self.debug("getDeployableComponentDefinitionTypeByName(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            value = self.getAttribute(node, "typeCode")
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDeployableComponentDefinitionNames()
    #
    #	DESCRIPTION:
    #		Get all the deployable componentDefinition names for
    #		../applicationsToUpdate/AppComponent
    #		element.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		Array of component names
    ##################################################################################
    def getDeployableComponentDefinitionNames(self):
        """Get all the deployable componentDefinition names for ../applicationsToUpdate/AppComponent elements.
        PARAMETERS:
            NONE
        RETURN:
            The array of component names.
        """

        ar = []
        xpath = self.root_tag + "/applicationsToUpdate/AppComponent"
        self.debug("getDeployableComponentDefinitionNames(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        for node in node_set:
            value = self.getAttribute(node, "name")
            ar.append(value)
        # Endfor
        ar = self.utils.uniquer(ar)
        return ar

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getSourceBase()
    #
    #	DESCRIPTION:
    #		Get the node_set of files from the
    #		../mnemonicFileDeploymentProperties/sourceBase
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getSourceBase(self):
        """Get the ../mnemonicFileDeploymentProperties/sourceBase value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/mnemonicFileDeploymentProperties" + self.version_filter + "/sourceBase"
        self.debug("getSourceBase(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.sourceBase )
            value = node.getValue()
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getHostApplicationComponentTypesByType()
    #
    #	DESCRIPTION:
    #		Get the node_set of files from the
    #		../runtimeHostDeploymentProperties/hostApplicationLists/hostApplicationList/hostApplications/hostApplication
    #		value.
    #
    #	PARAMETERS:
    #		componentType
    #
    #	RETURN:
    #		array of types
    ##################################################################################
    def getHostApplicationComponentTypesByType(self, componentType):
        """Get the array of files from the ../runtimeHostDeploymentProperties/hostApplicationLists/hostApplicationList/hostApplications/hostApplication value.
        PARAMETERS:
            componentType - componentType to filter the xpath on.
        RETURN:
            The array of types.
        """
        filter = "[@componentType=" + '"' + componentType + '"' + "]"
        xpath = self.root_tag + "/runtimeHostDeploymentProperties" + self.version_filter + "/hostApplicationLists/hostApplicationList/hostApplications"
        self.debug("getHostApplicationComponentTypesByType(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        ar = []
        for node in node_set:
            ar.append(str(self.getAttribute(node, "number")))
        ar = self.utils.uniquer(ar)
        return ar

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	isWas5Included()
    #
    #	DESCRIPTION:
    #		Determine if there are any was5 component types included.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		True or False
    ##################################################################################
    def isWas5Included(self):
        """Determine if there are any was5 component types included.
        PARAMETERS:
            NONE
        RETURN:
            True or False
        """
        ar = self.getHostApplicationComponentTypesByType("was5")
        if (len(ar) == 0): return False
        if (len(ar) > 0): return True

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	isPortalIncluded()
    #
    #	DESCRIPTION:
    #		Determine if there are any portal component types included.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		True or False
    ##################################################################################
    def isPortalIncluded(self):
        """Determine if there are any portal component types included.
        PARAMETERS:
            NONE
        RETURN:
            True or False
        """
        ar = self.getHostApplicationComponentTypesByType("portal")
        if (len(ar) == 0): return False
        if (len(ar) > 0): return True

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getHostsByTypeAndSubType()
    #
    #	DESCRIPTION:
    #		Get the hosts by componentType and componentSubType.
    #
    #	PARAMETERS:
    #		type
    #		subtype
    #
    #	RETURN:
    #		array of hosts.
    ##################################################################################
    def getHostsByTypeAndSubType(self, type, subtype):
        """Get the hosts by componentType and componentSubType.
        PARAMETERS:
            type    - componentType to filter on.
        	subtype - componentSubType to filter on.
        RETURN:
            Array of hosts.
        """
        daemons = self.getDaemonTableArray()
        ar = []
        for row in daemons:
            # print "type=" + type
            # print "subtype=" + subtype
            # print "row0=" + row[0]
            # print "row2=" + row[2]
            # print "row3=" + row[3]
            reMatch = re.match(type, str(row[2]))
            # print "group0=" + reMatch.group(0)
            if (reMatch and reMatch.group(0) == type and str(row[3]) == subtype): ar.append(str(row[0]))
        # Endfor
        ar = self.utils.uniquer(ar)
        return ar

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getEnv()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/environment
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getEnv(self):
        """Get the ../updateParameters/environment value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/environment"
        self.debug("getEnv(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.environment )
            value = node.getValue()
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getMNE()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/mne
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getMNE(self):
        """Get the ../updateParameters/mne value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/mne"
        self.debug("getMNE(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.mne )
            value = node.getValue()
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getAmpId()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/ampId
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getAmpId(self):
        """Get the ../updateParameters/ampId value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/ampId"
        self.debug("getAmpId(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.ampId )
            value = node.getValue()
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getPlatform()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/platform
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getPlatform(self):
        """Get the ../updateParameters/platform value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter
        self.debug("getPlatform(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            value = str(node.platform)
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getRestartsRequired()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/restartsRequired
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getRestartsRequired(self):
        """Get the ../updateParameters/restartsRequired value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/restartsRequired"
        self.debug("getRestartsRequired(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.restartsRequired )
            value = node.getValue()
        return value.lower()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDeveloperAcceptPostStage()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/developerAcceptPostStage
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getDeveloperAcceptPostStage(self):
        """Get the ../updateParameters/developerAcceptPostStage value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/developerAcceptPostStage"
        self.debug("getDeveloperAcceptPostStage(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.developerAcceptPostStage )
            value = node.getValue()
        return value.lower()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDeveloperAcceptPreRestart()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/developerAcceptPreRestart
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getDeveloperAcceptPreRestart(self):
        """Get the array of files from the ../updateParameters/developerAcceptPreRestart value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter
        self.debug("getDeveloperAcceptPreRestart(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            value = str(node.developerAcceptPreRestart)
        return value.lower()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDeveloperAcceptPostRestart()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/developerAcceptPostRestart
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getDeveloperAcceptPostRestart(self):
        """Get the array of files from the ../updateParameters/developerAcceptPostRestart value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/developerAcceptPostRestart"
        self.debug("getDeveloperAcceptPostRestart(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.developerAcceptPostRestart )
            value = node.getValue()
        return value.lower()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getMissingSourceFiles()
    #
    #	DESCRIPTION:
    #		Get the list of missing source files.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		array of missing source files.
    ##################################################################################
    def getMissingSourceFiles(self):
        """Get the list of missing source files.
        PARAMETERS:
            NONE
        RETURN:
            The array of missing files.
        """
        return self.MISSING_FILES

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getWrittenFiles()
    #
    #	DESCRIPTION:
    #		Get the list of written files
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		array of written files.
    ##################################################################################
    def getWrittenFiles(self):
        """Get the list of written files.
        PARAMETERS:
            NONE
        RETURN:
            The array of written files.
        """
        return self.FILES

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getRunAfterJobName()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/runAfterJobName
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getRunAfterJobName(self):
        """Get the ../updateParameters/runAfterJobName value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/runAfterJobName"
        self.debug("getEnv(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.runAfterJobName )
            value = node.getValue()
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDeveloperEmail()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/developerEmail
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getDeveloperEmail(self):
        """Get the ../updateParameters/developerEmail value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/developerEmail"
        self.debug("getDeveloperEmail(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.developerEmail )
            value = node.getValue()
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getCCID()
    #
    #	DESCRIPTION:
    #		Get the node_set of files from the
    #		../updateParameters/ccid
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getCCID(self):
        """Get the value of the ../updateParameters/ccid value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/ccid"
        self.debug("getDeveloperEmail(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.ccid )
            value = node.getValue()
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getJobName()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/jobName
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getJobName(self):
        """Get the ../updateParameters/jobName value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/jobName"
        self.debug("getDeveloperEmail(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.jobName )
            value = node.getValue()
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDeploymentDate()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/deploymentDate
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getDeploymentDate(self):
        """Get the ../updateParameters/deploymentDate value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/deploymentDate"
        self.debug("getDeveloperEmail(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.deploymentDate )
            value = node.getValue()
        # Endfor

        #######################################
        #	We only want YYYY-MM-DD and
        #	convert it to YYYYMMDD.
        #######################################
        myMatch = re.match(r'^(\d{4})-(\d{2})-(\d{2})', str(value))
        if (myMatch is not None): value = str(myMatch.group(1) + str(myMatch.group(2)) + str(myMatch.group(3)))
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDeploymentTime()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/deploymentTime
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getDeploymentTime(self):
        """Get the ../updateParameters/deploymentTime value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/deploymentTime"
        self.debug("getDeploymentTime(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.deploymentTime )
            value = node.getValue()
        # Endfor

        return value.lower()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getMaintenancePathRequired()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/maintenancePathRequired
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getMaintenancePathRequired(self):
        """Get the ../updateParameters/maintenancePathRequired value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/maintenancePathRequired"
        self.debug("getMaintenancePathRequired(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.maintenancePathRequired )
            value = node.getValue()
        # Endfor
        if (value is None): value = "no"

        return value.lower()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getCleanInstall()
    #
    #	DESCRIPTION:
    #		Get the
    #		../updateParameters/cleanInstall
    #		value.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getCleanInstall(self):
        """Get the ../updateParameters/cleanInstall value.
        PARAMETERS:
            NONE
        RETURN:
            The value.
        """
        xpath = self.root_tag + "/updateParameters" + self.version_filter + "/cleanInstall"
        self.debug("getCleanInstall(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        value = ""
        for node in node_set:
            # value = str( node.cleanInstall )
            value = node.getValue()
        # Endfor
        if (value is None): value = "no"

        return value.lower()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getTOCFilesArray()
    #
    #	DESCRIPTION:
    #		Get the node_set of files from the
    #		../mnemonicFileDeploymentProperties/fileDeploymentProperties/file
    #		elements.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		node_set
    ##################################################################################
    def getTOCFilesArray(self):
        """Get the node_set of files from the ../mnemonicFileDeploymentProperties/fileDeploymentProperties/file elements.
        PARAMETERS:
            NONE
        RETURN:
            The node_set.
        """
        xpath = self.root_tag + "/mnemonicFileDeploymentProperties" + self.version_filter + "/fileDeploymentProperties/file"
        self.debug("getTOCFilesArray(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = []
        allElements = self.getData(xpath)
        for el in allElements:
            # el.logMe()
            if (el.getName() == "file"):
                node_set.append(el)
        return node_set

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getRestartTargetGroups()
    #
    #	DESCRIPTION:
    #		Get the an array of
    #		../restartParameters/groups/group 'number' attribute values.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		array of group numbers.
    ##################################################################################
    def getRestartTargetGroups(self):
        """Get the array of ../restartParameters/groups/group 'number' attribute values.
        PARAMETERS:
            NONE
        RETURN:
            The array of group numbers.
        """
        xpath = self.root_tag + "/restartParameters" + self.version_filter + "/groups/group"
        self.debug("getRestartTargetGroups(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        ar = []
        for node in node_set:
            ar.append(str(self.getAttribute(node, "number")))
        ar = self.utils.uniquer(ar)
        return ar

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getRestartHostsByGroup()
    #
    #	DESCRIPTION:
    #		Get the an array of
    #		../restartParameters/groups/group/targets/restartTarget 'host'
    #		attribute values for the given group number.
    #
    #	PARAMETERS:
    #		groupNumber
    #
    #	RETURN:
    #		array of hosts.
    ##################################################################################
    def getRestartHostsByGroup(self, groupNumber):
        """Get the array of ../restartParameters/groups/group/targets/restartTarget 'host' attribute values.
        PARAMETERS:
            groupNumber - group number to filter on.
        RETURN:
            The array of hosts.
        """
        filter = "[@number = " + '"' + groupNumber + '"' + "]"
        xpath = self.root_tag + "/restartParameters" + self.version_filter + "/groups/group" + filter + "/targets/restartTarget"
        self.debug("getRestartHostsByGroup(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        ar = []
        for node in node_set:
            ar.append(str(self.getAttribute(node, "host")))
        # Endfor
        ar = self.utils.uniquer(ar)
        return ar

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getRestartDomainsByGroupAndHost()
    #
    #	DESCRIPTION:
    #		Get the an array of
    #		../restartParameters/groups/group/targets/restartTarget 'domain'
    #		attribute values for the given group number and host name.
    #
    #	PARAMETERS:
    #		groupNumber
    #		host
    #
    #	RETURN:
    #		array of domains.
    ##################################################################################
    def getRestartDomainsByGroupAndHost(self, groupNumber, host):
        """Get the array of ../restartParameters/groups/group/targets/restartTarget 'domain' attribute values.
        PARAMETERS:
            groupNumber - group number to filter on.
            host        - host to filter on.
        RETURN:
            The array of domains.
        """
        gfilter = "[@number = " + '"' + groupNumber + '"' + "]"
        hfilter = "[@host = " + '"' + host + '"' + "]"
        xpath = self.root_tag + "/restartParameters" + self.version_filter + "/groups/group" + gfilter + "/targets/restartTarget" + hfilter
        self.debug("getRestartDomainsByGroupAndHost(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        ar = []
        for node in node_set:
            ar.append(str(self.getAttribute(node, "domain")))
        ar = self.utils.uniquer(ar)
        return ar

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getRestartMnemonicsByGroupAndHostAndDomain()
    #
    #	DESCRIPTION:
    #		Get the an array of
    #		../restartParameters/groups/group/targets/restartTarget 'mnemonic'
    #		attribute values for the given group number,host name, and domain.
    #
    #	PARAMETERS:
    #		groupNumber
    #		host
    #		domain
    #
    #	RETURN:
    #		array of mnemonics.
    ##################################################################################
    def getRestartMnemonicsByGroupAndHostAndDomain(self, groupNumber, host, domain):
        """Get the array of ../restartParameters/groups/group/targets/restartTarget 'mnemonic' attribute values.
        PARAMETERS:
            groupNumber - group number to filter on.
            host        - host to filter on.
            domain      - domain to filter on.
        RETURN:
            The array of mnemonics.
        """
        gfilter = "[@number = " + '"' + groupNumber + '"' + "]"
        filter = "[@host = " + '"' + host + '"' + " and @domain=" + '"' + domain + '"' + "]"
        xpath = self.root_tag + "/restartParameters" + self.version_filter + "/groups/group" + gfilter + "/targets/restartTarget" + filter
        self.debug("getRestartMnemonicsByGroupAndHostAndDomain(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        ar = []
        for node in node_set:
            ar.append(str(self.getAttribute(node, "mnemonic")))
        # Endfor
        ar = self.utils.uniquer(ar)
        return ar

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getRestartTypesByGroupAndHostAndDomainAndMne()
    #
    #	DESCRIPTION:
    #		Get the an array of
    #		../restartParameters/groups/group/targets/restartTarget 'type'
    #		attribute values for the given group number,host name, domain, and mnemonic.
    #
    #	PARAMETERS:
    #		groupNumber
    #		host
    #		domain
    #		mnemonic
    #
    #	RETURN:
    #		array of types.
    ##################################################################################
    def getRestartTypesByGroupAndHostAndDomainAndMne(self, groupNumber, host, domain, mnemonic):
        """Get the array of ../restartParameters/groups/group/targets/restartTarget 'type' attribute values.
        PARAMETERS:
            groupNumber - group number to filter on.
            host        - host to filter on.
            domain      - domain to filter on.
            mnemonic    - mnemonic to filter on.
        RETURN:
            The array of types.
        """
        gfilter = "[@number = " + '"' + groupNumber + '"' + "]"
        filter = "[@host = " + '"' + host + '"' + " and @domain=" + '"' + domain + '"' + " and @mnemonic=" + '"' + mnemonic + '"' + "]"
        xpath = self.root_tag + "/restartParameters" + self.version_filter + "/groups/group" + gfilter + "/targets/restartTarget" + filter
        self.debug("getRestartMnemonicsByGroupAndHostAndDomain(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        ar = []
        for node in node_set:
            ar.append(str(self.getAttribute(node, "type")))
        # Endfor
        ar = self.utils.uniquer(ar)
        return ar

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getRestartTargetsByGroupAndHostAndDomainAndMneAndType()
    #
    #	DESCRIPTION:
    #		Get the an array of
    #		../restartParameters/groups/group/targets/restartTarget 'type'
    #		attribute values for the given group number,host name, domain, mnemonic, and type.
    #
    #	PARAMETERS:
    #		groupNumber
    #		host
    #		domain
    #		mnemonic
    #
    #	RETURN:
    #		array of names.
    ##################################################################################
    def getRestartTargetsByGroupAndHostAndDomainAndMneAndType(self, groupNumber, host, domain, mnemonic, type):
        """Get the array of ../restartParameters/groups/group/targets/restartTarget 'name' attribute values.
        PARAMETERS:
            groupNumber - group number to filter on.
            host        - host to filter on.
            domain      - domain to filter on.
            mnemonic    - mnemonic to filter on.
            type        - type to filter on.
        RETURN:
            The array of names.
        """
        gfilter = "[@number = " + '"' + groupNumber + '"' + "]"
        filter = "[@host = " + '"' + host + '"' + " and @domain=" + '"' + domain + '"' + " and @mnemonic=" + '"' + mnemonic + '"' + " and @type=" + '"' + type + '"' + "]"
        xpath = self.root_tag + "/restartParameters" + self.version_filter + "/groups/group" + gfilter + "/targets/restartTarget" + filter
        self.debug("getRestartTargetsByGroupAndHostAndDomainAndMneAndType(): xpath=" + xpath + "\n")
        # node_set = self.puke_dom.xml_select( xpath )
        node_set = self.getData(xpath)
        ar = []
        for node in node_set:
            ar.append(str(self.getAttribute(node, "name")))
        # Endfor
        ar = self.utils.uniquer(ar)
        return ar

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getRestartTargetRecords()
    #
    #	DESCRIPTION:
    #		Get the restarts targets data array.
    #		elements.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		array of targets {group}->{host}->{domain}->{mnemonic}->{type}->{target}
    ##################################################################################
    def getRestartTargetRecords(self):
        """Get the restart targets dict/hash array.
        PARAMETERS:
            NONE
        RETURN:
            The array of targets {group}->{host}->{domain}->{mnemonic}->{type}->{target}
        """
        records = []
        groups = self.getRestartTargetGroups()
        i = 0

        self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetRecords(): GROUPS: " + str(groups) + "\n")
        if (len(groups) < 1):
            self.logIt("pylib.Amp.AppUpdateProperties.getRestartTargetRecords(): No groups were found in the PUKE.\n")
            return None
        # Endif
        for group in groups:
            hosts = self.getRestartHostsByGroup(group)
            self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetRecords(): hosts: " + str(hosts) + "\n")
            for host in hosts:
                domains = self.getRestartDomainsByGroupAndHost(group, host)
                self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetRecords(): domains: " + str(domains) + "\n")
                for domain in domains:
                    mnemonics = self.getRestartMnemonicsByGroupAndHostAndDomain(group, host, domain)
                    self.debug(
                        "pylib.Amp.AppUpdateProperties.getRestartTargetRecords(): mnemonics: " + str(mnemonics) + "\n")
                    for mnemonic in mnemonics:
                        types = self.getRestartTypesByGroupAndHostAndDomainAndMne(group, host, domain, mnemonic)
                        self.debug(
                            "pylib.Amp.AppUpdateProperties.getRestartTargetRecords(): types: " + str(types) + "\n")
                        for type in types:
                            targets = self.getRestartTargetsByGroupAndHostAndDomainAndMneAndType(group, host, domain,
                                                                                                 mnemonic, type)
                            self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetRecords(): targets: " + str(
                                targets) + "\n")
                            found = False
                            for target in targets:
                                found = True
                                records.append([group, host, domain, mnemonic, type, target])
                            # Endfor
                            if (not found): records.append([group, host, domain, mnemonic, type, "UNDEFINED"])
                # Endfor
            # Endfor
        # Endfor
        # Endfor
        # EndFor
        self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetRecords(): TARGETS records: " + str(records) + "\n")
        return records

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getRestartTargetsArray()
    #
    #	DESCRIPTION:
    #		Get the restarts targets data array
    #		elements.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		Array of rows of targets.
    #		Each row is:
    #			group,
    #			host,
    #			domain,
    #			mnemonic,
    #			type,
    #			target
    ##################################################################################
    def getRestartTargetsArray(self):
        """Get the restart targets data array.
        PARAMETERS:
            NONE
        RETURN:
            The array of targets.
            Each row is:
                group,
                host,
                domain,
                mnemonic,
                type,
                target
        """
        data = []
        rc = True
        records = self.getRestartTargetRecords()

        self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetsArray(): TARGETS records: " + str(records) + "\n")
        for record in records:
            self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetsArray(): record: " + str(record) + "\n")
            row = []
            group = record[0]
            host = record[1]
            domain = record[2]
            mnemonic = record[3]
            type = record[4]
            target = record[5]
            self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetsArray(): group: " + str(group) + "\n")
            self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetsArray(): host: " + str(host) + "\n")
            self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetsArray(): domain: " + str(domain) + "\n")
            self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetsArray(): mnemonic: " + str(mnemonic) + "\n")
            self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetsArray(): type: " + str(type) + "\n")
            self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetsArray(): target: " + str(target) + "\n")
            if (target is None): target = "UNDEFINED"
            domain = str(re.sub(r'\s+', r'-', str(domain)))
            domain = domain.upper()
            type = str(re.sub(r'\s+', r'', str(type)))
            type = type.lower()
            row.append(group)
            row.append(host)
            row.append(domain)
            row.append(mnemonic)
            row.append(type)
            row.append(target)
            self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetsArray(): row: " + str(row) + "\n")
            data.append(row)
        # Endfor
        self.debug("pylib.Amp.AppUpdateProperties.getRestartTargetsArray(): TARGETS data: " + str(data) + "\n")
        return data

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getTOCArray()
    #
    #	DESCRIPTION:
    #		Return an array of arrays of
    #			[[
    #				fileName,
    #				sourceBase,
    #				sourcePath,
    #				targetBase,
    #				targetPath,
    #				status,
    #				user,
    #				group,
    #				perms
    #			]]
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		Array of arrays
    ##################################################################################
    def getTOCArray(self):
        """Return and array of arrays of file data.
        PARAMETERS:
            NONE
        RETURN:
            The array of targets.
            Each row is:
                fileName,
                sourceBase,
                sourcePath,
                targetBase,
                targetPath,
                status,
                user,
                group,
                perms
        """
        ar = []

        #######################################
        #	Populate the table.
        #######################################
        fileElements = self.getTOCFilesArray()
        # print fileElements
        for fileElement in fileElements:
            # print fileElement
            # fileElement.logMe()
            # fileElement.printMe()
            row = []
            fileName = self.getAttribute(fileElement, "name")
            # print "fileName=" + '"' + str( fileName ) + '"'
            status = self.getAttribute(fileElement, "status")
            # print "status=" + '"' + str( status ) + '"'
            user = self.getAttribute(fileElement, "owner")
            # print "user=" + '"' + str( user ) + '"'
            group = self.getAttribute(fileElement, "group")
            # print "group=" + '"' + str( group ) + '"'
            perms = self.getFilePermissions(fileName)
            # print "perms=" + '"' + str( perms ) + '"'
            targetBase = self.getTargetBase(fileName)
            # print "targetBase=" + '"' + str( targetBase ) + '"'
            targetPath = self.getTargetPath(fileName)
            # print "targetPath=" + '"' + str( targetPath ) + '"'
            sourceBase = self.getSourceBase()
            # print "sourceBase=" + '"' + str( sourceBase ) + '"'
            sourcePath = self.getSourcePath(fileName)
            # print "sourcePath=" + '"' + str( sourcePath ) + '"'
            row.append(fileName)
            row.append(sourceBase)
            row.append(sourcePath)
            row.append(targetBase)
            row.append(targetPath)
            row.append(status)
            row.append(user)
            row.append(group)
            row.append(perms)
            ar.append(row)
        return ar

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeMasterTOC()
    #
    #	DESCRIPTION:
    #		Write the Master TOC table from the PUKE file.
    #
    #	PARAMETERS:
    #		ouputDir	- output directory.
    #		tocFile		- output file name.
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeMasterTOC(self, outputDir="/tmp", tocFile="master_file_list.dat"):
        """Write the Master TOC table from the PUKE file.
        PARAMETERS:
            outputDir  - output directory.
            tocFile    - name of the resulting master TOC file.
        RETURN:
            True for success or False
        """
        rc = True
        backoutInd = False
        FH = None
        myFile = outputDir + "/" + tocFile
        flag = False
        env = self.getEnv()
        hashString = "#####################################################################################################################################################"
        header = "%-35s %-80s %-40s %-20s %-20s %-8s %-8s %-10s %-4s\n" % (
            "#Filename", "SourceBase", "SourcePath", "TargetBase", "TargetPath", "Action", "Owner", "GroupOwner",
            "Perms")
        header2 = "%-35.35s %-80.80s %-40.40s %-20.20s %-20.20s %-8.8s %-8.8s %-10.10s %-4.4s\n" % (
            hashString, hashString, hashString, hashString, hashString, hashString, hashString, hashString, hashString)
        header = header + header2

        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.UpdateProperties.writeMasterTOC(): Failed to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # EndTry

        self.logIt("pylib.Amp.UpdateProperties.writeMasterTOC(): Writing " + myFile + "\n")
        self.FILES.append(myFile)

        FH.write(header)

        ar = self.getTOCArray()

        for row in ar:
            fileName = row[0]
            sourceBase = row[1]
            sourcePath = row[2]
            targetBase = row[3]
            targetPath = row[4]
            status = row[5]
            user = row[6]
            group = row[7]
            perms = row[8]
            if (fileName is None):        fileName = "UNDEFINED"
            if (sourceBase is None):    sourceBase = "UNDEFINED"
            if (sourcePath is None):    sourcePath = "UNDEFINED"
            if (targetBase is None):    targetBase = "UNDEFINED"
            if (targetPath is None):    targetPath = "UNDEFINED"
            if (status is None):        status = "UNDEFINED"
            if (user is None):            user = "UNDEFINED"
            if (group is None):        group = "UNDEFINED"
            if (perms is None):        perms = "UNDEFINED"

            wString = "%-35s %-80s %-40s %-20s %-20s %-8s %-8s %-10s %-4s\n" % (
                fileName, sourceBase, sourcePath, targetBase, targetPath, status, user, group, perms)
            FH.write(wString)
            flag = True

            if (not re.match(r'\d{4,4}$', str(perms).strip())):
                rc = False
                self.logIt("pylib.Amp.UpdateProperties.writeMasterTOC(): Permissions " + str(
                    perms) + " are in the wrong format(0777) for " + fileName + "\n")
        # Endif
        # Endfor

        FH.close()

        if (not flag):
            self.logIt("pylib.Amp.UpdateProperties.writeMasterTOC(): " + myFile + " has no data.\n")
            rc = False
        # Endif
        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeTOC()
    #
    #	DESCRIPTION:
    #		Write the TOC table from the PUKE file.
    #
    #	PARAMETERS:
    #		ouputDir	- output directory.
    #		tocFile		- output file name.
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeTOC(self, outputDir="/tmp", tocFile="master_file_list.dat"):
        """Write the TOC table from the PUKE file.
        PARAMETERS:
            outputDir  - output directory.
            tocFile    - name of the resulting master TOC file.
        RETURN:
            True for success or False
        """
        rc = True
        backoutInd = False
        FH = None
        myFile = outputDir + "/" + "filelist.dat"
        backoutFile = outputDir + "/" + "backout_filelist.dat"
        flag = False
        env = self.getEnv()
        hashString = "#####################################################################################################################################################"
        header = "%-100s\n" % ("#RelativeSourceBase/SourcePath/FileName")
        header2 = "%-100.100s\n" % (hashString)
        header = header + header2

        self.source_list_file = myFile
        self.backout_list_file = backoutFile

        rc = self.writeMasterTOC(outputDir, tocFile)

        if (rc):
            try:
                FH = open(myFile, "w")
            except IOError as inst:
                self.logIt("pylib.Amp.UpdateProperties.writeTOC(): Failed to open " + myFile + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
                return False
            # EndTry

            self.FILES.append(myFile)

            FH.write(header)
            ar = self.getTOCArray()

            for row in ar:
                fileName = row[0]
                sourceBase = row[1]
                sourcePath = row[2]
                targetBase = row[3]
                targetPath = row[4]
                status = row[5]
                user = row[6]
                group = row[7]
                perms = row[8]
                if (fileName is None):        fileName = "UNDEFINED"
                if (sourceBase is None):    sourceBase = "UNDEFINED"
                if (sourcePath is None):    sourcePath = "UNDEFINED"
                if (targetBase is None):    targetBase = "UNDEFINED"
                if (targetPath is None):    targetPath = "UNDEFINED"
                if (status is None):        status = "UNDEFINED"
                if (user is None):            user = "UNDEFINED"
                if (group is None):        group = "UNDEFINED"
                if (perms is None):        perms = "0000"

                ######################################################
                #	Strip the first token from the source base to
                #	make it relative for the deployment tasks.
                ######################################################
                realBase = sourceBase
                if (env != "DEV"): sourceBase = str(re.sub(r'^/safe/', r'', str(sourceBase), 1))
                if (env == "DEV"): sourceBase = str(re.sub(r'^/nfs/', r'', str(sourceBase), 1))

                #####################################################
                #	Write the TOC data.
                #####################################################
                if (status == "DEPLOY"):
                    safeFile = str(realBase) + "/" + str(sourcePath) + "/" + str(fileName)
                    if (not os.access(str(safeFile), os.F_OK)): self.MISSING_FILES.append(str(safeFile))
                    if (not os.access(str(safeFile), os.F_OK)): rc = False
                    wString = "%s%-1s%-35s\n" % (str(sourcePath), "/", str(fileName))
                    FH.write(wString)
                    flag = True
            # Endif
            # Endfor
            FH.close()
            if (not flag):
                self.logIt("pylib.Amp.UpdateProperties.writeTOC(): Failed to open " + myFile + "\n")
                rc = False
        # Endif
        # Endif
        if (len(self.MISSING_FILES) > 0):
            self.logIt("pylib.Amp.UpdateProperties.writeTOC(): The following files are missing from the source tree:\n")
            rc = False
            for file in self.MISSING_FILES:
                self.logIt("pylib.Amp.UpdateProperties.writeTOC(): " + file + "\n")
        # Endfor
        # Endif
        self.logIt("pylib.Amp.UpdateProperties.writeTOC(): Returning " + str(rc) + "\n")
        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getDaemonTableArray()
    #
    #	DESCRIPTION:
    #		Return the /applicationUpdateProperties/runtimeHostDeploymentProperties/hostApplicationLists/hostApplicationList as an array of arrays.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		An array of arrays of
    #			host,
    #			component,
    #			daemon,
    #			subtype,
    #			count,
    #			domain,
    #			status,
    #			sysPlatform,
    #			appPlatform
    ##################################################################################
    def getDaemonTableArray(self):
        """
            RETURN:
            An array of arrays of
            host,
            component,
            daemon,
            subtype,
            count,
            domain,
            status,
            sysPlatform,
            appPlatform
        """
        rows = []
        hosts = self.getDaemonTableHostsArray()
        for hostName in hosts:
            componentElements = self.getDaemonTableComponents(hostName)
            # self.debug( "pylib.Amp.AppUpdateProperties.getDaemonTableArray(): " + str( componentElements ) + "\n" )
            # print "DEBUG getDaemonTableArray(): type of componentElements is " + str( type( componentElements ) )
            for componentElement in componentElements:
                row = []
                count = "1"
                # print "DEBUG getDaemonTableArray(): type of componentElement is " + str( type( componentElement ) )
                component = self.getAttribute(componentElement, "componentName")
                daemon = self.getAttribute(componentElement, "componentType")
                subtype = self.getAttribute(componentElement, "componentSubType")
                sysPlatform = self.getAttribute(componentElement, "systemPlatformType")
                appPlatform = self.getAttribute(componentElement, "applicationPlatformType")
                domain = self.getAttribute(componentElement, "domainName")
                daemon = daemon.lower()
                subtype = subtype.lower()
                status = self.getComponentDefinitionStatusByName(component)
                self.debug("pylib.Amp.AppUpdateProperties.getDaemonTableArray(): host=" + hostName + "\n")
                self.debug("pylib.Amp.AppUpdateProperties.getDaemonTableArray(): component=" + component + "\n")
                self.debug("pylib.Amp.AppUpdateProperties.getDaemonTableArray(): daemon=" + daemon + "\n")
                self.debug("pylib.Amp.AppUpdateProperties.getDaemonTableArray(): subtype=" + subtype + "\n")
                self.debug("pylib.Amp.AppUpdateProperties.getDaemonTableArray(): count=" + count + "\n")
                self.debug("pylib.Amp.AppUpdateProperties.getDaemonTableArray(): domain=" + domain + "\n")
                self.debug("pylib.Amp.AppUpdateProperties.getDaemonTableArray(): status=" + status + "\n")
                self.debug("pylib.Amp.AppUpdateProperties.getDaemonTableArray(): sysPlatform=" + sysPlatform + "\n")
                self.debug("pylib.Amp.AppUpdateProperties.getDaemonTableArray(): appPlatform=" + appPlatform + "\n")
                row.append(hostName)
                row.append(component)
                row.append(daemon)
                row.append(subtype)
                row.append(count)
                row.append(domain)
                row.append(status)
                row.append(sysPlatform)
                row.append(appPlatform)
                rows.append(row)

        return rows

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	arrayDiff()
    #
    #	DESCRIPTION:
    #		Return the items in array2 that are not in array1
    #
    #	PARAMETERS:
    #		array1
    #		array2
    #
    #	RETURN:
    #		array of missing items.
    ##################################################################################
    def arrayDiff(self, array1, array2):
        """Return the items in array2 that are not in array1.
        PARAMETERS:
            array1  - array1
            array2  - array2
        RETURN:
            Array of missing items.
        """
        rArray = []
        for item2 in array2:
            found = False
            for item1 in array1:
                if (item1 == item2):
                    found = True
            # Endif
            # Endfor
            if (not found):
                rArray.append(item2)
        # Endfor
        # Endfor
        return rArray

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeNonRuntimeDaemonTableFiles()
    #
    #	DESCRIPTION:
    #		Write the non-runtime hosts data the respective daemon.<host> files,
    #		creating new ones if needed.
    #
    #	PARAMETERS:
    #		outputDir	- directory of resulting files.
    #		daemonTableHosts	- List of hosts for which files have already been created.
    #		arefData	- Array of Arrays of daemon table data.
    #		appendFlag	- True means to append the daemon.<host> file.
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeNonRuntimeDaemonTableFiles(self, daemonTableHosts, outputDir, appendFlag=True):
        """Write the non-runtime hosts the respective daemon.<host> files, creating new ones if needed.
        PARAMETERS:
            deamonTableHosts  - List of host for which files have already been created.
            outputDir         - directory of resulting files.
            appendFlag        - True means to append the daemon.<host> file.
        RETURN:
            True for success or False
        """

        #########################################
        #	Initialize some things that we need.
        #########################################
        hashString = "##########################################################################################################"
        header = "%-35s %-10s %-13s %-5s %-8s\n" % ("#ComponentName", "DaemonType", "DaemonSubType", "Count", "Domain")
        header2 = "%-35.35s %-10.10s %-13.13s %-5.5s %-8.8s\n" % (
            hashString, hashString, hashString, hashString, hashString)
        header = header + header2
        flag = False
        hosts = []
        rc = True
        FH = None
        myAppendFlag = appendFlag

        ################################################
        #	Get non-runtime hosts
        ################################################
        otherHosts = self.getOtherHosts()
        otherHosts = self.utils.uniquer(otherHosts)

        ###############################################
        #	Determine the hosts that are missing from
        #	the daemon table host list.
        ###############################################
        missingHosts = self.arrayDiff(daemonTableHosts, otherHosts)
        # print "missingHosts=" + str( missingHosts ) + "\n"
        # print "daemonTableHosts=" + str( daemonTableHosts ) + "\n"
        # print "otherHosts=" + str( otherHosts ) + "\n"

        #########################################################
        #	Get the complete list of hosts included non-runtime.
        #########################################################
        allHosts = daemonTableHosts
        for otherHost in otherHosts: allHosts.append(otherHost)

        allHosts = self.utils.uniquer(allHosts)
        # print "allHosts=" + str( allHosts ) + "\n"

        ########################################################
        #	Process the complete list of hosts.
        ########################################################
        for host in allHosts:
            myFile = outputDir + "/" + "daemons." + host
            try:
                #####################################################
                #	Check to see if the current host hasn't had a
                #	file created for it yet.
                #####################################################
                if (host in missingHosts):
                    ################################################
                    #	It hasn't so we want to create the file
                    #	and write the header.
                    ################################################
                    myAppendFlag = False
                    FH = open(myFile, "w")
                    self.FILES.append(myFile)
                else:
                    ###################################################
                    #	Append the file if that is what was requested,
                    #	otherwise create it.
                    ###################################################
                    if (myAppendFlag):
                        FH = open(myFile, "a")
                    else:
                        FH = open(myFile, "w")
                        self.FILES.append(myFile)
            # Endif
            # Endif
            except IOError as inst:
                self.logIt(
                    "pylib.Amp.UpdateProperties.writeNonRuntimeDaemonTableFiles(): Failed to open " + myFile + " => " + str(
                        inst.errno) + ":" + str(inst.strerror) + "\n")
                return False
            # EndTry

            ###################################
            #	Write the data
            ###################################
            try:
                flag = True
                self.logIt("pylib.Amp.UpdateProperties.writeNonRuntimeDaemonTableFiles(): Writing " + myFile + "\n")
                if (not myAppendFlag): FH.write(header)
                wString = "%-35.35s %-10.10s %-13.13s %-5.5s %-8.8s\n" % ("quasiapp", "shared", "shared", "0", "NULL")
                FH.write(wString)
                FH.close()
            except IOError as inst:
                self.logIt(
                    "pylib.Amp.UpdateProperties.writeNonRuntimeDaemonTableFiles(): Unable to write to " + myFile + " => " + str(
                        inst.errno) + ":" + str(inst.strerror) + "\n")
                return False
            # EndTry

            myAppendFlag = appendFlag
        # EndFor

        if (not flag):
            rc = False
            self.logIt("pylib.Amp.UpdateProperties.writeNonRuntimeDaemonTableFiles(): No non-runtime hosts found.\n")
        # EndIf

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	splitDaemonTable()
    #
    #	DESCRIPTION:
    #		Split the daemon table into the respective daemon.<host> files.
    #
    #	PARAMETERS:
    #		outputDir	- directory of resulting files.
    #		arefData	- Array of Arrays of daemon table data.
    #		appendFlag	- True means to append the daemon.<host> file.
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def splitDaemonTable(self, outputDir, arefData, appendFlag=False):
        """Split the daemon table into the respective daemon.<host> files.
        PARAMETERS:
            outputDir         - directory of resulting files.
            arefData          - array of arrays of daemon table data.
            appendFlag        - True means to append the daemon.<host> file.
        RETURN:
            True for success or False
        """
        #########################################
        #	Initialize some things that we need.
        #########################################
        hashString = "##########################################################################################################"
        header = "%-35s %-10s %-13s %-5s %-8s\n" % ("#ComponentName", "DaemonType", "DaemonSubType", "Count", "Domain")
        header2 = "%-35.35s %-10.10s %-13.13s %-5.5s %-8.8s\n" % (
            hashString, hashString, hashString, hashString, hashString)
        header = header + header2
        flag = False
        hosts = []
        rc = True

        ####################################################################
        #	Create a unique list of hosts from the given array of arrays
        #	to daemon table hosts.
        ####################################################################
        for myRow in arefData: hosts.append(myRow[0])
        hosts = self.utils.uniquer(hosts)

        ###################################################################
        #	For each unique host, create the daemons.<host> file and
        #	write matching contents of the arefData to the file.
        ###################################################################
        for host in hosts:
            DFH = None
            myFile = outputDir + "/" + "daemons." + host
            try:
                if (appendFlag):
                    DFH = open(myFile, "a")
                else:
                    DFH = open(myFile, "w")
            except IOError as inst:
                self.logIt("pylib.Amp.AppUpdateProperties.splitDaemonTable(): Unable to open " + myFile + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
                return False
            # Endtry

            ################################################
            #	Write the header to the file not appending.
            ################################################
            if (not appendFlag): DFH.write(header)

            ###################################################
            #	For each row in the arefData array, write the
            #	data to the file.
            ###################################################
            for myRow in arefData:
                ###############################################
                #	Check for the host match.
                ###############################################
                if (host == myRow[0]):
                    error = False
                    logErr = False

                    application = myRow[1]
                    appserver = myRow[2]
                    appservertype = myRow[3]
                    count = myRow[4]
                    domain = myRow[5]
                    if (
                            not re.match('^was', appserver)
                            and not re.match('^generic', appserver)
                            and not re.match('^shared', appserver)
                            and not re.match('^portal', appserver)
                    ):
                        error = True
                    if (error):
                        logErr = True
                        error = False
                        rc = False
                        self.logIt(
                            "pylib.Amp.UpdateProperties.splitDaemonTable(): Invalid appserver=" + appserver + "\n")
                    if (
                            re.match('^as', appservertype)
                            and re.match('^generic', appservertype)
                            and re.match('^ws', appservertype)
                            and re.match('^shared', appservertype)
                            and re.match('^dmgr', appservertype)
                            and re.match('^portal', appservertype)
                    ):
                        error = True
                    if (error):
                        logErr = True
                        error = False
                        rc = False
                        self.logIt(
                            "pylib.Amp.UpdateProperties.splitDaemonTable(): Invalid appservertype=" + appservertype + "\n")
                    if (not re.match('^[0-9]', count)):
                        error = True
                    if (error):
                        logErr = True
                        error = False
                        rc = False
                        self.logIt("pylib.Amp.UpdateProperties.splitDaemonTable(): Invalid count=" + count + "\n")
                    if (
                            not re.match('^V5_PROD', domain)
                            and not re.match('^V6_PROD', domain)
                            and not re.match('^NULL', domain)
                            and not re.match('^V5_QUAL', domain)
                            and not re.match('^V6_QUAL', domain)
                            and not re.match('^V5_DEV', domain)
                            and not re.match('^V6_DEV', domain)
                    ):
                        error = True
                    if (error):
                        logErr = True
                        error = False
                        rc = False
                        self.logIt("pylib.Amp.UpdateProperties.splitDaemonTable(): Invalid domain=" + domain + "\n")
                    if (logErr):
                        wString = str(myRow) + "\n"  # ???
                        self.logIt(wString)

                    ################################################
                    #	Write the data to the file.
                    ################################################
                    wString = "%-35s %-10s %-13s %-5s %-8s\n" % (application, appserver, appservertype, count, domain)
                    DFH.write(wString)
            # EndIf
            # EndFor
            DFH.close()
            self.FILES.append(myFile)
        # EndFor

        ################################################
        #	Add the non-runtime host data to the files.
        ################################################
        rc = self.writeNonRuntimeDaemonTableFiles(hosts, outputDir, True)
        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeConfigFiles()
    #
    #	DESCRIPTION:
    #		Write the cfg.<host> files into the config directory.
    #
    #	PARAMETERS:
    #		outputDir
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeConfigFiles(self, outputDir):
        """Write the cfg.<host> files into the config directory.
        PARAMETERS:
            outputDir         - directory of resulting files.
        RETURN:
            True for success or False
        """
        rc = True
        FH = None
        flag = False
        developerEmail = self.getDeveloperEmail()

        if (not os.access(outputDir, os.F_OK)): os.mkdir(outputDir)
        if (not os.access(outputDir, os.F_OK)):
            self.debug("pylib.Amp.AppUpdateProperties.writeConfigFiles(): Unable to create " + outputDir + ".\n")
            return False
        # Endif
        if (not os.access(outputDir, os.W_OK)):
            self.debug("pylib.Amp.AppUpdateProperties.writeConfigFiles(): " + outputDir + " is not writable.\n")
            return False
        # Endif

        ar = self.getAllHosts()

        for host in ar:
            flag = False
            myFile = outputDir + "/" + "cfg." + host

            try:
                FH = open(myFile, "w")
            except IOError as inst:
                self.logIt("pylib.Amp.AppUpdateProperties.writeConfigFiles(): Unable to open " + myFile + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
                return False
            # Endtry
            self.FILES.append(myFile)
            wString = "export USER_EMAIL_LIST=" + '"' + str(developerEmail) + '"' + "\n"
            FH.write(wString)
            FH.close()
        # Endfor
        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeComponentDefinitions()
    #
    #	DESCRIPTION:
    #		Write the files like app_uat_test2.V6_DEV.xml as the component
    #		definitions from the PUKE file.
    #
    #	PARAMETERS:
    #		outputDir
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeComponentDefinitions(self, outputDir):
        """Write the Write the files like app_uat_test2.V6_DEV.xml as the component definitions from the PUKE file.
        PARAMETERS:
            outputDir         - directory of resulting files.
        RETURN:
            True for success or False
        """
        rc = True
        FH = None
        flag = False
        hostApplicationNames = self.getHostApplicationComponentNames()
        applicationHash = {}

        if (not os.access(outputDir, os.F_OK)): os.mkdir(outputDir)
        if (not os.access(outputDir, os.F_OK)):
            self.debug(
                "pylib.Amp.AppUpdateProperties.writeComponentDefinitions(): Unable to create " + outputDir + ".\n")
            return False
        # Endif
        if (not os.access(outputDir, os.W_OK)):
            self.debug(
                "pylib.Amp.AppUpdateProperties.writeComponentDefinitions(): " + outputDir + " is not writable.\n")
            return False
        # Endif

        ##################################################
        #	Get a unique hash keyed on name and component.
        #	Something like perl hash{app}{comp} = 1
        ##################################################
        for componentDefintionName in hostApplicationNames:
            names = self.getComponentDefinitionApplicationNames(componentDefintionName)
            # print "names=" + str( names ) + "\n"
            # print "componentDefintionName=" + str( componentDefintionName ) + "\n"
            for name in names: applicationHash[name] = {componentDefintionName: 1}
        # Endfor
        # print "applicationHash=" + str( applicationHash ) + "\n"
        # test = applicationHash['app_ea_ias_deskb']['ea_ias_deskb']
        # print "test=" + str( test ) + "\n"

        #########################################################
        #	Now lets unpack the "hash" and do some work.
        #########################################################
        applications = list(applicationHash.keys())
        # print "applications=" + str( applications ) + "\n"
        for appName in applications:
            self.debug("pylib.Amp.AppUpdateProperties.writeComponentDefinitions(): appName=" + appName + ".\n")
            componentHash = applicationHash[appName]
            # print "componentHash=" + str( componentHash ) + "\n"
            compKeys = list(componentHash.keys())
            for componentName in compKeys:
                # print "componentName=" + str( componentName ) + "\n"

                #################################################################################
                #	Make sure the host application component name is in the component definition
                #	application names.
                #################################################################################
                # print "hostApplicationNames=" + str( hostApplicationNames ) + "\n"
                if (componentName not in hostApplicationNames):
                    rc = False
                    self.logIt(
                        "pylib.Amp.AppUpdateProperties.writeComponentDefinitions(): The WAS component=" + componentName + " is not in the runtimeHostDeploymentProperties list and therefore not in the daemon.<host> or selective update files.\n")
                # Endif

                ################################################################################
                #	Get the domain so we can construct the output file name.
                ################################################################################
                domain = self.getComponentDomain(componentName)
                if (domain is None):
                    self.logIt(
                        "pylib.Amp.AppUpdateProperties.writeComponentDefinitions(): Unable to get the domain for version=" + self.tag_version + ".\n")
                    continue
                # Endif

                myFile = outputDir + "/" + str(appName) + "." + str(domain) + ".xml"
                self.logIt(
                    "pylib.Amp.AppUpdateProperties.writeComponentDefinitions(): Writing " + myFile + " for componentDefinitions version=" + self.tag_version + ".\n")
                try:
                    FH = open(myFile, "w")
                except IOError as inst:
                    self.logIt(
                        "pylib.Amp.AppUpdateProperties.writeComponentDefinitions(): Unable to open " + myFile + " => " + str(
                            inst.errno) + ":" + str(inst.strerror) + "\n")
                    return False
                # Endtry
                self.FILES.append(myFile)
                flag = False

                ###############################################################################
                #	Get the XML for the websphere element that is to be written to the output
                #	file.
                ###############################################################################
                properties = self.getWASDeploymentProperties(componentName, appName)
                if (properties is not None):
                    header = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\n"
                    FH.write(header)
                    # xml_print( properties, FH )
                    myString = self.getXMLforNodes(properties)
                    FH.write(myString)
                    flag = True
                # Endif
                FH.close()
                if (not flag):
                    self.logIt(
                        "pylib.Amp.AppUpdateProperties.writeComponentDefinitions(): No WAS data was written for " + appName + " version=" + self.tag_version + ".\n")
                    rc = False
        # Endfor
        # Endfor

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeSelectedUpdateFile()
    #
    #	DESCRIPTION:
    #		Write the selected update daemon table from the PUKE file.
    #
    #	PARAMETERS:
    #		outputDir
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeSelectedUpdateFile(self, outputDir, fileName="selective_update.dat"):
        """Write the selected update daemon table from the PUKE file.
        PARAMETERS:
            outputDir   - directory of resulting files.
            fileName    - name of the selective update file.
        RETURN:
            True for success or False
        """
        rc = True
        FH = None
        myFile = outputDir + "/" + fileName
        flag = False
        daemonNames = []

        self.logIt("pylib.Amp.AppUpdateProperties.writeSelectedUpdateFile(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt(
                "pylib.Amp.AppUpdateProperties.writeSelectedUpdateFile(): Unable to open " + myFile + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        daemonsArray = self.getDaemonTableArray()

        ########################################################
        #	Get all the daemon names so that we can see
        #	if any are missing from the component definitions.
        ########################################################
        for row in daemonsArray:
            daemonName = row[1]
            type = self.getDeployableComponentDefinitionTypeByName(daemonName)
            if (type is None):
                self.logIt(
                    "pylib.Amp.AppUpdateProperties.writeSelectedUpdateFile(): WARNING: No componentType attribute found for " + daemonName + " in the applicationComponentConfigurations.  This may mean that the " + daemonName + " is not in the applicationsToUpdate list or that the \"componentType\" was not specified in the \"applicationComponentConfigurations\".\n")
                continue
            # Endif
            if (daemonName is not None and re.match(r'was', str(type))): daemonNames.append(daemonName)
        # Endfor

        #######################################################
        #	Add each deployable component to a unique array
        #######################################################
        componentNames = []
        for row in daemonsArray:
            daemonName = row[1]
            names = self.getDeployableComponentDefinitionNames()
            for name in names:
                componentNames.append(name)
                flag = True
        # Endfor
        # Endfor
        componentNames = self.utils.uniquer(componentNames)
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeSelectedUpdateFile(): " + myFile + " has no data.\n")
            rc = False
        else:
            #####################################################
            #	Write the unique components to the selected
            #	update file.
            #####################################################
            for name in componentNames: FH.write(str(name) + "\n")
        # Endif
        FH.close()
        #########################################################
        #	Check to see if we are missing any deployable
        #	components from the daemon_tables.
        #########################################################
        for name in componentNames:
            type = self.getDeployableComponentDefinitionTypeByName(name)
            if (not re.match(r'was', str(type))): continue
            if (name not in daemonNames):
                rc = False
                self.logIt(
                    "pylib.Amp.AppUpdateProperties.writeSelectedUpdateFile(): The deployable component=" + name + " is not in the daemon_table/component lis and therefore not in the selective update file " + myFile + ".\n")
        # Endif
        # Endfor
        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeRestartGroups()
    #
    #	DESCRIPTION:
    #		Write the restart_groups.dat file form the PUKE file.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeRestartGroups(self, outputDir, fileName="restart_groups.dat"):
        """Write the restart groups data file.
        PARAMETERS:
            outputDir   - directory of resulting files.
            fileName    - name of the restart groups file.
        RETURN:
            True for success or False
        """

        #########################################
        #	Initialize some things that we need.
        #########################################
        hashString = "##########################################################################################################"
        header = "%-6s %-15s %-8s %-8s %-24s %-35s\n" % (
            "#Group", "Host", "Domain", "Mnemonic", "RestartType", "Application")
        header2 = "%-6.6s %-15.15s %-8.8s %-8.8s %-24.24s %-35.35s\n" % (
            hashString, hashString, hashString, hashString, hashString, hashString)
        myFile = outputDir + "/" + fileName
        header = header + header2
        flag = False
        myRows = []
        rc = True
        FH = None
        restarts = self.getRestartTargetsArray()

        self.logIt("pylib.Amp.AppUpdateProperties.writeRestartGroups(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeRestartGroups(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        FH.write(header)
        for row in restarts:
            group = row[0]
            host = row[1]
            domain = row[2]
            mne = row[3]
            restartType = row[4]
            application = row[5]
            if (group is None):        group = "UNDEFINED"
            if (host is None):            host = "UNDEFINED"
            if (domain is None):        domain = "UNDEFINED"
            if (mne is None):            mne = "UNDEFINED"
            if (restartType is None):    restartType = "UNDEFINED"
            if (application is None):    application = "UNDEFINED"
            wString = "%-6s %-15s %-8s %-8s %-24s %-35s\n" % (group, host, domain, mne, restartType, application)
            FH.write(wString)
            flag = True
        # Endfor
        FH.close()
        if (not flag): self.logIt("pylib.Amp.AppUpdateProperties.writeRestartGroups(): " + myFile + " has no data.\n")
        return True

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeDaemonTables()
    #
    #	DESCRIPTION:
    #		Write the master daemon table and the individual daemon.<host>
    #		files from the application update properties file.
    #
    #	PARAMETERS:
    #		outputDir
    #		masterFile
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeDaemonTables(self, outputDir, masterFile):
        """Write the master daemon table and the individual daemon.<host> files from the application update properties file.
        PARAMETERS:
            outputDir   - directory of resulting files.
            masterFile  - name of the master daemons table file.
        RETURN:
            True for success or False
        """

        #########################################
        #	Initialize some things that we need.
        #########################################
        myFile = outputDir + "/" + masterFile
        hashString = "##########################################################################################################"
        header = "%-40s %-35s %-10s %-13s %-5s %-8s %-8s %-8s %-8s\n" % (
            "#Host", "ComponentName", "daemonType", "daemonSubType", "Count", "Domain", "Status", "SysType", "AppType")
        header2 = "%-40.40s %-35.35s %-10.10s %-13.13s %-5.5s %-8.8s %-8.8s %-8.8s %-8.8s\n" % (
            hashString, hashString, hashString, hashString, hashString, hashString, hashString, hashString, hashString)
        header = header + header2
        flag = False
        myRows = []
        rc = True

        #######################################
        #	Check to see if the given output
        #	directory exists.
        #######################################
        if (os.path.exists(outputDir)):
            self.debug("pylib.Amp.AppUpdateProperties.writeDaemonTables(): The directory " + outputDir + " exists.\n")
        else:
            ######################################
            #	No, so lets create it.
            ######################################
            self.logIt(
                "pylib.Amp.AppUpdateProperties.writeDaemonTables(): The directory " + outputDir + " does not exist.\n")
            os.makedirs(outputDir)

            #####################################
            #	Check to see if we created it.
            #####################################
            if (not os.path.exists(outputDir)):
                self.logIt(
                    "pylib.Amp.AppUpdateProperties.writeDaemonTables(): Cannot create the directory " + outputDir + ".\n")
                return False
        # Endif
        # Endif

        ############################################
        #	Okay we got the prelimary stuff done
        #	so lets get to work.
        ############################################
        try:
            self.logIt(
                "pylib.Amp.AppUpdateProperties.writeDaemonTables(): Writing " + myFile + " for mnemonic_files_list version=" + self.tag_version + "\n")
            FH = open(myFile, "w")
            FH.write(header)

            myRows = self.getDaemonTableArray()
            for row in myRows:
                host = row[0]
                componentName = row[1]
                daemonType = row[2]
                daemonSubType = row[3]
                count = row[4]
                domain = row[5]
                status = row[6]
                sysType = row[7]
                appType = row[8]
                if (host is None):                host = "UNDEFINED"
                if (componentName is None):    componentName = "UNDEFINED"
                if (daemonType is None):        daemonType = "UNDEFINED"
                if (daemonSubType is None):    daemonSubType = "UNDEFINED"
                if (count is None):            count = "UNDEFINED"
                if (domain is None):            domain = "UNDEFINED"
                if (status is None):            status = "UNDEFINED"
                if (sysType is None):            sysType = "UNDEFINED"
                if (appType is None):            appType = "UNDEFINED"

                wString = "%-40s %-35s %-10s %-13s %-5s %-8s %-8s %-8s %-8s\n" % (
                    host, componentName, daemonType, daemonSubType, count, domain, status, sysType, appType)
                FH.write(wString)
            # Endfor

            FH.close()
            self.FILES.append(myFile)
            flag = True
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeDaemonTables(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + ".\n")
            return False
        # EndTry

        if (flag):
            ###################################################
            #	Write the individual daemon.<host> files.
            ###################################################
            rc = self.splitDaemonTable(outputDir, myRows, False);
        else:
            self.logIt("pylib.Amp.AppUpdateProperties.writeDaemonTables(): " + myFile + "has no data.\n")
            return False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeDeveloperEmail()
    #
    #	DESCRIPTION:
    #		Write the developer email file from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeDeveloperEmail(self, outputDir, fileName="dev_email.dat"):
        """Write the developer email file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the dev email file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        email = self.getDeveloperEmail()

        self.logIt("pylib.Amp.AppUpdateProperties.writeDeveloperEmail(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeDeveloperEmail(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (email is not None):
            FH.write(email + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeDeveloperEmail(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeCCID()
    #
    #	DESCRIPTION:
    #		Write the ccid from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeCCID(self, outputDir, fileName="ccid.dat"):
        """Write the developer ccid file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the ccid file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getCCID()

        self.logIt("pylib.Amp.AppUpdateProperties.writeCCID(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeCCID(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(value + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeCCID(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeJobname()
    #
    #	DESCRIPTION:
    #		Write the jobname from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeJobname(self, outputDir, fileName="jobid.dat"):
        """Write the jobname file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the jobname file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getJobName()

        self.logIt("pylib.Amp.AppUpdateProperties.writeJobname(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeJobname(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(value + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeJobname(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeIsStageAcceptRequired()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeIsStageAcceptRequired(self, outputDir, fileName="isStageAcceptRequired.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getDeveloperAcceptPostStage()

        self.logIt("pylib.Amp.AppUpdateProperties.writeIsStageAcceptRequired(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt(
                "pylib.Amp.AppUpdateProperties.writeIsStageAcceptRequired(): Unable to open " + myFile + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(value + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeIsStageAcceptRequired(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeIsRestartRequired()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeIsRestartRequired(self, outputDir, fileName="isRestartRequired.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getRestartsRequired()

        self.logIt("pylib.Amp.AppUpdateProperties.writeIsRestartRequired(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt(
                "pylib.Amp.AppUpdateProperties.writeIsRestartRequired(): Unable to open " + myFile + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(value + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeIsRestartRequired(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeIsCleanInstallRequired()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeIsCleanInstallRequired(self, outputDir, fileName="isCleanInstallRequired.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getCleanInstall()

        self.logIt("pylib.Amp.AppUpdateProperties.writeIsCleanInstallRequired(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt(
                "pylib.Amp.AppUpdateProperties.writeIsCleanInstallRequired(): Unable to open " + myFile + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(value + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeIsRestartRequired(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeIsMaintencePathRequired()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeIsMaintencePathRequired(self, outputDir, fileName="isMaintenancePathRequired.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getMaintenancePathRequired()

        self.logIt("pylib.Amp.AppUpdateProperties.writeIsMaintencePathRequired(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt(
                "pylib.Amp.AppUpdateProperties.writeIsMaintencePathRequired(): Unable to open " + myFile + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(value + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeIsMaintencePathRequired(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeIsRestartAcceptRequired()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeIsRestartAcceptRequired(self, outputDir, fileName="isRestartAcceptRequired.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getDeveloperAcceptPostRestart()

        self.logIt("pylib.Amp.AppUpdateProperties.writeIsRestartAcceptRequired(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt(
                "pylib.Amp.AppUpdateProperties.writeIsRestartAcceptRequired(): Unable to open " + myFile + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(str(value) + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeIsRestartAcceptRequired(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeIsCheckAcceptRequired()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeIsCheckAcceptRequired(self, outputDir, fileName="isCheckAcceptRequired.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getDeveloperAcceptPostStage()

        self.logIt("pylib.Amp.AppUpdateProperties.writeIsCheckAcceptRequired(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt(
                "pylib.Amp.AppUpdateProperties.writeIsCheckAcceptRequired(): Unable to open " + myFile + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(value + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeIsCheckAcceptRequired(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeIsWas5Included()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeIsWas5Included(self, outputDir, fileName="isWASIncluded.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        indicator = self.isWas5Included()
        value = ""

        self.logIt("pylib.Amp.AppUpdateProperties.writeIsWas5Included(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeIsWas5Included(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (indicator is not None):
            if (indicator):
                value = "yes\n"
            else:
                value = "no\n"
            FH.write(value)
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeIsWas5Included(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeIsPortalIncluded()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeIsPortalIncluded(self, outputDir, fileName="isPortalIncluded.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        indicator = self.isPortalIncluded()
        value = ""

        self.logIt("pylib.Amp.AppUpdateProperties.writeIsPortalIncluded(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeIsPortalIncluded(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (indicator is not None):
            if (indicator):
                value = "yes\n"
            else:
                value = "no\n"
            FH.write(value)
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeIsPortalIncluded(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeRuntimeHosts()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeRuntimeHosts(self, outputDir, fileName="hosts_runtime.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        hosts = self.getRuntimeHosts()

        self.logIt("pylib.Amp.AppUpdateProperties.writeRuntimeHosts(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeRuntimeHosts(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        for host in hosts:
            FH.write(host + "\n")
            flag = True
        # Endfor
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeRuntimeHosts(): " + myFile + " has no data.\n")
            rc = True

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeNonRuntimeHosts()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeNonRuntimeHosts(self, outputDir, fileName="hosts_nonruntime.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        hosts = self.getOtherHosts()

        self.logIt("pylib.Amp.AppUpdateProperties.writeNonRuntimeHosts(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeNonRuntimeHosts(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        for host in hosts:
            FH.write(host + "\n")
            flag = True
        # Endfor
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeNonRuntimeHosts(): " + myFile + " has no data.\n")
            rc = True

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeWasAsHosts()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeWasAsHosts(self, outputDir, fileName="hosts_wasas.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        hosts = self.getHostsByTypeAndSubType("was", "as")

        self.logIt("pylib.Amp.AppUpdateProperties.writeWasAsHosts(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeWasAsHosts(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        for host in hosts:
            FH.write(host + "\n")
            flag = True
        # Endfor
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeWasAsHosts(): " + myFile + " has no data.\n")
            rc = True

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeWasWsHosts()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeWasWsHosts(self, outputDir, fileName="hosts_wasws.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        hosts = self.getHostsByTypeAndSubType("was", "ws")

        self.logIt("pylib.Amp.AppUpdateProperties.writeWasWsHosts(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeWasWsHosts(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        for host in hosts:
            FH.write(host + "\n")
            flag = True
        # Endfor
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeWasWsHosts(): " + myFile + " has no data.\n")
            rc = True

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeWasDmgrHosts()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeWasDmgrHosts(self, outputDir, fileName="hosts_wasdmgr.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        hosts = self.getHostsByTypeAndSubType("was", "dmgr")

        self.logIt("pylib.Amp.AppUpdateProperties.writeWasDmgrHosts(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeWasWsHosts(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        for host in hosts:
            FH.write(host + "\n")
            flag = True
        # Endfor
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeWasDmgrHosts(): " + myFile + " has no data.\n")
            rc = True

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writePortalPortalHosts()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writePortalPortalHosts(self, outputDir, fileName="hosts_portal.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        hosts = self.getHostsByTypeAndSubType("portal", "portal")

        self.logIt("pylib.Amp.AppUpdateProperties.writePortalPortalHosts(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeWasWsHosts(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        for host in hosts:
            FH.write(host + "\n")
            flag = True
        # Endfor
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writePortalPortalHosts(): " + myFile + " has no data.\n")
            rc = True

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writePortalDmgrHosts()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writePortalDmgrHosts(self, outputDir, fileName="hosts_portaldmgr.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        hosts = self.getHostsByTypeAndSubType("portal", "dmgr")

        self.logIt("pylib.Amp.AppUpdateProperties.writePortalDmgrHosts(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeWasWsHosts(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        for host in hosts:
            FH.write(host + "\n")
            flag = True
        # Endfor
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writePortalDmgrHosts(): " + myFile + " has no data.\n")
            rc = True

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeGenericGenericHosts()
    #
    #	DESCRIPTION:
    #		Write the data from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeGenericGenericHosts(self, outputDir, fileName="hosts_rp.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        hosts = self.getHostsByTypeAndSubType("generic", "generic")

        self.logIt("pylib.Amp.AppUpdateProperties.writeGenericGenericHosts(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeWasWsHosts(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        for host in hosts:
            FH.write(host + "\n")
            flag = True
        # Endfor
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeGenericGenericHosts(): " + myFile + " has no data.\n")
            rc = True

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeEnv()
    #
    #	DESCRIPTION:
    #		Write the env file from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeEnv(self, outputDir, fileName="environment.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getEnv()

        self.logIt("pylib.Amp.AppUpdateProperties.writeEnv(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeEnv(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(value + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeEnv(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeMne()
    #
    #	DESCRIPTION:
    #		Write the mne file from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeMne(self, outputDir, fileName="mne.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getMNE()

        self.logIt("pylib.Amp.AppUpdateProperties.writeMne(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeMne(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(value + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeMne(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeAmpId()
    #
    #	DESCRIPTION:
    #		Write the mne file from the PUKE.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeAmpId(self, outputDir, fileName="ampid.dat"):
        """Write the data file from the PUKE.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getAmpId()

        self.logIt("pylib.Amp.AppUpdateProperties.writeAmpId(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeAmpId(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(value + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeAmpId(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeAutosysDate()
    #
    #	DESCRIPTION:
    #		Write the autosys date file from the application update properties file.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeAutosysDate(self, outputDir, fileName="autosys_date.dat"):
        """Write the autosys date file from the application update properties file.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = False
        rc = True
        FH = None
        value = self.getDeploymentDate()

        if (not self.isDateValid(value)):
            self.logIt(
                "pylib.Amp.AppUpdateProperties.writeAutosysDate(): " + value + " is an invalid autosys date format(YYYYMMDD)\n")
            rc = False
        # Endif
        self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysDate(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysDate(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            value = self.formatYYYYMMDDtoMMDDYYYY(value)
            FH.write(value + "\n")
            flag = True
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysDate(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeAutosysTime()
    #
    #	DESCRIPTION:
    #		Write the autosys date file from the application update properties file.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeAutosysTime(self, outputDir, fileName="autosys_time.dat"):
        """Write the autosys date file from the application update properties file.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = True
        rc = True
        FH = None
        value = self.getDeploymentTime()

        if (not self.isTimeValid(value)):
            self.logIt(
                "pylib.Amp.AppUpdateProperties.writeAutosysTime(): " + value + " is an invalid time format(HHMM)\n")
            rc = False
        # Endif
        self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysTime(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysTime(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            if (self.isTimeValid(value)):
                if (value == "asap"):
                    FH.write(value + "\n")
                else:
                    myMatch = re.match(r'(\d{2})(\d{2})', str(value))
                    hour = myMatch.group(1)
                    minute = myMatch.group(2)
                    value = hour + ":" + minute
                    FH.write(value + "\n")
            # Endif
            else:
                flag = False
            # Endif
            flag = True
        # Endif
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysTime(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeRunAfterJobName()
    #
    #	DESCRIPTION:
    #		Write the runafter file from the application update properties file.
    #
    #	PARAMETERS:
    #		outputDir
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeRunAfterJobName(self, outputDir, fileName="autosys_runafter.dat"):
        """Write the runafer file from the application update properties file.
        PARAMETERS:
            outputDir - directory of resulting files.
            fileName  - name of the data file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = True
        rc = True
        FH = None
        value = self.getRunAfterJobName()

        self.logIt("pylib.Amp.AppUpdateProperties.writeRunAfterJobName(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeRunAfterJobName(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (value is not None):
            FH.write(value + "\n")
            flag = True
        # Endif
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeRunAfterJobName(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeAutosysInsertJil()
    #
    #	DESCRIPTION:
    #		Write the autosys insert jil file.
    #
    #	PARAMETERS:
    #		outputDir
    #		machine
    #		jobname
    #		ampid
    #		jilCommand
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeAutosysInsertJil(self, outputDir, machine, jobname, ampid, jilCommand, fileName="autosys_insert_jil.dat"):
        """Write the autosys insert jil file.
        PARAMETERS:
            outputDir - directory of resulting files.
            machine   - name of the host.
            jobname   - name of the amp job.
            ampid     - amp request id.
            jilCommand   - the jil command to be executed.
            fileName   - name of the file file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = True
        rc = True
        FH = None

        self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysInsertJil(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysInsertJil(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (jobname is not None and machine is not None):
            wString = "insert_job: " + jobname + " job_type: c\n"
            FH.write(wString)
            wString = "command: " + jilCommand + "\n"
            FH.write(wString)
            wString = "machine: " + machine + "\n"
            FH.write(wString)
            wString = "owner: " + "root@" + machine + "\n"
            FH.write(wString)
            wString = "permission: " + "gx,wx" + "\n"
            FH.write(wString)
            wString = "alarm_if_fail: " + "1" + "\n"
            FH.write(wString)
            wString = "job_load: " + "20" + "\n"
            FH.write(wString)
            wString = "priority: " + "1" + "\n"
            FH.write(wString)
        else:
            flag = False
        # Endif
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysInsertJil(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	writeAutosysUpdateJil()
    #
    #	DESCRIPTION:
    #		Write the runafter file from the application update properties file.
    #
    #	PARAMETERS:
    #		outputDir
    #		machine
    #		jobname
    #		ampid
    #		jilCommand
    #		fileName
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeAutosysUpdateJil(self, outputDir, machine, jobname, ampid, jilCommand, fileName="autosys_update_jil.dat"):
        """Write the autosys update jil file.
        PARAMETERS:
            outputDir - directory of resulting files.
            machine   - name of the host.
            jobname   - name of the amp job.
            ampid     - amp request id.
            jilCommand   - the jil command to be executed.
            fileName   - name of the file file.
        RETURN:
            True for success or False
        """
        myFile = outputDir + "/" + fileName
        flag = True
        rc = True
        FH = None

        self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysUpdateJil(): Writing " + myFile + "\n")
        try:
            FH = open(myFile, "w")
        except IOError as inst:
            self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysUpdateJil(): Unable to open " + myFile + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            return False
        # Endtry
        self.FILES.append(myFile)

        if (jobname is not None and machine is not None):
            wString = "update_job: " + jobname + " job_type: c\n"
            FH.write(wString)
            wString = "command: " + jilCommand + "\n"
            FH.write(wString)
            wString = "machine: " + machine + "\n"
            FH.write(wString)
            wString = "owner: " + "root@" + machine + "\n"
            FH.write(wString)
            wString = "permission: " + "gx,wx" + "\n"
            FH.write(wString)
            wString = "alarm_if_fail: " + "1" + "\n"
            FH.write(wString)
            wString = "job_load: " + "20" + "\n"
            FH.write(wString)
            wString = "priority: " + "1" + "\n"
            FH.write(wString)
        else:
            flag = False
        # Endif
        FH.close()
        if (not flag):
            self.logIt("pylib.Amp.AppUpdateProperties.writeAutosysUpdateJil(): " + myFile + " has no data.\n")
            rc = False

        return rc

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	isDateValid()
    #
    #	DESCRIPTION:
    #		Check to see if the given date is a valid YYYYMMDD format.
    #
    #	PARAMETERS:
    #		date - The date to be validated.
    #
    #	RETURN:
    #		True or False
    ##################################################################################
    def isDateValid(self, date):
        """Check to see if the given date is a valid YYYYMMDD format.
        PARAMETERS:
            date - date to be validated.
        RETURN:
            True or False
        """

        year = None
        month = None
        day = None
        if (not re.match(r'^\d{8}$', str(date))): return False
        if (not re.match(r'(\d{4})(\d{2})(\d{2})', str(date))): return False
        dateMatch = re.match(r'(\d{4})(\d{2})(\d{2})', str(date))
        year = dateMatch.group(1)
        month = dateMatch.group(2)
        day = dateMatch.group(3)
        if (int(year) < 1000 or int(year) > 9999): return False
        self.debug("pylib.Amp.AppUpdateProperties.isDateValid(): year=" + year + "\n")
        if (int(month) < 1 or int(month) > 12): return False
        self.debug("pylib.Amp.AppUpdateProperties.isDateValid(): month=" + month + "\n")
        if (int(day) < 1 or int(day) > 31): return False
        self.debug("pylib.Amp.AppUpdateProperties.isDateValid(): day=" + day + "\n")

        return True

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	isTimeValid()
    #
    #	DESCRIPTION:
    #		Check to see if the given date is a valid HHMM format.
    #
    #	PARAMETERS:
    #		time - The time to be validated.
    #
    #	RETURN:
    #		True or False
    ##################################################################################
    def isTimeValid(self, time):
        """Check to see if the given date is a valid HHMM format.
        PARAMETERS:
            time - time to be validated.
        RETURN:
            True or False
        """

        if (time == "asap"): return True
        hour = None
        minute = None
        if (not re.match(r'^\d{4}$', str(time))): return False
        dateMatch = re.match(r'(\d{2})(\d{2})', str(time))
        hour = dateMatch.group(1)
        minute = dateMatch.group(2)
        if (int(hour) < 0 or int(minute) > 60): return False
        self.debug("pylib.Amp.AppUpdateProperties.isTimeValid(): hour=" + hour + "\n")
        if (int(minute) < 0 or int(minute) > 60): return False
        self.debug("pylib.Amp.AppUpdateProperties.isTimeValid(): minute=" + minute + "\n")

        return True

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	formatYYYYMMDDtoMMDDYYYY()
    #
    #	DESCRIPTION:
    #		Format a YYYYMMDD date to MM/DD/YYYY.
    #
    #	PARAMETERS:
    #		date - The date to be formated.
    #
    #	RETURN:
    #		date
    ##################################################################################
    def formatYYYYMMDDtoMMDDYYYY(self, date):
        """Format a YYYYMMDD date to MM/DD/YYYY.
        PARAMETERS:
            date - date to be formatted.
        RETURN:
            The formatted date string.
        """

        year = None
        month = None
        day = None
        if (not self.isDateValid(date)): return date
        dateMatch = re.match(r'(\d{4})(\d{2})(\d{2})', str(date))
        year = dateMatch.group(1)
        month = dateMatch.group(2)
        day = dateMatch.group(3)
        date = str(month) + "/" + str(day) + "/" + str(year)

        return date

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	isAutosysDateValid()
    #
    #	DESCRIPTION:
    #		Check to see if the given date is a valid YYYY-MM-DD HH:MM:SS format.
    #
    #	PARAMETERS:
    #		date - The date to be validated.
    #
    #	RETURN:
    #		True or False
    ##################################################################################
    def isAutosysDateTimeValid(self, date):
        """Check to see if the given date is a valid YYYY-MM-DD HH:MM:SS format.
        PARAMETERS:
            date - date to be validated.
        RETURN:
            True or False
        """

        year = None
        month = None
        day = None
        hour = None
        minute = None
        second = None
        dateMatch = re.match(r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$', str(date))
        if (dateMatch is None): return False
        year = dateMatch.group(1)
        month = dateMatch.group(2)
        day = dateMatch.group(3)
        hour = dateMatch.group(4)
        minute = dateMatch.group(5)
        second = dateMatch.group(6)

        if (int(year) < 1000 or int(year) > 9999): return False
        self.debug("pylib.Amp.AppUpdateProperties.isAutosysDateTimeValid(): year=" + year + "\n")

        if (int(month) < 1 or int(month) > 12): return False
        self.debug("pylib.Amp.AppUpdateProperties.isAutosysDateTimeValid(): month=" + month + "\n")

        if (int(day) < 1 or int(day) > 31): return False
        self.debug("pylib.Amp.AppUpdateProperties.isAutosysDateTimeValid(): day=" + day + "\n")

        if (int(hour) < 0 or int(hour) > 60): return False
        self.debug("pylib.Amp.AppUpdateProperties.isAutosysDateTimeValid(): hour=" + hour + "\n")

        if (int(minute) < 0 or int(minute) > 60): return False
        self.debug("pylib.Amp.AppUpdateProperties.isAutosysDateTimeValid(): minute=" + minute + "\n")

        if (int(second) < 0 or int(second) > 60): return False
        self.debug("pylib.Amp.AppUpdateProperties.isAutosysDateTimeValid(): second=" + second + "\n")

        return True

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	formatYYYYMMDDtoMMDDYYYY()
    #
    #	DESCRIPTION:
    #		Format the date from YYYYMMDD to MM/DD/YYYY.
    #
    #	PARAMETERS:
    #		date - The date in the YYYYMMDD format.
    #
    #	RETURN:
    #		date
    ##################################################################################
    def formatYYYMMDDtoMMDDYYYY(self, date):
        """Format the date from YYYYMMDD to MM/DD/YYYY.
        PARAMETERS:
            date - date to be formatted.
        RETURN:
            formatted date string.
        """
        dateAR = []
        mydate = ""

        if (self.isDateValid(date)):
            dateMatch = re.match(r'(\d{4})(\d{2})(\d{2})', str(date))
            year = dateMatch.group(1)
            month = dateMatch.group(2)
            day = dateMatch.group(3)
            mydate = month + "/" + day + "/" + year
            # print "mydate=" + mydate + "\n"
            return mydate
        else:
            self.logIt(
                "pylib.Amp.AppUpdateProperties.formatYYYYMMDDtoMMDDYYYY(): " + date + " is not a valid format.\n")
        # Endif
        return date


##################################################################################


# Enddef
##################################################################################

#####################################################################################
# Endclass
#####################################################################################

#########################################################################
#	For testing.
#########################################################################
def main():
    myLogger = MyLogger(LOGFILE="/tmp/AppUpdateProperties.log", STDOUT=True, DEBUG=False)
    # myObject = AppUpdateProperties(xml_file="/nfs/home4/trpapp/appd4ec/tmp/QAMP_UAT0000000_090504130000i.xml",
    myObject = AppUpdateProperties(
        xml_file="/tmp/denis.xml",
        logger=myLogger);
    # myObject = AppUpdateProperties(xml_file="/nfs/home4/trpapp/appd4ec/tmp/QAMP_UAT0000000_090504130000i.xml");
    # myObject.print_xml()
    # myObject.log_xml()
    # myObject.logIt( "main(): Hello world\n" )
    # myObject.debug( "main(): Debug Hello world\n" )
    # myObject.getDaemonTableHostsArray()
    # hostArray = myObject.getDaemonTableHostsArray()
    # print hostArray
    # myObject.logIt( "main(): " + str( hostArray ) + "\n" )
    # tableArray = myObject.getDaemonTableArray()
    # print tableArray
    # componentElements	= myObject.getDaemonTableComponents( "didmgr11" )
    # print componentElements
    # for el in componentElements:
    #	myObject.logMyElement( el )
    # status = myObject.getComponentDefinitionStatusByName( "ea_ias_deska" )
    # print "status=" + status +"\n"

    myObject.write_xml("/tmp/denis.xml")
    myObject.writeDaemonTables("/tmp/denis2", "master.dat")
    rc = myObject.writeTOC(outputDir="/tmp/denis2")
    rc = myObject.writeConfigFiles("/tmp/denis2")
    rc = myObject.writeSelectedUpdateFile("/tmp/denis2")
    rc = myObject.writeComponentDefinitions("/tmp/denis2")
    rc = myObject.writeRestartGroups("/tmp/denis2")
    rc = myObject.writeDeveloperEmail("/tmp/denis2")
    rc = myObject.writeCCID("/tmp/denis2")
    rc = myObject.writeJobname("/tmp/denis2")
    ##msg = "Date is valid."
    ##if( myObject.isDateValid( "20090817" ) ): print( msg )
    ##print "isDateValid returns " + str( myObject.isDateValid( "20090817" ) )
    ##mydate = myObject.formatYYYMMDDtoMMDDYYYY( "20090817" )
    ##print( "mydate=" + mydate )
    rc = myObject.writeAutosysDate("/tmp/denis2")
    rc = myObject.writeAutosysTime("/tmp/denis2")
    rc = myObject.writeRunAfterJobName("/tmp/denis2")
    rc = myObject.writeAutosysInsertJil("/tmp/denis2", "dapp41", "myjobname", "999999",
                                        "/nfs/dist/trp/amp/bin/IW_MASTER_run_deployment_workflow -jobid myjobname -ampid 999999")
    rc = myObject.writeAutosysUpdateJil("/tmp/denis2", "dapp41", "myjobname", "999999",
                                        "/nfs/dist/trp/amp/bin/IW_MASTER_run_deployment_workflow -jobid myjobname -ampid 999999")
    rc = myObject.writeEnv("/tmp/denis2")
    rc = myObject.writeMne("/tmp/denis2")
    rc = myObject.writeAmpId("/tmp/denis2")
    rc = myObject.writeIsWas5Included("/tmp/denis2")
    rc = myObject.writeIsPortalIncluded("/tmp/denis2")
    rc = myObject.writeRuntimeHosts("/tmp/denis2")
    rc = myObject.writeNonRuntimeHosts("/tmp/denis2")
    rc = myObject.writeWasAsHosts("/tmp/denis2")
    rc = myObject.writeWasWsHosts("/tmp/denis2")
    rc = myObject.writeWasDmgrHosts("/tmp/denis2")
    rc = myObject.writePortalPortalHosts("/tmp/denis2")
    rc = myObject.writePortalDmgrHosts("/tmp/denis2")
    rc = myObject.writeGenericGenericHosts("/tmp/denis2")
    rc = myObject.writeIsCheckAcceptRequired("/tmp/denis2")
    rc = myObject.writeIsRestartAcceptRequired("/tmp/denis2")
    rc = myObject.writeIsMaintencePathRequired("/tmp/denis2")
    rc = myObject.writeIsCleanInstallRequired("/tmp/denis2")
    rc = myObject.writeIsRestartRequired("/tmp/denis2")
    rc = myObject.writeIsStageAcceptRequired("/tmp/denis2")

    myObject.closeMe();


##################################################################################
# Enddef
##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
    main()
