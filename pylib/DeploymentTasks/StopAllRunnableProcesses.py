#!/usr/bin/env python
######################################################################################
##	StopAllRunnableProcesses.py
##
##	Python module stops all runnable processes based on a process dictionary.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	02/09/2010	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
import time
import random
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from pylib.MyThreads.StopRunnableProcessThread import *


class StopAllRunnableProcesses():
    """StopAllRunnableProcesses class to stop remote runnable processes."""

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
            domain,
            mne,
            statusFile,
            processDict,
            logger=None
    ):
        """Class Initializer.
           PARAMETERS:
               jobid         - autosys jobid.
               ampid         - AMP ID.
               domain        - Domain.
               mne	         - Mneumonic.
               statusFile	 - File to store the results of the threads.
               processDict	 - Dictionary of processes to stop keyed by the host name.
               logger        - instance of the MyLogger class.

           RETURN:
               An instance of this class
        """
        self.logger = logger
        self.jobid = jobid
        self.ampid = ampid
        self.domain = domain
        self.mne = mne
        self.statusFile = statusFile
        self.status = False
        self.message = "\n"
        self.processDict = processDict
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
    #		Append the given message to the message buffer.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #
    ##################################################################################
    def appendMsg(self, msg):
        """Append the given message to the message buffer.
           PARAMETERS:
               msg -- string to append to the message buffer.

           RETURN:
        """
        self.message += str(msg)

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	stopProcesses()
    #
    #	DESCRIPTION:
    #		Stop all the processes on all the hosts in the process dictionary.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #
    ##################################################################################
    def stopProcesses(self, timeout=None):
        """Stop all the processes on all the hosts in the process dictionary.
           PARAMETERS:
               timeout -- number of seconds to allow the process to complete.  Use a float value.

           RETURN:
               True if successful.
        """
        self.debug(__name__ + ".stopProcesses(): timeout=" + str(timeout) + "\n")
        self.debug(__name__ + ".stopProcesses(): self.jobid=" + str(self.jobid) + "\n")
        self.debug(__name__ + ".stopProcesses(): self.ampid=" + str(self.ampid) + "\n")
        self.debug(__name__ + ".stopProcesses(): self.domain=" + str(self.domain) + "\n")
        self.debug(__name__ + ".stopProcesses(): self.mne=" + str(self.mne) + "\n")
        self.debug(__name__ + ".stopProcesses(): self.processDict=" + str(self.processDict) + "\n")
        self.debug(__name__ + ".stopProcesses(): self.statusFile=" + str(self.statusFile) + "\n")

        rVal = True
        threadList = []
        for (host, pList) in self.processDict.items():
            threadName = str(self.mne) + '_' + str(self.domain) + '_' + str(self.jobid) + '_' + str(
                self.ampid) + '_' + str(host)
            current = StopRunnableProcessThread(
                self.jobid,
                self.ampid,
                host,
                self.domain,
                self.statusFile,
                self.mne,
                pList,
                threadName=threadName,
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
                self.logIt(__name__ + ".stopProcesses(): " + str(mythread) + "timed out.\n")
                self.appendMsg(__name__ + ".stopProcesses(): " + str(mythread) + "timed out.\n")
            # Endif
            self.logIt(__name__ + ".stopProcesses(): " + str(mythread) + "\n")
            rc = mythread.status
            if not rc:
                self.status = False
            self.appendMsg(__name__ + ".stopProcesses(): " + str(mythread.message))
            mythread.closeMe()
        # Endfor
        return rVal

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
    myLogger = MyLogger(LOGFILE="/tmp/StopAllRunnableProcesses.log", STDOUT=True, DEBUG=True)

    threadList = []
    processDict = dict()
    for mythread in range(0, 3):
        hostName = 'host' + str(mythread)
        processList = ['comp' + str(mythread + 1), 'comp' + str(mythread + 2), 'comp' + str(mythread + 3)]
        processDict[hostName] = processList
    # Endfor

    jobid = 'SomeAutoSysId'
    ampid = 'SomeAmpId'
    mne = 'DMP'
    statusFile = '/tmp/stop_all_runable_processes.MYDOMAIN'
    myStopAllRunnableProcesses = StopAllRunnableProcesses(
        jobid,
        ampid,
        'MYDOMAIN',
        mne,
        statusFile,
        processDict,
        logger=myLogger
    )
    rc = myStopAllRunnableProcesses.stopProcesses()
    msgs = myStopAllRunnableProcesses.message
    myLogger.logIt("main(): msgs=" + str(msgs) + "\n")

    myStopAllRunnableProcesses.closeMe()


##################################################################################
# Enddef
##################################################################################

######################################################################################
#   End
######################################################################################
if __name__ == "__main__":
    main()
