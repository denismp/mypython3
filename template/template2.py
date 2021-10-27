import sys

from pylib.Utils.log_utils import LogUtils
from cmd_opts_handler import CmdOptsHandler

class Template2():

    def __init__(self, log_level: str = "DEBUG"):
        logutils = LogUtils()
        self.logger = logutils.set_logger(__name__, log_level)
        self.cmd_opt_obj = CmdOptsHandler()
        self.cmd_opt_obj.getCmdOptions(sys.argv[0])

def main():
    tmp_obj = Template2()
    tmp_obj.logger.info("Started...")
    tmp_obj.logger.fatal("Fatal message")
    tmp_obj.logger.error("Error message")
    tmp_obj.logger.debug("Debug message")
    tmp_obj.logger.info(f"my_opts={tmp_obj.cmd_opt_obj.my_opts}")

if __name__ == "__main__":
    main()