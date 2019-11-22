#!/bin/env python
######################################################################################
##	MyElement.py
##
##	Jython module contains MyElement data and methods.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	09/03/2009	Denis M. Putnam		Created.
######################################################################################
import time
import os, sys
import re
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.XML.MyAttribute import *


class MyElement:
    """MyElement class contains MyElement data, which consists of name/value and its list of attributes."""

    ##################################################################################
    #	__init__()
    #
    #	DESCRIPTION:
    #		Class initializer.
    #
    #	PARAMETERS:
    #		logger  - instance of the pylib.Utils.MyLogger class.
    #		name    - name of the attribute.
    #		value   - value of the attribute.
    #
    #	RETURN:
    #		An instance of this class
    ##################################################################################
    def __init__(
            self,
            logger=None,
            name=None,
            value=None
    ):
        """Class Initializer.
           PARAMETERS:
               logger - instance of the pylib.Utils.MyLogger class.
               name   - name of the attribute.
               value  - value of the attribute.
        """
        self.logger = logger
        self.name = name
        self.value = value
        self.attributes = []

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	getName()
    #
    #	DESCRIPTION:
    #		Get the name of this element.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		name
    ##################################################################################
    def getName(self):
        """Get the name of this element."""

        return self.name

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	setName()
    #
    #	DESCRIPTION:
    #		Set the name of this element.
    #
    #	PARAMETERS:
    #		name
    #
    #	RETURN:
    #		name
    ##################################################################################
    def setName(self, name):
        """Set the name of this element."""

        self.name = name

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getValue()
    #
    #	DESCRIPTION:
    #		Get the name of this element.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		name
    ##################################################################################
    def getValue(self):
        """Get the value of this element."""

        return self.value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	setValue()
    #
    #	DESCRIPTION:
    #		Set the value of this element.
    #
    #	PARAMETERS:
    #		name
    #
    #	RETURN:
    ##################################################################################
    def setValue(self, value):
        """Set the value of this element."""

        self.value = value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	addAttribute()
    #
    #	DESCRIPTION:
    #		Set the value of this element.
    #
    #	PARAMETERS:
    #		attribute - an instance of the MyAttribute class
    #
    #	RETURN:
    ##################################################################################
    def addAttribute(self, attribute):
        """
        add the given attribute to this object.
        PARAMETERS:
            attribute - an instance of the MyAttribute class.
        """
        if isinstance(attribute, MyAttribute):
            self.attributes.append(attribute)
        else:
            self.logIt("pylib.XML.MyElement.addAttribute(): attribute is not an instance of pylib.XML.MyAttribute.\n")

    # Endif
    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getAttributeByName()
    #
    #	DESCRIPTION:
    #		Get the attribute by name
    #
    #	PARAMETERS:
    #		name - name of the attribute.
    #
    #	RETURN:
    #		An instance of pylib.XML.MyAttribute or None
    ##################################################################################
    def getAttributeByName(self, name):
        """
        Get the attribute by name.
        PARAMETERS:
            name - name of the attribute
        RETURN:
            An instance of the pylib.XML.MyAttribute or None
        """
        for attribute in self.attributes:
            if attribute.getName() == name:
                return attribute
        # Endif
        # Endfor
        return None

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getAllAttributes()
    #
    #	DESCRIPTION:
    #		Get the attribute by name
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		An array of all the pylib.XML.MyAttribute instances.
    ##################################################################################
    def getAllAttributes(self):
        """
        Get the attribute by name.
        PARAMETERS:
        RETURN:
            An array of all the pylib.XML.MyAttribute instances.
        """
        return self.attributes

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	logMe()
    #
    #	DESCRIPTION:
    #		Log myself to the logger.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #
    ##################################################################################
    def logMe(self):
        """
        Log myself to the logger.
        PARAMETERS:
        RETURN:
            Nothing.
        """
        self.logIt("pylib.XML.MyElement.logMe(): Element name=" + self.getName() + "\n")
        self.logIt("pylib.XML.MyElement.logMe(): Element value=" + self.getValue() + "\n")
        for attr in self.attributes:
            self.logIt("pylib.XML.MyElement.logMe(): \tAttribute name=" + attr.getName() + "\n")
            self.logIt("pylib.XML.MyElement.logMe(): \tAttribute value=" + attr.getValue() + "\n")

    # Endfor
    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	printMe()
    #
    #	DESCRIPTION:
    #		Log myself to the logger.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #
    ##################################################################################
    def printMe(self):
        """
        Log myself to the logger.
        PARAMETERS:
        RETURN:
            Nothing.
        """
        print(("pylib.XML.MyElement.printMe(): Element name=" + self.getName()))
        print(("pylib.XML.MyElement.printMe(): Element value=" + self.getValue()))
        for attr in self.attributes:
            print(("pylib.XML.MyElement.printMe(): \tAttribute name=" + attr.getName()))
            print(("pylib.XML.MyElement.printMe(): \tAttribute value=" + attr.getValue()))

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
    myLogger = MyLogger(LOGFILE="/tmp/MyElement.log", STDOUT=True, DEBUG=True)
    myObject = MyElement(myLogger, name="name", value="Denis value")
    myObject.logIt("main(): Hello world\n")
    myObject.debug("main(): Debug Hello world\n")
    print("name=" + myObject.getName())
    print("value=" + myObject.getValue())
    myObject.setName("bulltwinkie")
    myObject.setValue("real tasty")
    print("name=" + myObject.getName())
    print("value=" + myObject.getValue())

    for i in range(0, 10):
        myAttribute = MyAttribute(logger=myLogger, name="name" + str(i), value="value" + str(i))
        myObject.addAttribute(myAttribute)
    # Endfor
    for i in range(0, 10):
        myAttribute = myObject.getAttributeByName("name" + str(i))
        print("attr name=" + myAttribute.getName())
        print("attr value=" + myAttribute.getValue())
    # Endfor
    myAttrs = myObject.getAllAttributes()
    for attr in myAttrs:
        print(attr.getName())
        print(attr.getValue())
    myObject.closeMe();


##################################################################################
#	Enddef
##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
    main()
