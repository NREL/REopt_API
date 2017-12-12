import logging
import inspect
import os


def setup_logging():
    file_logfile = os.path.join(os.getcwd(), "log", "reopt_api.log")
    logging.basicConfig(filename=file_logfile,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M%S %p',
                        level=logging.INFO)
    log("INFO", "Logging setup")


# logging utility
def log(level, message):

    func = inspect.currentframe().f_back.f_code
    if level == "DEBUG":
        logging.debug("%s: %s in %s" % (
            message,
            func.co_name,
            func.co_filename
        ))
    elif level == "INFO":
        logging.info("%s: %s in %s" % (
            message,
            func.co_name,
            func.co_filename
        ))
    elif level == "WARNING":
        logging.warning("%s: %s in %s" % (
            message,
            func.co_name,
            func.co_filename
        ))
    elif level == "ERROR":
        logging.error("%s: %s in %s" % (
            message,
            func.co_name,
            func.co_filename
        ))
    elif level == "CRITICAL":
        logging.critical("%s: %s in %s" % (
            message,
            func.co_name,
            func.co_filename
        ))
