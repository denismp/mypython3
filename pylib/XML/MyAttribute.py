#!/bin/env python
######################################################################################
##	MyAttribute.py
##
##	Jython module to contains a XML attribute.
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


class MyAttribute:
    """MyAttribute class contains name/value pair for a singleton XML attribute."""

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

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	getName()
    #
    #	DESCRIPTION:
    #		Get the name of this attribute.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		name
    ##################################################################################
    def getName(self):
        """Get the name of this attribute."""

        return self.name

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	setName()
    #
    #	DESCRIPTION:
    #		Set the name of this attribute.
    #
    #	PARAMETERS:
    #		name
    #
    #	RETURN:
    #		name
    ##################################################################################
    def setName(self, name):
        """Set the name of this attribute."""

        self.name = name

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getValue()
    #
    #	DESCRIPTION:
    #		Get the name of this attribute.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		name
    ##################################################################################
    def getValue(self):
        """Get the value of this attribute."""

        return self.value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	setValue()
    #
    #	DESCRIPTION:
    #		Set the value of this attribute.
    #
    #	PARAMETERS:
    #		name
    #
    #	RETURN:
    ##################################################################################
    def setValue(self, value):
        """Set the value of this attribute."""

        self.value = value

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
    myLogger = MyLogger(LOGFILE="/tmp/MyAttribute.log", STDOUT=True, DEBUG=True)
    myObject = MyAttribute(myLogger, name="name", value="Denis value")
    myObject.logIt("main(): Hello world\n")
    myObject.debug("main(): Debug Hello world\n")
    print("name=" + myObject.getName())
    print("value=" + myObject.getValue())
    myObject.setName("bulltwinkie")
    myObject.setValue("real tasty")
    print("name=" + myObject.getName())
    print("value=" + myObject.getValue())
    myObject.closeMe();


##################################################################################
#	Enddef
##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
    main()
