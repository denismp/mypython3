#!/bin/env python
######################################################################################
##	MyXML.py
##
##	Jython module to deal with nu.xom xpath queries.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	09/01/2009	Denis M. Putnam		Created.
######################################################################################
import time
import os, sys
import re
# from xml.dom import minidom
import xml

from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.XML.MyAttribute import *
from pylib.XML.MyElement import *
# import java.io.IOException
# import nu.xom.Builder
# import nu.xom.Document
# import nu.xom.ParsingException
from xml.dom.minidom import parse, parseString, getDOMImplementation


class MyXML:
    """
    MyXML class wrapper for the nu.xom class library.
        NOTE:  the nu.xom library is a java library.  I converted this to the xml.dom
        library, but none of this has been tested.
    """

    ##################################################################################
    #	__init__()
    #
    #	DESCRIPTION:
    #		Class initializer.
    #
    #	PARAMETERS:
    #		logger  - instance of the pylib.Utils.MyLogger class.
    #		URI     - something like "file:///nfs/dist/trp/amp/update/UAT/QUAL/QAMP_UAT0000000_090504130000i/QAMP_UAT0000000_090504130000i.xml"
    #
    #	RETURN:
    #		An instance of this class
    ##################################################################################
    def __init__(
            self,
            logger=None,
            URI=""
    ):
        """Class Initializer.
           PARAMETERS:
               logger - instance of the pylib.Utils.MyLogger class.
               URI    - "file:///nfs/dist/trp/amp/update/UAT/QUAL/QAMP_UAT0000000_090504130000i/QAMP_UAT0000000_090504130000i.xml"
        """
        self.logger = logger
        self.URI = URI
        self.parser = None
        self.document = None
        self.rootElement = None
        try:
            # self.parser = nu.xom.Builder()
            # self.document = self.parser.build(self.URI)
            self.parser = parse
            self.document = parse(self.URI)
            # print self.document.toXML()
            self.rootElement = self.document.getRootElement()
        except SyntaxError as e:
            print(self.URL + " is not well-formed.")
            # print(self.URL + " unable to load module.")
            print(e)
        except IOError as inst:
            print(("Unable to open " + str(self.URI) + " => " + str(inst.errno) + ":" + str(inst.strerror)), end=' ')
            raise

    # Endtry
    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	getRootDocumentXML()
    #
    #	DESCRIPTION:
    #		Get root document XML.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		a string of the root document XML.
    ##################################################################################
    def getRootDocumentXML(self):
        """
        Get the root document XML.
        RETURN:
            A string containing the XML of the entire document.
        """
        return self.document.toXML()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getXML()
    #
    #	DESCRIPTION:
    #		Get the element XML.
    #
    #	PARAMETERS:
    #		element - an instance of nu.xom.Element, nu.xom.Node
    #
    #	RETURN:
    #		a string of the root document XML.
    ##################################################################################
    def getXML(self, element):
        """
        Get the element XML.
        PARAMETERS:
            element - an instance of nu.xom.Element or nu.xom.Node
        RETURN:
            A string containing the XML of the element.
        """
        # if isinstance(element, nu.xom.Element) or isinstance(element, nu.xom.Node):
        if (isinstance(element, xml.dom.Node.ELEMENT_NODE)):
            return element.toXML()
        else:
            return ""

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getXMLforNodes()
    #
    #	DESCRIPTION:
    #		Get the nu.xom.Nodes XML.
    #
    #	PARAMETERS:
    #		nodes - an instance of nu.xom.Nodes
    #
    #	RETURN:
    #		a string of the document XML.
    ##################################################################################
    def getXMLforNodes(self, nodes, index=None):
        """
        Get the nu.xom.Nodes XML.
        PARAMETERS:
            nodes - an instance of nu.xom.Nodes
            index   - index of the element.
        RETURN:
            A string containing the XML of the Nodes.
        """
        rString = ""
        # if isinstance(nodes, nu.xom.Nodes):
        if isinstance(nodes, xml.dom.Node.DOCUMENT_NODE):
            nodeCount = nodes.size()
            if index is None:
                for i in range(0, nodeCount):
                    ############################################
                    #	Get each element in the nu.xom.Nodes
                    ############################################
                    node = nodes.get(i)
                    print(node)
                    rString = rString + node.toXML()
            # Endfor
            else:
                if index < nodeCount:
                    node = nodes.get(index)
                    rString = node.toXML()
        # Endif
        # Endif
        else:
            self.logIt("pylib.XML.MyXML.getXMLforNodes(): nodes is not of type nu.xom.Nodes.\n")
            return ""
        # Endif
        return rString

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	xpathQuery()
    #
    #	DESCRIPTION:
    #		Perform an xpath query.
    #
    #	PARAMETERS:
    #		xpath  - somthing like '//root/element/element2[@name="value"]'
    #		offset - defaults to None which returns nu.xom.Nodes or an integer which returns
    #				 a particular nu.xom.Node
    #
    #	RETURN:
    #		nu.xom.Nodes or nu.xom.Node or None
    ##################################################################################
    def xpathQuery(self, xpath, offset=None):
        """
        Perform an xpath query.
        PARAMETERS:
            xpath  - somthing like '//root/element/element2[@name="value"]'
            offset - defaults to None which returns nu.xom.Nodes, or an integer index
                     which returns a particular nu.xom.Node.
        RETURN:
            nu.xom.Nodes or nu.xom.Node or None
        """
        self.debug("pylib.XML.xpathQuery(): xpath=" + xpath + "\n")
        result = self.rootElement.query(xpath)

        if offset is not None:
            nodeCount = result.size()
            if nodeCount == 0:
                self.logIt("pylib.XML.xpathQuery(): No results found.\n")
                return None
            elif nodeCount - 1 > offset:
                self.logIt("pylib.XML.xpathQuery(): Offset is greater than the number of results.\n")
                return None
            else:
                return result.get(offset)
        # Endif
        else:
            return result

    # Endif
    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getData()
    #
    #	DESCRIPTION:
    #		Perform an xpath query.
    #
    #	PARAMETERS:
    #		xpath  - somthing like '//root/element/element2[@name="value"]'
    #		offset - defaults to None which returns nu.xom.Nodes or an integer which returns
    #				 a particular nu.xom.Node
    #
    #	RETURN:
    #		nu.xom.Nodes or nu.xom.Node or None
    ##################################################################################
    def getData(self, xpath, offset=None):
        """
        Perform an xpath query.
        PARAMETERS:
            xpath  - somthing like '//root/element/element2[@name="value"]'
            offset - defaults to None which returns nu.xom.Nodes or an integer index
                     which returns a particular nu.xom.Node.
        RETURN:
            nu.xom.Nodes or nu.xom.Node or None
        """
        self.debug("pylib.XML.getData(): xpath=" + xpath + "\n")
        results = self.xpathQuery(xpath, offset=offset)
        return self.getElementInfo(results)

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	makeMyElement()
    #
    #	DESCRIPTION:
    #		Make a new instance of the pylib.XML.MyElement class.
    #
    #	PARAMETERS:
    #		element - nu.xom.Element
    #
    #	RETURN:
    #       A MyElement instance.
    ##################################################################################
    def makeMyElement(self, element):
        """
        Make a new instance of the pylib.XML.MyElement class.
        PARAMETERS:
            element - nu.xom.Element
        RETURN:
            A pylib.XML.MyElement instance.
        """
        elname = element.getLocalName().strip()
        elvalue = element.getValue().split("\n")[0]
        myElement = MyElement(logger=self.logger, name=elname, value=elvalue)
        attrCount = element.getAttributeCount()
        for i in range(0, attrCount):
            myAttr = element.getAttribute(i)
            attrName = myAttr.getLocalName()
            attrValue = element.getAttributeValue(attrName)
            myAttribute = MyAttribute(logger=self.logger, name=attrName, value=attrValue)
            myElement.addAttribute(myAttribute)
        return myElement

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getElementInfo()
    #
    #	DESCRIPTION:
    #		Get the complete tree of the element information.
    #
    #	PARAMETERS:
    #		element - nu.xom.Element or nu.xom.Nodes
    #
    #	RETURN:
    #       a array of MyElement instances.
    ##################################################################################
    def getElementInfo(self, element):
        """
        Get the complete tree of element information.
        PARAMETERS:
            element - nu.xom.Element or nu.xom.Nodes
        RETURN:
            an array of MyElement instances.
        """
        ar = []
        # if isinstance(element, nu.xom.Element):
        if isinstance(element, xml.dom.Node.ELEMENT_NODE):
            ##############################################
            #	Make an MyElement instance
            #	and add it to the return array.
            ##############################################
            myElement = self.makeMyElement(element)
            ar.append(myElement)

            #############################################
            #	Recursively walk down the XML tree to
            #	build the rest of the return array.
            #############################################
            childCount = element.getChildCount()
            childElements = element.getChildElements()
            for i in range(0, childCount):
                child = element.getChild(i)
                myAr = self.getElementInfo(child)
                if len(myAr) > 0: ar.extend(myAr)
        # Endfor
        # elif isinstance(element, nu.xom.Nodes):
        elif isinstance(element, xml.dom.Node.DOCUMENT_NODE):
            ############################################
            #	Nodes consist of nu.xom.Element's
            ############################################
            nodeCount = element.size()
            for i in range(0, nodeCount):
                ############################################
                #	Get each element in the nu.xom.Nodes
                ############################################
                node = element.get(i)

                ############################################
                #	Make and MyElement instance
                #	and add it to the return array.
                ############################################
                myElement = self.makeMyElement(node)
                ar.append(myElement)
                childCount = node.getChildCount()
                childElements = node.getChildElements()

                #############################################
                #	Recursively walk down the XML tree to
                #	build the rest of the return array.
                #############################################
                for i in range(0, childCount):
                    child = node.getChild(i)
                    myAr = self.getElementInfo(child)
                    if len(myAr) > 0: ar.extend(myAr)
        # Endfor
        # Endfor
        # Endif
        return ar

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	logMyElement()
    #
    #	DESCRIPTION:
    #		Log the given MyElement instance to the logger.
    #
    #	PARAMETERS:
    #		myElement - an instance of the pylib.XML.MyElement class.
    #
    #	RETURN:
    ##################################################################################
    def logMyElement(self, myElement):
        """
        Log the given MyElement instance to the logger.
        PARAMETERS:
           myElement - an instance to the pylib.XML.MyElement class.
        RETURN:
           None
        """
        self.logIt("pylib.XML.MyXML.logMyElement(): elname=" + '"' + myElement.getName() + '"' + "\n")
        self.logIt("pylib.XML.MyXML.logMyElement(): elvalue=" + '"' + myElement.getValue() + '"' + "\n")
        myAttrs = myElement.getAllAttributes()
        for myAttr in myAttrs:
            self.logIt("pylib.XML.MyXML.logMyElement(): \tattname=" + '"' + myAttr.getName() + '"' + "\n")
            self.logIt("pylib.XML.MyXML.logMyElement(): \tattvalue=" + '"' + myAttr.getValue() + '"' + "\n")

    # Endfor

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	printMyElement()
    #
    #	DESCRIPTION:
    #		Print the given MyElement instance to the stdout.
    #
    #	PARAMETERS:
    #		myElement - an instance of the pylib.XML.MyElement class.
    #
    #	RETURN:
    ##################################################################################
    def printMyElement(self, myElement):
        """
        Log the given MyElement instance to the stdout.
        PARAMETERS:
           myElement - an instance to the pylib.XML.MyElement class.
        RETURN:
           None
        """
        print(("elname=" + '"' + myElement.getName() + '"'))
        print(("elvalue=" + '"' + myElement.getValue() + '"'))
        myAttrs = myElement.getAllAttributes()
        for myAttr in myAttrs:
            print(("\tattname=" + '"' + myAttr.getName() + '"'))
            print(("\tattvalue=" + '"' + myAttr.getValue() + '"'))

    # Endfor
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
    #	Enddef
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
#	Enddef
##################################################################################

##################################################################################
#	Endclass
##################################################################################


def main():
    """Unit testing."""
    myLogger = MyLogger(LOGFILE="/tmp/MyXML.log", STDOUT=True, DEBUG=True)
    myObject = MyXML(myLogger,
                     URI="file:///nfs/dist/trp/amp/update/UAT/QUAL/QAMP_UAT0000000_090504130000i/QAMP_UAT0000000_090504130000i.xml")
    myObject.logIt("main(): Hello world\n")
    myObject.debug("main(): Debug Hello world\n")

    result = myObject.xpathQuery("/applicationUpdateProperties/updateParameters/ccid")
    ar = myObject.getElementInfo(result)
    print(type(ar))
    print(ar)
    for el in ar:
        myObject.logMyElement(el)
    # myObject.printMyElement( el )

    result = myObject.xpathQuery("/applicationUpdateProperties/updateParameters/ccid", offset=0)
    print(type(ar))
    print(ar)
    for el in ar:
        myObject.logMyElement(el)
    # myObject.printMyElement( el )

    result = myObject.xpathQuery(
        '/applicationUpdateProperties/runtimeHostDeploymentProperties/hostApplicationLists/hostApplicationList[@hostName="didmgr11"]',
        offset=0)
    print(type(result))
    ar = myObject.getElementInfo(result)
    print(type(ar))
    print(ar)
    for el in ar:
        myObject.logMyElement(el)
    # myObject.printMyElement( el )

    result = myObject.xpathQuery(
        '/applicationUpdateProperties/applicationComponentConfigurations/applicationConfigurations/domainApplicationComponentConfiguration/runtimeFiles')
    ar = myObject.getElementInfo(result)
    print(type(ar))
    print(ar)
    for el in ar:
        myObject.logMyElement(el)
    # myObject.printMyElement( el )
    # print type( result )
    # print ar
    myObject.closeMe();


##################################################################################
#	Enddef
##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
    main()
