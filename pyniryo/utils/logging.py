import logging


def get_logger(name):
    logger = logging.getLogger('pyniryo').getChild(name)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    logger.addHandler(handler)

    return logger
