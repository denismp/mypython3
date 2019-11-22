#!/usr/bin/env python
######################################################################################
##    FileThread.py
##
##    Python module to run postconfig on a host in a thread.
######################################################################################
##
##    MODIFICATION HISTORY:
##    DATE        WHOM                DESCRIPTION
##    02/12/2010    Denis M. Putnam        Created.
######################################################################################
import os, sys  # @UnusedImport
import re  # @UnusedImport
import socket  # @UnusedImport
import time  # @UnusedImport
import random
from subprocess import *  # @UnusedWildImport
from threading import Thread
from pylib.Utils.MyLogger import *  # @UnusedWildImport
from pylib.Utils.MyUtils import *  # @UnusedWildImport
from pylib.Utils.MySocket import *  # @UnusedWildImport
# import posixfile # this has been deprecated.
import fcntl
random.seed(time.localtime())


class FileThread(Thread):
    """FileThread class extends the Thread class to serve up a file in a thread."""

    ##################################################################################
    #    __init__()
    #
    #    DESCRIPTION:
    #        Class initializer.
    #
    #    PARAMETERS:
    #        See below.
    #
    #    RETURN:
    #        An instance of this class
    ##################################################################################
    def __init__(
            self,
            mySocketObj,
            socketConn,
            recvData,
            statusFile,
            threadName=None,
            logger=None
    ):
        """Class Initializer.
           PARAMETERS:
               mySocketObj   - An instance of the pylib.Utils.MySocket class.
               socketConn    - socket connect from accept() call.
               recvData      - data from socketConn.recv()
               statusFile    - File to store the results of the thread.
               threadName    - Optional thread name.
               logger        - instance of the MyLogger class.

           RETURN:
               An instance of this class
        """

        Thread.__init__(self, name=threadName)  # Initialize the super.
        self.logger = logger
        self.mySocketObj = mySocketObj
        self.socketConn = socketConn
        self.recvData = recvData
        self.statusFile = statusFile
        self.threadName = threadName
        self.msgNum = None
        self.status = True
        self.message = '\n'
        self.logMySelf()
        self.validate()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #    validate()
    #
    #    DESCRIPTION:
    #        Validate the parameters and calculated values.
    #
    #    PARAMETERS:
    #
    #    RETURN:
    #        True for valid.
    ##################################################################################
    def validate(self):
        """Validate the parameters and calculated values.
           PARAMETERS:

           RETURN:
               True for valid or False.
        """
        # rVal = False
        # return rVal
        return True

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #    logMySelf()
    #
    #    DESCRIPTION:
    #        Log myself.
    #
    #    PARAMETERS:
    #
    #    RETURN:
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
    #    logIt()
    #
    #    DESCRIPTION:
    #        Write a message to the log and possibly stdout.
    #
    #    PARAMETERS:
    #        msg - what you want to log.
    #
    #    RETURN:
    ##################################################################################
    def logIt(self, msg):
        """Write a message to the log and possibly stdout."""

        if (self.logger): self.logger.logIt(msg)

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #    debug()
    #
    #    DESCRIPTION:
    #        Write a message to the log and possibly stdout.
    #
    #    PARAMETERS:
    #        msg - what you want to log.
    #
    #    RETURN:
    #################################################################################
    def debug(self, msg):
        """Write a message to the log and possibly stdout."""

        if (self.logger): self.logger.debug(msg)

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #    closeMe()
    #
    #    DESCRIPTION:
    #        Closes this instance.
    #
    #    PARAMETERS:
    #
    #    RETURN:
    ##################################################################################
    def closeMe(self):
        """Closes this instance."""
        self.debug(__name__ + ".closeMe(): called.\n")
        # Endif

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #    __del__()
    #
    #    DESCRIPTION:
    #        Really closes this instance.
    #
    #    PARAMETERS:
    #
    #    RETURN:
    ##################################################################################
    def __del__(self):
        """Closes this instance."""
        # self.logIt( __name__ + ".__del__(): called.\n" )
        self.closeMe()

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #    appendMsg()
    #
    #    DESCRIPTION:
    #        Append a string to the self.message string.
    #
    #    PARAMETERS:
    #
    #    RETURN:
    ##################################################################################
    def appendMsg(self, msg):
        """Append a string to the self.message string."""
        # self.message += msg
        theTime = self.logger.mytime()
        # self.message += theTime + " " + str( msg )
        self.message = str(self.message) + str(theTime) + " " + str(msg)

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #    getFileData()
    #
    #    DESCRIPTION:
    #        Get the NNNN number from the recvData.
    #
    #    PARAMETERS:
    #
    #    RETURN:
    #        
    ##################################################################################
    def getMsgNumber(self):
        """Get the NNNN number from the recvData.
           PARAMETERS:

           RETURN:
               data - the data read from the file.
        """
        wData = self.recvData
        self.logIt(__name__ + ".getMsgNumber(): wData=" + str(wData) + "\n")
        msgNum = ""
        msgNum2 = None
        for i in range(0, len(str(wData))):
            if wData is None:
                break
            if str(wData[i]).isdigit():
                msgNum += str(wData[i])
            else:
                break
        if msgNum != "":
            msgNum2 = socket.ntohl(int(str(msgNum)))

        return msgNum2

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #    getFileData()
    #
    #    DESCRIPTION:
    #        Get the file data to be returned to the client.
    #
    #    PARAMETERS:
    #
    #    RETURN:
    #        
    ##################################################################################
    def getFileData(self):
        """Get the file data to be returned to the client.  The file is assummed to bi in the 
           current working directory.  The file name will be name NNNN.txt where NNNN is
           the first 4 bytes of the received data.  The rest of the received data is ignored.
           PARAMETERS:

           RETURN:
               data - the data read from the file.
        """
        # fileName = "./0000.txt"
        self.logIt(__name__ + ".getFileData(): data=" + str(self.recvData) + "\n")
        msgNum = self.getMsgNumber()
        if msgNum is None:
            return ""
        # fileName    = "%-04.4d" % (msgNum )   + ".txt"
        fileName = "./files/" + str(msgNum)
        self.msgNum = msgNum
        self.logIt(__name__ + ".getFileData(): fileName=" + fileName + "\n")
        try:
            FH = open(fileName, "r")
            data = FH.read()
            FH.close()
        except IOError as inst:
            self.logIt(__name__ + ".getFileData(): Unable to open " + fileName + " for write." + " => " + str(
                inst.errno) + ":" + str(inst.strerror) + "\n")
            raise
        # Endtry
        return data

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #    updateCounts()
    #
    #    DESCRIPTION:
    #        Update the counts file.
    #
    #    PARAMETERS:
    #
    #    RETURN:
    #        
    ##################################################################################
    def updateCounts(self):
        """Update the counts file.
           PARAMETERS:

           RETURN:
               
        """
        found = False
        fileName = "counts"
        if not os.access(fileName, os.F_OK):
            try:
                TFH = open(fileName, "w")
                TFH.close()
            except IOError as inst:  # @UnusedVariable
                self.logIt(__name__ + ".updateCounts(): Unable to open " + fileName + " for write." + " => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
                raise

        self.logIt(__name__ + ".updateCounts(): fileName=" + fileName + "\n")
        try:
            FH = open(fileName, "rb+")
            # FH = posixfile.open(fileName, "rb+") # posixfile has been deprecated.
            # FH.lock('w|')
            data = None
            while 1:
                data = str(FH.readline())
                if data is None or data == "": break
                data = re.sub("\n", "", data)
                self.debug(__name__ + ".updateCounts(): data is " + str(data) + "\n")
                ms = str(self.msgNum) + "="
                self.debug(__name__ + ".updateCounts(): ms is" + str(ms) + "\n")
                if re.search(ms, data):
                    found = True
                    self.debug(__name__ + ".updateCounts(): DEBUG0.5\n")
                    break
            self.debug(__name__ + ".updateCounts(): DEBUG1\n")
            if data and found:
                self.debug(__name__ + ".updateCounts(): DEBUG2\n")
                eloc = FH.tell()
                self.debug(__name__ + ".updateCounts(): eloc=" + str(eloc) + "\n")
                sloc = eloc - len(data) - 1
                self.debug(__name__ + ".updateCounts(): sloc=" + str(sloc) + "\n")
                FH.seek(sloc, os.SEEK_SET)
                cloc = FH.tell()
                self.debug(__name__ + ".updateCounts(): cloc=" + str(cloc) + "\n")
                myList = list()
                myList = data.split('=')
                icount = int(myList[1]) + 1
                FH.write(str(self.msgNum) + "=" + str(icount) + "\n")
            else:
                self.debug(__name__ + ".updateCounts(): DEBUG3\n")
                FH.write(str(self.msgNum) + "=1" + "\n")
            FH.lock('u')
            FH.close()
        except IOError as inst:  # @UnusedVariable
            pass
            # self.logIt( __name__ + ".updateCounts(): Unable to open " + fileName + " for write."  + " => " + str( inst.errno ) + ":" + str( inst.strerror ) + "\n" )
        # Endtry

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #    run()
    #
    #    DESCRIPTION:
    #        Override the Thread run() method with what we want to do.
    #
    #    PARAMETERS:
    #
    #    RETURN:
    #        
    ##################################################################################
    def run(self):
        """Override the Thread run() method with what we want to do.
           PARAMETERS:

           RETURN:
        """
        self.debug(__name__ + ".run(): self.threadName=" + str(self.threadName) + "\n")
        self.debug(__name__ + ".run(): self.statusFile=" + str(self.statusFile) + "\n")
        self.debug(__name__ + ".run(): self.recvData=" + str(self.recvData) + "\n")
        self.debug(__name__ + ".run(): self.socketConn=" + str(self.socketConn) + "\n")

        status = True
        data = self.getFileData()
        self.mySocketObj.serverSend(self.socketConn, data)
        if self.socketConn: self.socketConn.close()
        # self.updateCounts()
        self.status = status
        if status:
            self.appendMsg(__name__ + ".run(): Completed successfully for " + str(self.threadName) + "\n")
        else:
            self.appendMsg(__name__ + ".run(): Failed for " + str(self.threadName) + "\n")
        # Endif

    ##################################################################################
    # Enddef
    ##################################################################################

    ##################################################################################
    #   terminate()
    #
    #   DESCRIPTION:
    #       Terminate this thread.
    #
    #   PARAMETERS:
    #
    #   RETURN:
    ##################################################################################
    def terminate(self, msg=None):
        """Terminate this thread."""
        if msg is not None: self.logIt(__name__ + ".terminate(): " + str(msg) + '\n')
        sys.exit()
    ##################################################################################
    # Enddef
    ##################################################################################


######################################################################################
# Endclass
######################################################################################

#########################################################################
#    For testing.
#########################################################################
def main():
    myLogger = MyLogger(LOGFILE="/tmp/FileThread.log", STDOUT=True, DEBUG=True)
    mySocketObj = MySocket(port=50007, logger=myLogger)
    mySocketObj.bindAndListen()
    conn, data = mySocketObj.serverRead(1, packetSize=2048)

    statusFile = '/tmp/mystatus.txt'

    threadList = []
    for mythread in range(0, 1):
        current = FileThread(
            mySocketObj,
            conn,
            data,
            statusFile + str(mythread + 1),
            threadName='thread_jobid_' + str(mythread) + '_host' + str(mythread + 1),
            logger=myLogger
        )
        threadList.append(current)
        current.start()
    # Endfor

    ################################
    #    Join on all the threads.
    ################################
    for mythread in threadList:
        mythread.join()
        myLogger.logIt("main(): " + str(mythread) + "\n")
        myLogger.logIt("main(): " + str(mythread.message) + '\n')
        mythread.closeMe()
    # Endfor

    ##################################################################################
    # Enddef
    ##################################################################################


######################################################################################
#   End
######################################################################################
if __name__ == "__main__":
    main()
