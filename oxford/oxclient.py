#!/usr/bin/env python
##################################################################################
##    oxclient.py
##    Python script to:
##    Test the oxserver.py code.  The code is designed to invoke a socket
##    for one file based on the message number.  This will allow a calling script
##    to execute this script in the background while the script invokes other
##    calls to run this script in parallel to load the server.
##################################################################################
##
##    MODIFICATION HISTORY:
##    DATE        WHOM                DESCRIPTION
##    04/01/2011  Denis M. Putnam        Created.
##################################################################################

#########################################
#    Import section.
#########################################
import getopt, sys  # @UnusedImport
import os, socket  # @UnusedImport
from stat import *  # @UnusedWildImport
from pylib.Utils.MyLogger import *  # @UnusedWildImport
# from pylib.Utils.MySocket import * #@UnusedWildImport
from pylib.Tasks.FileTask import *  # @UnusedWildImport

#########################################
#    Global variables.
#########################################
CONFIG = {}


#########################################
#    Function definitions.
#########################################

#######################################################
#    initialize()
#
#    DESCRIPTION:
#        This function initializes this program.
#
#    PARAMETERS:
#
#    RETURN:
#######################################################
def initialize():
    """Initialize this module."""
    mytime = time.localtime()
    mytimestr = time.strftime("%Y%m%d-%H_%M_%S", mytime)

    # CONFIG['logfile'    ]        = "/tmp/mywas.log"
    CONFIG['thisprogram'] = os.path.basename(sys.argv[0])
    CONFIG['number'] = 0
    CONFIG['host'] = 'localhost'
    CONFIG['port'] = 50007
    CONFIG['logfile'] = "/tmp/" + CONFIG['thisprogram'] + "_" + mytimestr + ".log"
    # CONFIG['logfile'       ]        = CONFIG['thisprogram'] + ".log"
    CONFIG['stdout'] = False
    CONFIG['debug'] = False


#######################################################
#    Enddef
#######################################################

#######################################################
#    resetInit()
#
#    DESCRIPTION:
#        Reset the initialized values based on what
#        the user specified on the command line.
#
#    PARAMETERS:
#        myopts - a dictionary of the command line
#
#    RETURN:
#######################################################
def resetInit(myopts):
    """Reset the initialize values based on what the user specified on the command line."""
    for my_opt in list(myopts.keys()):
        CONFIG[my_opt] = myopts[my_opt]
        # print( my_opt + '=' + str( CONFIG[my_opt] ) )
    # Endfor

    if int(CONFIG['number']) > 9999 or int(CONFIG['number']) < 0:
        print("--number is not valid.")
        usage()
        sys.exit(2)

    CONFIG['utils'] = MyLogger(LOGFILE=CONFIG['logfile'], STDOUT=CONFIG['stdout'], DEBUG=CONFIG['debug']);

    # CONFIG['utils'].logIt( "resetInit(): Here I am.\n" );


#######################################################
#    Enddef
#######################################################

#######################################################
#    usage()
#
#    DESCRIPTION:
#        Display the usage of this program to standard
#        output.
#
#    PARAMETERS:
#
#    RETURN:
#######################################################
def usage():
    """Display the command line usage."""
    usage_string = "oxclient.py\n" + \
                   "\t[-n, --number]   -- NNNN [0-9999] (optional: default is " + str(CONFIG['number']) + ")\n" + \
                   "\t[-H, --host]     -- Something like freedom.dynalis.org(optional: default is " + str(
        CONFIG['host']) + ")\n" + \
                   "\t[-p, --port]     -- Something like 50007(optional: default is " + str(CONFIG['port']) + ")\n" + \
                   "\t[-l, --logfile]  -- log file(optional: default is " + str(CONFIG['logfile']) + ")\n" + \
                   "\t[-s, --stdout]   -- stdout on.\n" + \
                   "\t[-d, --debug]    -- debug on.\n" + \
                   "\t[-h, --help]     -- show usage.\n\n" + \
                   "oxclient.py --number 9999 --host freedom.dynalis.org --port 50007 --logfile /tmp/oxclient.log --stdout\n"
    print(usage_string)


#######################################################
#    Enddef
#######################################################

#######################################################
#    getCmdOptions()
#
#    DESCRIPTION:
#        Get the command line options and store them
#        into the CONFIG dictionary.
#
#    PARAMETERS:
#
#    RETURN:
#######################################################
def getCmdOptions():
    """Get the command line arguments."""
    # print( "getCmdOptions() entered...\n )"
    my_opts = {}
    err = None
    required_opts = {'number': True, 'host': True, 'port': True, 'help': True, 'debug': True, 'stdout': True,
                     'logfile': True}
    rc = 1

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdsn:H:p:l:", ["help", "debug", "stdout", "number=", "host=", "port=",
                                                                 "logfile="])  # @UnusedVariable
    except(getopt.GetoptError, err):
        # print help information and exit:
        print((str(err)))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-n", "--number"):
            my_opts['number'] = a
        elif o in ("-H", "--host"):
            my_opts['host'] = a
        elif o in ("-p", "--port"):
            my_opts['port'] = a
            required_opts['port'] = True
        elif o in ("-l", "--logfile"):
            my_opts['logfile'] = a
        elif o in ("-s", "--stdout"):
            my_opts['stdout'] = True
        elif o in ("-d", "--debug"):
            my_opts['debug'] = True
        else:
            rc = 0
            assert False, "unhandled option"
        # Endif
    # Endfor

    if (rc == 0):
        usage()

    # for k, v in required_opts.iteritem():
    for k, v in list(required_opts.items()):  # @UnusedVariable
        if (required_opts[k] == False):
            msg = sys.argv[0] + " Must provide: " + "--" + str(k)
            print(msg)
            rc = 0
        # Endif
    # Endfor

    if (rc == 0):
        usage()
        sys.exit(2)
    # Endif

    resetInit(my_opts)


#######################################################
#    Enddef
#######################################################

#######################################################
#    printVersionInfo()
#
#    DESCRIPTION:
#        Print the version and other information about
#        this program.
#
#    PARAMETERS:
#
#    RETURN:
#######################################################
def printVersionInfo():
    """Print the version and other information about this program."""
    # pass
    pathname = sys.argv[0]
    myMtime = os.stat(pathname)[ST_MTIME]
    modDate = CONFIG['utils'].mktime(myMtime)
    logIt("Python Script: " + pathname + "\n")
    logIt("Version Date:  " + modDate + "\n")


#######################################################
#    Enddef
#######################################################

#######################################################
#    printInfo()
#
#    DESCRIPTION:
#        Print the detailed information about 
#        this program.
#
#    PARAMETERS:
#
#    RETURN:
#######################################################
def printInfo():
    """Print the detailed information about this program."""
    utils = CONFIG['utils']
    mytime = utils.mytime()
    logIt("Todays date:   " + mytime + "\n")
    logIt("        Number is: " + str(CONFIG['number']) + "\n")
    logIt("          Host is: " + str(CONFIG['host']) + "\n")
    logIt("          Port is: " + str(CONFIG['port']) + "\n")
    logIt("      Log file is: " + str(CONFIG['logfile']) + "\n")
    logIt("   Stdout flag is: " + str(CONFIG['stdout']) + "\n")
    logIt("    Debug flag is: " + str(CONFIG['debug']) + "\n")


#######################################################
#    Enddef
#######################################################

#######################################################
#    logIt()
#
#    DESCRIPTION:
#        Logs the given message.
#
#    PARAMETERS:
#
#    RETURN:
#######################################################
def logIt(msg):
    """Logs the given message."""
    utils = CONFIG['utils'].logIt(msg)  # @UnusedVariable


#######################################################
#    Enddef
#######################################################

#######################################################
#    debug()
#
#    DESCRIPTION:
#        Logs the given message.
#
#    PARAMETERS:
#
#    RETURN:
#######################################################
def debug(msg):
    """Logs the given message."""
    if (CONFIG['debug']):
        logIt(msg)


#######################################################
#    Enddef
#######################################################

#######################################################
#    getFillerData()
#
#    DESCRIPTION:
#        Get the filler data for the test.
#
#    PARAMETERS:
#
#    RETURN:
#######################################################
def getFillerData():
    """Get the filler data for the test.  Reads 2000 bytes
       from the filler.txt file.
    """
    filler = ""
    fileName = "filler.txt"

    try:
        FH = open(fileName, "r")
        filler = FH.read(2000)
        FH.close()
        return filler
    except IOError as inst:  # @UnusedVariable
        raise
    # Endtry


#######################################################
#    Enddef
#######################################################

#######################################################
#    getFillerData()
#
#    DESCRIPTION:
#        Get the filler data for the test.
#
#    PARAMETERS:
#
#    RETURN:
#######################################################
def requestServerFile(filler):
    """Request the file from the server."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((CONFIG['host'], CONFIG['port']))

    debug('requestServerFile(): Before msgNum=' + str(CONFIG['number']) + "\n")
    msgNum = socket.htonl(int(str(CONFIG['number'])))
    debug('requestServerFile(): After msgNum=' + str(msgNum) + "\n")
    if True:
        s.send(str(msgNum).encode())
        s.send(filler.encode())
        data = "XXX"
        while data != "":
            data = s.recv(2048)
            if data != "":
                print('Received', repr(data))
        s.close()
        # print 'Received', repr(data)


#######################################################
#    Enddef
#######################################################

#######################################################
#    doWork()
#
#    DESCRIPTION:
#        This function does all work for this program.
#
#    PARAMETERS:
#
#    RETURN:
#        0 for success or non-zero.
#######################################################
def doWork():
    """Do all the real work for this program."""
    # rVal    = True
    rc = 0
    printInfo()

    filler = getFillerData()
    # debug( "doWork(): filler = " + filler )
    requestServerFile(filler)

    return rc


#######################################################
#    Enddef
#######################################################

#######################################################
#    cleanUp()
#
#    DESCRIPTION:
#
#    PARAMETERS:
#
#    RETURN:
#######################################################
def cleanUp():
    """Do any clean up required for this program."""
    pass


#######################################################
#    Enddef
#######################################################

#######################################################
#    main()
#
#    DESCRIPTION:
#        The entry point into this program.
#
#    PARAMETERS:
#
#    RETURN:
#######################################################
def main():
    """The entry point into this program."""
    # print( "main() entered..." )
    initialize()
    getCmdOptions()
    printVersionInfo()

    rc = doWork()

    cleanUp()
    sys.exit(rc)


#######################################################
#    Enddef
#######################################################

#########################################
#    End
#########################################
if __name__ == "__main__":
    main()
