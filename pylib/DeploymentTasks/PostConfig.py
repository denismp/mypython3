#!/usr/bin/env python
######################################################################################
##	PostConfig.py
##
##	Python module run postconfig on all the hosts.
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
from pylib.MyThreads.PostConfigThread import *


class PostConfig():
    """PostConfig class to run postconfig on all the hosts."""

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
               mne	          - Mneumonic.
               domain         - domain.
               hostDict       - List of hosts to work on and their associated arguments if any.
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
    #	postConfigure()
    #
    #	DESCRIPTION:
    #		Configure the MNE on all the hosts.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #
    ##################################################################################
    def postConfigure(self, timeout=None):
        """Configure the MNE on all the hosts.
           PARAMETERS:

           RETURN:
        """
        self.debug(__name__ + ".postConfigure(): timeout=" + str(timeout) + "\n")
        self.debug(__name__ + ".postConfigure(): self.jobid=" + str(self.jobid) + "\n")
        self.debug(__name__ + ".postConfigure(): self.ampid=" + str(self.ampid) + "\n")
        self.debug(__name__ + ".postConfigure(): self.mne=" + str(self.mne) + "\n")
        self.debug(__name__ + ".postConfigure(): self.domain=" + str(self.domain) + "\n")
        self.debug(__name__ + ".postConfigure(): self.statusFileHome=" + str(self.statusFileHome) + "\n")

        threadList = []
        for (host, args) in self.hostDict.items():
            statusFile = str(self.statusFileHome) + '/runPOSTCONFIG.' + str(self.domain) + '.' + str(host)
            current = PostConfigThread(
                self.jobid,
                self.ampid,
                host,
                statusFile,
                self.mne,
                self.domain,
                threadName=str(self.jobid) + '_' + str(self.ampid) + '_' + str(self.domain) + '_' + str(host),
                logger=self.logger
            )
            threadList.append(current)
            current.start()
        # Endfor

        ################################
        #	Join on all the threads.
        ################################
        for mythread in threadList:
            mythread.join(timeout)
            if mythread.isAlive():
                self.status = False
                self.appendMsg(__name__ + ".postConfigure(): " + str(mythread) + " timed out.\n")
                self.logIt(__name__ + ".postConfigure(): " + str(mythread) + " timed out.\n")
            # Endif
            self.logIt(__name__ + ".postConfigure(): " + str(mythread) + "\n")
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
    myLogger = MyLogger(LOGFILE="/tmp/PostConfig.log", STDOUT=True, DEBUG=True)

    threadList = []

    hostDict = dict()
    for mythread in range(0, 3):
        hostName = 'host' + str(mythread)
        hostDict[hostName] = ['arg1', 'arg2', 'arg3']
    # Endfor

    jobid = 'SomeAutoSysId'
    ampid = 'SomeAmpId'
    mne = 'DMP'
    statusFileHome = '/tmp'
    myPostConfig = PostConfig(
        jobid,
        ampid,
        mne,
        'MYDOMAIN',
        hostDict,
        statusFileHome,
        logger=myLogger
    )
    myPostConfig.postConfigure(timeout=5.0)
    myLogger.logIt('main(): ' + str(myPostConfig.message))

    myPostConfig.closeMe()


##################################################################################
# Enddef
##################################################################################

######################################################################################
#   End
######################################################################################
if __name__ == "__main__":
    main()
