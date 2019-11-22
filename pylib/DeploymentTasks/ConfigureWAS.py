#!/usr/bin/env python
######################################################################################
##	ConfigureWAS.py
##
##	Python module configures WAS on all the hosts.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	02/11/2010	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
import time
import random
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.MyThreads.ConfigureWASThread import *


class ConfigureWAS():
    """ConfigureWAS class to configure WAS on all the hosts."""

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
            jobid,
            ampid,
            mne,
            domain,
            hostDict,
            statusFileHome,
            logger=None
    ):
        """Class Initializer.
           PARAMETERS:
               jobid          - autosys jobid.
               ampid          - AMP ID.
               mne            - Mneumonic.
               domain         - domain.
               hostDict       - List of hosts to work on along with their components.
               statusFileHome - File to store the results of the thread.
               logger         - instance of the MyLogger class.

           RETURN:
               An instance of this class
        """
        self.logger = logger
        self.jobid = jobid
        self.ampid = ampid
        self.mne = mne
        self.domain = domain
        self.statusFileHome = statusFileHome
        self.hostDict = hostDict
        self.status = True
        self.message = '\n'
        self.logMySelf()
        self.validate()

    ##################################################################################
    # Enddef
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
        # return rVal
        return True

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
            try:
                if re.search('__doc__', attr): continue
                if re.search('__module__', attr): continue
                if re.search('bound method', str(getattr(self, attr))): continue
                if re.search('instance', str(getattr(self, attr))): continue
                if (debugOnly == True):
                    self.debug(__name__ + ".logMySelf(): " + str(attr) + "=" + str(getattr(self, attr)) + "\n")
                else:
                    self.logIt(__name__ + ".logMySelf(): " + str(attr) + "=" + str(getattr(self, attr)) + "\n")
            # Endif
            except AttributeError as e:
                continue

    # Endtry

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
    #################################################################################
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
        self.debug(__name__ + ".closeMe(): called.\n")

    # Endif
    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	__del__()
    #
    #	DESCRIPTION:
    #		Really closes this instance.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    ##################################################################################
    def __del__(self):
        """Closes this instance."""
        # self.logIt( __name__ + ".__del__(): called.\n" )
        self.closeMe()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	appendMsg()
    #
    #	DESCRIPTION:
    #		Append a string to the self.message string.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    ##################################################################################
    def appendMsg(self, msg):
        """Append a string to the self.message string."""
        self.message += msg

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	configureWAS()
    #
    #	DESCRIPTION:
    #		Configure WAS on all the hosts.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #
    ##################################################################################
    def configureWAS(self, timeout=None):
        """Configure WAS on all the hosts.
           PARAMETERS:

           RETURN:
        """
        self.debug(__name__ + ".configureWAS(): timeout=" + str(timeout) + "\n")
        self.debug(__name__ + ".configureWAS(): self.jobid=" + str(self.jobid) + "\n")
        self.debug(__name__ + ".configureWAS(): self.ampid=" + str(self.ampid) + "\n")
        self.debug(__name__ + ".configureWAS(): self.mne=" + str(self.mne) + "\n")
        self.debug(__name__ + ".configureWAS(): self.domain=" + str(self.domain) + "\n")
        self.debug(__name__ + ".configureWAS(): self.hostDict=" + str(self.hostDict) + "\n")
        self.debug(__name__ + ".configureWAS(): self.statusFileHome=" + str(self.statusFileHome) + "\n")

        threadList = []
        for (host, componentList) in self.hostDict.items():
            for component in componentList:
                statusFile = str(self.statusFileHome) + '/configureWAS.' + str(self.domain) + '.' + str(
                    host) + '.' + str(component)
                current = ConfigureWASThread(
                    self.jobid,
                    self.ampid,
                    host,
                    statusFile,
                    self.mne,
                    component,
                    threadName=str(self.jobid) + '_' + str(self.ampid) + '_' + str(host) + '_' + str(component),
                    logger=self.logger
                )
                threadList.append(current)
                current.start()
        # Endfor
        # Endfor

        ################################
        #	Join on all the threads.
        ################################
        for mythread in threadList:
            mythread.join(timeout)
            if mythread.isAlive():
                self.status = False
                self.appendMsg(__name__ + ".configureWAS(): " + str(mythread) + " timed out.\n")
                self.logIt(__name__ + ".configureWAS(): " + str(mythread) + " timed out.\n")
            # Endif
            self.logIt(__name__ + ".configureWAS(): " + str(mythread) + "\n")
            mythread.closeMe()
# Endfor

##################################################################################


# Enddef
##################################################################################

######################################################################################
# Endclass
######################################################################################

#########################################################################
#	For testing.
#########################################################################
def main():
    myLogger = MyLogger(LOGFILE="/tmp/ConfigureWAS.log", STDOUT=True, DEBUG=True)

    threadList = []

    hostDict = dict()
    for mythread in range(0, 3):
        hostName = 'host' + str(mythread)
        hostDict[hostName] = ['comp1', 'comp2', 'comp3']
    # Endfor

    jobid = 'SomeAutoSysId'
    ampid = 'SomeAmpId'
    mne = 'DMP'
    # statusFileHome	= '/tmp/stop_all_runable_processes.MYDOMAIN'
    statusFileHome = '/tmp'
    myConfigureWAS = ConfigureWAS(
        jobid,
        ampid,
        mne,
        'MYDOMAIN',
        hostDict,
        statusFileHome,
        logger=myLogger
    )
    myConfigureWAS.configureWAS(timeout=5.0)
    myLogger.logIt('main(): ' + str(myConfigureWAS.message))

    myConfigureWAS.closeMe()


##################################################################################
# Enddef
##################################################################################

######################################################################################
#   End
######################################################################################
if __name__ == "__main__":
    main()
