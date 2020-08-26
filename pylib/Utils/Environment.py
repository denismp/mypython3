#!/usr/bin/env python
######################################################################################
##	Environment.py
##
##	Python module deals with Environment.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	09/21/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *


class Environment():
    """
    Environment class that deals with the environment.
    When this class is instantiated, it sucks in the entire user environment.
    This makes all the environment variable available via the python dot
    notation.  Setting new environment variables also makes them available.
    """

    ##################################################################################
    #	__init__()
    #
    #	DESCRIPTION:
    #		Class initializer.
    #
    #	PARAMETERS:
    #		logger	    - instance of the pylib.Utils.MyLogger class.
    #
    #	RETURN:
    #		An instance of this class
    ##################################################################################
    def __init__(
            self,
            logger=None
    ):
        """Class Initializer.
           PARAMETERS:
               logger   - instance of the pylib.Utils.MyLogger class.

           RETURN:
               An instance of this class
        """
        self.logger = logger
        self.utils = MyUtils()
        self.getAllTheEnvironment()

    # self.logMySelf()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getEnvironmentVariable()
    #
    #	DESCRIPTION:
    #		Get an environment variable
    #
    #	PARAMETERS:
    #       name is the name of the environment variable.
    #       default is the default value of the environment variable if it is not set.
    #
    #	RETURN:
    #		value
    ##################################################################################
    def getEnvironmentVariable(self, name=None, default=''):
        """Get the environment variable value.
           PARAMETERS:
               name is the name of the environment variable.
               default is the default value of the environment variable if it is not set.

           RETURN:
               value
        """
        if name is None: return None

        value = default
        try:
            value = os.environ[name]
        except KeyError as e:
            self.logIt("pylib.Utils.Environment.getEnvironmentVariable(): Unable to get " + str(e) + ".  Using " + str(
                default) + ".\n")
            value = default
        # Endtry
        setattr(self, name, value)
        return value

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	setEnvironmentVariable()
    #
    #	DESCRIPTION:
    #		Set an environment variable
    #
    #	PARAMETERS:
    #       name is the name of the environment variable.
    #       value is the value of the environment variable.
    #
    #	RETURN:
    ##################################################################################
    def setEnvironmentVariable(self, name=None, value=None):
        """Set the environment variable value.
           PARAMETERS:
               name is the name of the environment variable.
               value is the value of the environment variable.

           RETURN:
        """
        if name is None: return
        if value is None:
            self.logIt("pylib.Utils.Environment.setEnvironmentVariable(): value=" + str(
                value) + ".  Environment variable " + str(name) + " is not set.\n")
            return
        # Endif

        try:
            os.environ[name] = value
            setattr(self, name, value)
        except KeyError as e:
            self.logIt("pylib.Utils.Environment.setEnvironmentVariable(): Unable to set " + str(e) + ".\n")

    # Endtry

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	getAllTheEnvironment()
    #
    #	DESCRIPTION:
    #		Get all the environment variables and make them part of this object.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    ##################################################################################
    def getAllTheEnvironment(self):
        """Get all the environment variables and make them part of this object.
        PARMETERS:
        RETURN:
        """

        myEnv = os.environ
        for env in list(myEnv.keys()):
            setattr(self, env, myEnv.get(env))

    # Endfor

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	logEnv()
    #
    #	DESCRIPTION:
    #		Log the environment.
    #
    #	PARAMETERS:
    #		debugOnly
    #
    #	RETURN:
    ##################################################################################
    def logEnv(self, debugOnly=True):
        """Log the environment.
        PARMETERS:
            debugOnly is either True or False.  A value of True will only log if the
            logger's debug flag is set.
        """

        myEnv = os.environ
        for env in list(myEnv.keys()):
            if (debugOnly == True):
                self.debug("pylib.Utils.Environment.logEnv(): " + str(env) + "=" + str(myEnv.get(env)) + "\n")
            else:
                self.logIt("pylib.Utils.Environment.logEnv(): " + str(env) + "=" + str(myEnv.get(env)) + "\n")

    # Endif

    # Endfor

    ##################################################################################
    # Enddef
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

        myAttrs = dir(self)
        for attr in myAttrs:
            if re.search('__doc__', attr): continue
            if re.search('__module__', attr): continue
            if re.search('bound method', str(getattr(self, attr))): continue
            if re.search('instance', str(getattr(self, attr))): continue
            if (debugOnly == True):
                self.debug("pylib.Utils.Environment.logMySelf(): " + str(attr) + "=" + str(getattr(self, attr)) + "\n")
            else:
                self.logIt("pylib.Utils.Environment.logMySelf(): " + str(attr) + "=" + str(getattr(self, attr)) + "\n")

    # Endif

    # Endfor
    # self.logEnv( debugOnly=debugOnly )

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

#####################################################################################
# Endclass
#####################################################################################

#########################################################################
#	For testing.
#########################################################################
def main_environment():
    myLogger = MyLogger(LOGFILE="/tmp/Environment.log", STDOUT=True, DEBUG=False)
    myObject = Environment(logger=myLogger)
    myObject.logMySelf(debugOnly=False)

    myObject.closeMe()


##################################################################################
# Enddef
##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
    main_environment()
