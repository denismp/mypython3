#!/usr/bin/env python
######################################################################################
##	MyUtils.py
##
##	Python module with some useful utility functions.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	08/07/2009	Denis M. Putnam		Created.
######################################################################################
import time
import platform
import re


# try: set
# except NameError: from sets import Set as set

class MyUtils:
    """MyUtils class that provides some useful utilities."""

    ##################################################################################
    #	__init__()
    #
    #	DESCRIPTION:
    #		Class initializer.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		An instance of this class
    ##################################################################################
    def __init__(self):
        """Initializer."""

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	getPlatform()
    #
    #	DESCRIPTION:
    #		Get the system platform.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		The platform name
    ##################################################################################
    def getPlatform(self):
        """
           Get the system platform.
           PARAMETERS:

           RETURN:
               value
        """
        ##############################################################################
        #	The platform string looks something like:
        #	platform=Java-1.5.0_13-Java_HotSpot-TM-_Server_VM,_1.5.0_13-b05,_Sun_Microsystems_Inc.-on-Linux-2.6.18-92.el5-i386
        #   NOTE:  This code was originally written in jython 2.7
        ##############################################################################
        mysystem = platform.system()
        myname = platform.uname()
        machine = platform.machine()
        fullInfo = platform.platform()
        # ar = re.split('-', fullInfo)  # split on the '-'
        # ar = re.split('-', ar[1])  # split on the '-'
        # value = ar[2].lower()  # take the first token and lower case it.
        return fullInfo

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	calcArgsvIndex()
    #
    #	DESCRIPTION:
    #		Calculate the INDEX value to be used in the getopt.getopt( sys.argv[INDEX:], .... )
    #
    #	PARAMETERS:
    #		see below.
    #
    #	RETURN:
    #		INDEX
    ##################################################################################
    def calcArgsvIndex(self, argv0=None, programName=None):
        """
           Calculate the INDEX value to be used in the getopt.getopt( sys.argv[INDEX:], .... )
           PARAMETERS:
               argv0       - the value of sys.argv[0]
               programName - the name of the calling program.

           RETURN:
               value
        """
        INDEX = 1
        firstArg = ''

        ###############################################
        #	Determine if were called from the command
        #	line or from wsadmin.sh or some other
        #	script that strips off argv[0].
        ###############################################
        # print "platform=" + str( self.getPlatform() )
        # print "thisprogram=" + str( programName )
        try:
            firstArg = argv0
            # print "firstArg=" + str( firstArg )
            if firstArg != programName:
                INDEX = 0
        except IndexError as e:
            print(e)
        # Endtry

        ##############################################
        #	For now we will assume that the linux
        #	platform is always 1.  This may change
        #	later.
        ##############################################
        if self.getPlatform() == 'linux':
            INDEX = 1
        # print "INDEX=" + str( INDEX )
        return INDEX

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	uniquer()
    #
    #	DESCRIPTION:
    #		Remove duplicates from a sequence while maintaining sequence order.
    #
    #	PARAMETERS:
    #		seq - the sequence to be made unique.
    #		f   - defines an equivalence relation among items of sequence, seq, and
    #			  f(x) must be hashable for each item x for the seq.
    #
    #	RETURN:
    #		result
    ##################################################################################
    def uniquer(self, seq, f=None):
        """
           Remove duplicates from a sequence while maintaining sequence order.
           Keeps earliest occuring item of each f-defined equivalence class.
           PARAMETERS:
               seq - the sequence to be made unique.
               f   - defines an equivalence relation among items of sequence, seq, and
               f(x) must be hashable for each item x for the seq.

           RETURN:
               result sequence
        """
        # print( __name__ + ".uniquer(): seq=" + str( seq ) + '\n' )
        # print( __name__ + ".uniquer(): f=" + str( f ) + '\n' )

        try:
            if f is None:  # f's default is the identity function f(x) -> x
                def f(x): return x
        # Endif
        except Exception as e:
            print((__name__ + ".uniquer(): call to f(x) failed:" + str(e) + '\n'))
            print((__name__ + ".uniquer(): seq=" + str(seq) + '\n'))
            print((__name__ + ".uniquer(): f=" + str(f) + '\n'))
            raise
        # Endtry

        already_seen = set()
        result = []

        try:
            for item in seq:
                marker = f(item)
                if marker not in already_seen:
                    already_seen.add(marker)
                    result.append(item)
        # Endif
        # Endfor
        except Exception as e:
            print((__name__ + ".uniquer(): Parse of seq failed:" + str(e) + '\n'))
            print((__name__ + ".uniquer(): seq=" + str(seq) + '\n'))
            print((__name__ + ".uniquer(): f=" + str(f) + '\n'))
            raise
        # Endtry

        # print( __name__ + ".uniquer(): already_seen=" + str( already_seen ) + '\n' )
        # print( __name__ + ".uniquer(): result=" + str( result ) + '\n' )
        return result

    ##################################################################################
    #	Enddef
    ##################################################################################

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
        """Get the current time as YYYYMMDD_HH:MM:SS format.
           RETURN:
              The time string.
        """
        mytime = time.localtime()
        mytimestr = time.strftime("%Y%m%d-%H:%M:%S", mytime)
        return mytimestr

    ##################################################################################
    #	Enddef
    ##################################################################################

    ##################################################################################
    #	mktime()
    #
    #	DESCRIPTION:
    #		Get the current time.
    #
    #	PARAMETERS:
    #
    #	RETURN:
    #		time
    ##################################################################################
    def mktime(self, secs):
        """Make the given secs into a string in the YYYYMMDD_HH:MM:SS format.
           RETURN:
              The time string.
        """
        mytime = time.localtime(secs)
        mytimestr = time.strftime("%Y%m%d-%H:%M:%S", mytime)
        return mytimestr

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
    #		Destructor
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


def myf(x):
    mykey = list(x.keys())[0]
    myvalue = x.get(mykey)
    return mykey + ":" + myvalue


# Enddef

def main():
    import sys
    myObject = MyUtils()
    print((myObject.mytime()))
    mylist = ['a', 'a', 'b', 'b', 'c']
    newlist = myObject.uniquer(mylist)
    print(mylist, "\n")
    print(newlist, "\n")
    print(myObject.getPlatform())
    INDEX = myObject.calcArgsvIndex(argv0=sys.argv[0], programName=__name__)
    print("INDEX=" + str(INDEX))
    INDEX = myObject.calcArgsvIndex(argv0=sys.argv[0], programName="MyUtils.py")
    print("INDEX=" + str(INDEX))

    myar = list()
    myar.append({"host1": "01"})
    myar.append({"host1": "01"})
    myar.append({"host2": "02"})
    myar.append({"host2": "02"})

    myres = myObject.uniquer(myar, myf)
    print(myres)
    myObject.closeMe()


#	Enddef

#########################################
#   End
#########################################
if __name__ == "__main__":
    main()
