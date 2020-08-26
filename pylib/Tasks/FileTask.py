#!/usr/bin/env python
######################################################################################
##	FileTask.py
##
##	Python module run FileTask.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	03/31/2011	Denis M. Putnam		Created.
######################################################################################
import os, sys  # @UnusedImport
import re  # @UnusedImport
import socket  # @UnusedImport
import time  # @UnusedImport
import random  # @UnusedImport
from pylib.Utils.MyLogger import MyLogger  # @UnusedWildImport
from pylib.Utils.MyUtils import MyUtils  # @UnusedWildImport
from pylib.MyThreads.FileThread import FileThread  # @UnusedWildImport
from pylib.Utils.MySocket import MySocket


class FileTask():
    """FileTask class to run FileThreads."""

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
            port=50007,
            statusFileHome='/tmp',
            logger=None
    ):
        """Class Initializer.
           PARAMETERS:
               port           - port number to listen on.
               statusFileHome - home directory of the status file.
               logger         - instance of the MyLogger class.

           RETURN:
               An instance of this class
        """
        self.logger = logger
        self.port = port
        self.statusFileHome = statusFileHome
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
                # if re.search('__doc__', attr): continue
                # if re.search('__module__', attr): continue
                # if re.search('bound method', str(getattr(self, attr))): continue
                # if re.search('instance', str(getattr(self, attr))): continue
                if (debugOnly == True):
                    self.debug(__name__ + ".logMySelf(): " + str(attr) + "=" + str(getattr(self, attr)) + "\n")
                else:
                    self.logIt(__name__ + ".logMySelf(): " + str(attr) + "=" + str(getattr(self, attr)) + "\n")
            # Endif
            except AttributeError as e:  # @UnusedVariable
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
        # self.message += msg
        self.message = str(self.message) + str(msg)

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #	fileTask()
    #
    #	DESCRIPTION:
    #		Run the FileThread for all requests.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #
    ##################################################################################
    def fileTask(self, timeout=None):
        """Run the FileThread for all requests.
           PARAMETERS:
               timeout -- number of seconds to allow the thread to complete.  Use a float value.

           RETURN:
               True if successful.
        """
        self.debug(__name__ + ".fileTask(): timeout=" + str(timeout) + "\n")
        self.debug(__name__ + ".fileTask(): self.statusFileHome=" + str(self.statusFileHome) + "\n")
        threadHash = dict()
        myThreadName = "thread"
        count = 0
        mySocketObj = MySocket(port=self.port, logger=self.logger)
        mySocketObj.bindAndListen()

        while True:
            conn, data = mySocketObj.serverRead(16, packetSize=2048)

            currentThreadName = myThreadName + str(count)
            statusFile = str(self.statusFileHome) + '/runFileTask.' + currentThreadName
            current = FileThread(
                mySocketObj,
                conn,
                data,
                statusFile,
                threadName=currentThreadName,
                logger=self.logger
            )
            threadHash[currentThreadName] = current

            current.start()
            count += 1

            ################################
            #	Join on all the threads.
            ################################
            for (tname, mythread) in list(threadHash.items()):
                mythread.join(timeout)
                if mythread.isAlive():
                    self.status = False
                    self.logIt(__name__ + ".fileTask(): " + str(mythread) + "timed out.\n")
                    self.appendMsg(__name__ + ".fileTask(): " + str(mythread) + "timed out.\n")
                # Endif
                self.logIt(__name__ + ".fileTask(): " + str(mythread) + "\n")
                rc = mythread.status
                if not rc:
                    self.status = False
                self.appendMsg(__name__ + ".fileTask(): " + str(mythread.message))
                mythread.closeMe()
                if threadHash[tname]: del threadHash[tname]
        # Endfor
        # Endwhile

        return self.status

##################################################################################


# Enddef
##################################################################################

######################################################################################
# Endclass
######################################################################################

#########################################################################
#	For testing.
#########################################################################
def main_file_task():
    myLogger = MyLogger(LOGFILE="/tmp/FileTask.log", STDOUT=True, DEBUG=True)

    statusFileHome = '/tmp'
    myFileTask = FileTask(
        port=50007,
        statusFileHome=statusFileHome,
        logger=myLogger
    )
    myFileTask.fileTask(timeout=None)
    myLogger.logIt('main(): ' + str(myFileTask.message))


# myFileTask.closeMe()

##################################################################################
# Enddef
##################################################################################

######################################################################################
#   End
######################################################################################
if __name__ == "__main__":
    main_file_task()
