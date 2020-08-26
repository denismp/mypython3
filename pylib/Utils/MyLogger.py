#!/usr/bin/env python
######################################################################################
##	MyLogger.py
##
##	Python module with some useful logging functions.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	07/17/2009	Denis M. Putnam		Created.
######################################################################################
import time


# False = 0
# True = 1

class MyLogger:
    """MyLogger class that provides some useful logging methods."""

    ##################################################################################
    #	__init__()
    #
    #	DESCRIPTION:
    #		Class initializer.
    #
    #	PARAMETERS:
    #		LOGFILE - Name of the log file(default is /dev/null)
    #		MODE	- overwrite|append
    #		STDOUT	- Also write to stdout flag(default is False)
    #		DEBUG	- Turn on verbose debugging(defalut is False)
    #
    #	RETURN:
    #		An instance of this class
    ##################################################################################
    def __init__(self, LOGFILE="/dev/null", MODE="overwrite", STDOUT=False, DEBUG=False):
        """Class Initializer.
           PARAMETERS:
               LOGFILE - Name of the log file(default is /dev/null)
               MODE	- overwrite|append
               STDOUT	- Also write to stdout flag(default is False)
               DEBUG	- Turn on verbose debugging(defalut is False)
        """
        self.LOGFILE = LOGFILE
        self.MODE = MODE
        self.STDOUT = STDOUT
        self.DEBUG = DEBUG

        if (MODE != "overwrite" or MODE != "append"): __MODE = "overwrite"
        try:
            if (MODE == "overwrite"):
                self.__FH = open(LOGFILE, 'w')
            else:
                self.__FH = open(LOGFILE, 'w+')
        except IOError as inst:
            print(("Unable to open " + str(LOGFILE) + " => " + str(inst.errno) + ":" + str(inst.strerror)), end=' ')
            raise

    #	Enddef

    ##################################################################################
    #	getLogHandle()
    #
    #	DESCRIPTION:
    #		Get the logger file handle
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		logger file handle
    ##################################################################################
    def getLogHandle(self):
        """Get the logger file handle."""
        return self.__FH

    #	Enddef

    ##################################################################################
    #	mytime()
    #
    #	DESCRIPTION:
    #		Get the current time.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		curent time
    ##################################################################################
    def mytime(self):
        """Get the current time as YYYYMMDD_HH:MM:SS format."""
        mytime = time.localtime()
        mytimestr = time.strftime("%Y%m%d-%H:%M:%S", mytime)
        return mytimestr

    #	Enddef

    ##################################################################################
    #	mktime()
    #
    #	DESCRIPTION:
    #		Get the current time.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		curent time
    ##################################################################################
    def mktime(self, secs):
        """Get the current time as YYYYMMDD_HH:MM:SS format."""
        mytime = time.localtime(secs)
        mytimestr = time.strftime("%Y%m%d-%H:%M:%S", mytime)
        return mytimestr

    #	Enddef

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
        theTime = self.mytime()
        myMsg = theTime + " " + msg
        try:
            self.__FH.write(myMsg)
            self.__FH.flush()
        except IOError as inst:
            print(("Unable to write to " + str(self.LOGFILE) + " => " + str(inst.errno) + ":" + str(inst.strerror)))
        else:
            if (self.STDOUT):
                print((myMsg), end=' ')

    #	Enddef

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
        if (self.DEBUG):
            theTime = self.mytime()
            myMsg = theTime + " " + msg
            try:
                self.__FH.write(myMsg)
                self.__FH.flush()
            except IOError as inst:
                print(("Unable to write to " + str(self.LOGFILE) + " => " + str(inst.errno) + ":" + str(inst.strerror)))
            else:
                if (self.STDOUT):
                    print((myMsg), end=' ')

    #	Enddef

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
        try:
            self.__FH.close()
        except IOError as inst:
            print(("Unable to close " + str(self.LOGFILE) + " => " + str(inst.errno) + ":" + str(inst.strerror)))
            raise

    #	Enddef

    ##################################################################################
    #	__del__()
    #
    #	DESCRIPTION:
    #		Destructor
    #
    #	PARAMETERS:
    #
    #	RETURN:
    ##################################################################################
    def __del__(self):
        """Closes this instance."""
        try:
            self.closeMe()
        except IOError as inst:
            print(inst.strerror)
            raise
#	Enddef

#	Endclass


def main_logger():
    myObject = MyLogger(LOGFILE="/tmp/denis.log", DEBUG=True, STDOUT=True)
    # myObject = MyLogger(LOGFILE="/nfs/dist/dmp/amp/update/UAT/DEV/denis.log", DEBUG=True, STDOUT=True);
    print((myObject.mytime()))
    myObject.logIt("main(): Hello world\n")
    myObject.debug("main(): Debug Hello world\n")
    myObject.closeMe()


#	Enddef

#########################################
#   End
#########################################
if __name__ == "__main__":
    main_logger()
