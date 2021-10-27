import os
import sys
import inspect
import getopt

from pylib.Utils.log_utils import LogUtils

def lineno():
    """Returns the current line number in our program"""
    return inspect.currentframe().f_back.f_lineno

class CmdOptsHandler():

    __name__ = "cmd_opts_handler"

    def __init__(self,log_level: str = "INFO"):
        """
        Class to handle command line args.
        :param log_level: contains the logging level for this class.
        """
        logutils = LogUtils()
        self.logger = logutils.set_logger(__name__, log_level)

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
    def usage(self, app:str):
        """Display the command line usage."""
        usage_string = f"python {app}\n" + \
            "\t[-s, --stdout]   -- stdout on.\n" + \
            "\t[-d, --debug]    -- debug on.\n" + \
            "\t[-h, --help]     -- show usage.\n\n" + \
            f"python {app} --stdout --debug\n"
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
    def getCmdOptions(self, app: str):
        """Get the command line arguments."""
        #print( "getCmdOptions() entered...\n )"
        self.my_opts = {}
        err = None
        required_opts = { 'help': True, 'debug': True, 'stdout': True }
        rc = 1
    
        try:
            #opts, args = getopt.getopt(sys.argv[1:], "hdsn:h:p:l:", ["help", "debug", "stdout", "number=", "host=", "port=", "logfile="]) #@UnusedVariable
            opts, args = getopt.getopt(sys.argv[1:], "hdsl:", ["help", "debug", "stdout"]) #@UnusedVariable
        except(getopt.GetoptError, err):
            # print help information and exit:
            print(str(err)) # will print something like "option -a not recognized"
            self.usage(app)
            sys.exit(2)
    
        for o, a in opts:
            if o in ("-h", "--help"):
                self.usage(app)
                sys.exit()
            #elif o in ("-p", "--port"):
            #    my_opts['port'] = a
            #    required_opts['port'] = True
            elif o in ("-s", "--stdout"):
                my_opts['stdout'] = True
            elif o in ("-d", "--debug"):
                my_opts['debug'] = True
            else:
                rc = 0
                assert False, "unhandled option"
            #Endif
        #Endfor
    
        if(rc == 0):
            usage(app)
    
        #for k, v in required_opts.iteritem():
        for k, v in required_opts.items(): #@UnusedVariable
            if(required_opts[k] == False):
                msg = sys.argv[0] + " Must provide: " + "--" + str(k)
                print(msg)
                rc = 0
            #Endif
        #Endfor
    
        if(rc == 0):
            usage()
            sys.exit(2)
        #Endif 
    

    def show_cmd_settings(self):
        print(f"Command line Settings: opts={self.my_opts}")
    
def main():
    cmd_obj = CmdOptsHandler()
    cmd_obj.getCmdOptions(sys.argv[0])
    cmd_obj.show_cmd_settings()


if __name__ == "__main__":
    main()