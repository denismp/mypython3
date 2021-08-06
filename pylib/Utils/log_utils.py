import logging

class LogUtils():

    def __init__(self):
        self.VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL")

    def set_root_log_level(self,log_level="INFO"):
        if log_level not in self.VALID_LOG_LEVELS:
            raise ValueError(f"Invalid Log Level.  It must be one of {self.VALID_LOG_LEVELS}")
        logging.getLogger().setLevel(logging.getLevelName(log_level))


    def set_logger(self, logger_name, log_level="INFO"):
        #logger = logging.getLogger(logger_name)
        if log_level not in self.VALID_LOG_LEVELS:
            raise ValueError(f"Invalid Log Level.  It must be one of {self.VALID_LOG_LEVELS}")
        #logger.setLevel(logging.getLevelName(log_level))
        #return logger
        logging.getLogger(logger_name).setLevel(logging.getLevelName(log_level))
        logging.basicConfig(format='%(levelname)s:%(message)s')
        return logging