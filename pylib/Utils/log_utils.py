import logging
import sys

local_flag = True if sys.platform.startswith('win') or sys.platform == 'darwin' else False

class LogUtils():

    def __init__(self):
        self.VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL")

    def set_root_log_level(self,log_level="INFO"):
        if log_level not in self.VALID_LOG_LEVELS:
            raise ValueError(f"Invalid Log Level.  It must be one of {self.VALID_LOG_LEVELS}")
        logging.getLogger().setLevel(logging.getLevelName(log_level))


    def set_logger(self, logger_name, log_level="INFO"):
        """
            1. All logging propagates to the root logger.  The root logger has it's own handlers and
               configuration.  This propagation can cause duplicate log entries in cloudwatch and on the command line output.
            2. The very first logger that gets called, sets the logging configuration for the whole application.  The root logger will also log.
            3. To overcome this, it is important to configure the root logger BEFORE any logger is called.  You must remove the root handlers,
               set the logging.basicConfig() with the level and the format.
            4. In 2. and 3. above, you must set the configuration for the logging(root) BEFORE you get the logger via the logger = logging.getLogger(logger_name) call. 
               Again, all this must be done BEFORE getting the logger to return.
        """
        if log_level not in self.VALID_LOG_LEVELS:
            raise ValueError(f"Invalid log level.  It must be one of {self.VALID_LOG_LEVELS}")
        while len(logging.root.handlers) > 0:
            logging.root.removeHandler(logging.root.handlers[-1])
        logging_level = logging.getLevelName(log_level)
        if local_flag:
            logging.basicConfig(level=logging_level,format='%(asctime)s %(levelname)s %(message)s')
        else:
            logging.basicConfig(level=logging_level,format='%(levelname)s %(message)s')
        logger = logging.getLogger(logger_name)
        #logger.setLevel(logging.getLevelName(log_level))
        return logger