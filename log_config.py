import logging
import logging.handlers
import os

ARTIFACTS_FOLDER_NAME = 'artifacts'
EXECUTION_LOG_NAME = 'execution_log.log'


def log(func):
    """ Log what function is called. """
    def wrap_log(*args, **kwargs):
        name = func.__name__
        result = func(*args, **kwargs)
        logger = logging.getLogger('root')
        logger.debug("Call function %s with args %s" % (name, args))
        logger.debug("Function %s returned %s" % (name, result))
        return result
    return wrap_log


def setup_custom_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s:%(module)s:%(funcName)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if not os.path.exists(ARTIFACTS_FOLDER_NAME): os.makedirs(ARTIFACTS_FOLDER_NAME)
    log_path = os.path.join(ARTIFACTS_FOLDER_NAME, EXECUTION_LOG_NAME)
    file_handler = logging.handlers.TimedRotatingFileHandler(log_path, when="midnight")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

setup_custom_logger('root')

