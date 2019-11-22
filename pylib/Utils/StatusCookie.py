#!/usr/bin/env python
######################################################################################
##	StatusCookie.py
##
##	Python module that provides methods for handling status cookies.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	08/19/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys, re
# sys.path.append( '/nfs/home4/dmpapp/appd4ec/python' )
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *


class StatusCookie:
    """StatusCookie class that provides methods for handling status cookies.
       Typically the status cookie is a file something like:
       /nfs/dist/dmp/amp/update/UAT/QUAL/QAMP_UAT0000000_090504130000i/email/notice.dideploy11.gen_giblets.py.31545.failed
    """

    ##################################################################################
    #	__init__()
    #
    #	DESCRIPTION:
    #		Class initializer.
    #
    #	PARAMETERS:
    #		jobname - used to calculate the directory of the cookie files.
    #		logger	- instance of the pylib.Utils.MyLogger class
    #
    #	RETURN:
    #		An instance of this class
    ##################################################################################
    def __init__(self, jobname="QAMP_UAT0000000_090504130000i", logger=None):
        """Class Initializer.
           PARAMETERS:
               jobname - used to calculate the directory of the cookie files.
               logger  - instance of the pylib.Utils.MyLogger class
        """
        self.jobname = jobname
        self.email_dir = self.mkEmailDir(jobname)
        self.work_dir = self.mkWorkDir(jobname)
        self.logger = logger
        self.utils = MyUtils()
        self.error_msg = ""

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	mkEmailDir()
    #
    #	DESCRIPTION:
    #		Make the email_dir from the jobname
    #		DAMP_UAT0000000_090504130000i - 29 chars
    #
    #	PARAMETERS:
    #		jobname
    #
    #	RETURN:
    #		email_dir
    ##################################################################################
    def mkEmailDir(self, jobname):
        """Make the email_dir string.  Something like:
           /nfs/dist/dmp/amp/update/UAT/QUAL/QAMP_UAT0000000_090504130000i/email
           PARAMETERS:
               jobname - Something like DAMP_UAT0000000_090504130000i that is 29 characters.
           RETURNS:
               email_dir string.
        """
        email_dir = "/nfs/dist/dmp/amp/update/" + self.getMne(jobname) + "/" + self.getEnv(
            jobname) + "/" + jobname + "/email"
        return email_dir

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	mkWorkDir()
    #
    #	DESCRIPTION:
    #		Make the work directory from the jobname
    #		DAMP_UAT0000000_090504130000i - 29 chars
    #
    #	PARAMETERS:
    #		jobname
    #
    #	RETURN:
    #		work_dir
    ##################################################################################
    def mkWorkDir(self, jobname):
        """Make the work_dir string.  Something like:
           /nfs/dist/dmp/amp/update/UAT/QUAL/QAMP_UAT0000000_090504130000i
           PARAMETERS:
               jobname - Something like DAMP_UAT0000000_090504130000i that is 29 characters.
           RETURNS:
               work_dir string.
        """
        work_dir = "/nfs/dist/dmp/amp/update/" + self.getMne(jobname) + "/" + self.getEnv(jobname) + "/" + jobname
        return work_dir

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	isValidJobName()
    #
    #	DESCRIPTION:
    #		Is the jobname valid.
    #		DAMP_UAT0000000_090504130000i - 29 chars
    #
    #	PARAMETERS:
    #		jobname
    #
    #	RETURN:
    #		True or False
    ##################################################################################
    def isValidJobName(self, jobname):
        """Is the job name valid.
           PARAMETERS:
               jobname - Something like DAMP_UAT0000000_090504130000i that is 29 characters.
           RETURNS:
               True or False
        """
        rc = True
        if (len(jobname) != 29): return False
        ar = re.split(r'_', str(self.jobname))
        if (len(ar) != 3): return False
        env = ar[0][0]
        if (env != 'D' and env != 'Q' and env != 'P'): return False
        if (len(ar[1]) != 10): return False
        wstr = ar[1]
        if (not re.match(r'^([A-Z]{3,3})(\d{7,7})$', wstr)): return False
        wstr = ar[2]
        if (not re.match(r'(^\d{12,12})i$', wstr)): return False
        return rc

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	getEnv()
    #
    #	DESCRIPTION:
    #		Get the environment from the jobname
    #
    #	PARAMETERS:
    #		jobname
    #
    #	RETURN:
    #		env - DEV|QUAL|PROD
    ##################################################################################
    def getEnv(self, jobname):
        """Get the environment from the jobname.
           PARAMETERS:
               jobname - Something like DAMP_UAT0000000_090504130000i that is 29 characters.
           RETURNS:
               A string of either DEV|QUAL|PROD|UNKNOWN or None.
        """
        env = None
        if (not self.isValidJobName(jobname)): return "UNKNOWN"
        ar = re.split(r'_', jobname)
        # env = re.split( r'', ar[0] )[0]
        env = ar[0][0]
        if (env == 'D'): env = "DEV"
        if (env == 'Q'): env = "QUAL"
        if (env == 'P'): env = "PROD"
        return env

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	getMne()
    #
    #	DESCRIPTION:
    #		Get the mnemonic from the jobname
    #
    #	PARAMETERS:
    #		jobname
    #
    #	RETURN:
    #		mne
    ##################################################################################
    def getMne(self, jobname):
        """Get the mnemonic from the jobname.
           PARAMETERS:
               jobname - Something like DAMP_UAT0000000_090504130000i that is 29 characters.
           RETURNS:
               A string containing the mnemonic, "UNKNOWN",  or None.
        """
        mne = None
        if (not self.isValidJobName(jobname)): return "UNKNOWN"
        ar = re.split(r'_', jobname)
        wstr = ar[1]
        myMatch = re.match(r'^([A-Z]{3,3})(\d{7,7})', wstr)
        mne = myMatch.group(1)
        return mne

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	getCCID()
    #
    #	DESCRIPTION:
    #		Get the CCID from the jobname
    #
    #	PARAMETERS:
    #		jobname
    #
    #	RETURN:
    #		ccid
    ##################################################################################
    def getCCID(self, jobname):
        """Get the CCID from the jobname.
           PARAMETERS:
               jobname - Something like DAMP_UAT0000000_090504130000i that is 29 characters.
           RETURNS:
               A string containing the CCID, "UNKNOWN",  or None.
        """
        ccid = None
        if (not self.isValidJobName(jobname)): return "UNKNOWN"
        ar = re.split(r'_', jobname)
        wstr = ar[1]
        myMatch = re.match(r'^([A-Z]{3,3})(\d{7,7})', wstr)
        ccid = myMatch.group(2)
        return mne

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	getError()
    #
    #	DESCRIPTION:
    #		Get the last error for this module.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		error_msg
    ##################################################################################
    def getError(self):
        """Get the last error for this module."""
        return self.error_msg

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	getEmailDir()
    #
    #	DESCRIPTION:
    #		Get the email directory used to instantiate this instance.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		email_dir
    ##################################################################################
    def getEmailDir(self):
        """Get the email directory used to instantiate this instance."""
        return self.email_dir

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	getWorkDir()
    #
    #	DESCRIPTION:
    #		Get the working directory used to instantiate this instance.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		email_dir
    ##################################################################################
    def getWorkDir(self):
        """Get the email directory used to instantiate this instance."""
        return self.work_dir

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	setLog()
    #
    #	DESCRIPTION:
    #		Get the email directory used to instantiate this instance.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		email_dir
    ##################################################################################
    def setLog(self, log):
        """Get the email directory used to instantiate this instance.
           PARAMETERS:
               log  - instance of the pylib.Utils.MyLogger class
        """
        self.logger = log

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	logIt()
    #
    #	DESCRIPTION:
    #		Write a message to the log and possibly stdout.
    #
    #	PARAMETERS:
    #		msg - What you want to log.
    #
    #	RETURN:
    #		email_dir
    ##################################################################################
    def logIt(self, msg):
        """Write a message to the log and possibly stdout."""
        if (self.logger): self.logger.logIt(msg)

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	debug()
    #
    #	DESCRIPTION:
    #		Write a message to the log and possibly stdout.
    #
    #	PARAMETERS:
    #		msg - What you want to log.
    #
    #	RETURN:
    #		email_dir
    ##################################################################################
    def debug(self, msg):
        """Write a message to the log and possibly stdout."""
        if (self.logger): self.logger.debug(msg)

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	writeStatus()
    #
    #	DESCRIPTION:
    #		Write a status cookie file.
    #
    #	PARAMETERS:
    #		type -- "notice"
    #		host -- host name for the file
    #		app  -- application name
    #		status  -- ok|failed
    #		msg  -- message to be written to the status cookie file
    #
    #	RETURN:
    #		True for success or False
    ##################################################################################
    def writeStatus(self, type="notice", host="none", app="none", status="ok", msg=""):
        """Write a status cookie file.
           PARAMETERS:
               type -- "notice"
               host -- host name for the file
               app  -- application name
               status  -- ok|failed
               msg  -- message to be written to the status cookie file

           RETURN:
               True for success or False
        """
        self.error_msg = ""
        mytime = self.utils.mytime()
        FH = None
        status = status.lower()
        statusFile = self.email_dir + "/" + type + "." + host + "." + app + "." + str(os.getpid()) + "." + status

        try:
            FH = open(statusFile, "a")
        except IOError as inst:
            self.logIt(
                "pylib.Utils.CookieStatus.writeStatus(): Unable to open " + statusFile + " for append. => " + str(
                    inst.errno) + ":" + str(inst.strerror) + "\n")
            self.error_msg = "Unable to open " + statusFile + " for append. => " + str(inst.errno) + ":" + str(
                inst.strerror)
            return False
        # Endtry

        indicator = 0
        if (status != "ok"):  indicator = 1
        buffer = mytime + " " + host + " " + str(indicator) + " " + msg + "\n"
        FH.write(buffer)
        FH.close()
        return True

    ##################################################################################
    #	Enddef
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
    #		Destructor.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    ##################################################################################
    def __del__(self):
        """Destructor."""
        self.closeMe()
##################################################################################
#	Enddef
##################################################################################

##################################################################################
#	Endclass
##################################################################################


def main():
    myLogger = MyLogger(LOGFILE="/tmp/StatusCookie.log", STDOUT=True, DEBUG=True)
    myObject = StatusCookie(jobname="QAMP_UAT0000000_090504130000i", logger=myLogger);
    if (myObject is None): print("Failed to create the StatusCookie object.")
    email_dir = myObject.getEmailDir()
    myLogger.logIt("email_dir=" + str(email_dir) + "\n")
    work_dir = myObject.getWorkDir()
    myLogger.logIt("work_dir=" + str(work_dir) + "\n")
    myObject.writeStatus(host="dideploy11", app="StatusCookie", msg="This is a test")
    myObject.closeMe();


#	Enddef

#########################################
#   End
#########################################
if __name__ == "__main__":
    main()
