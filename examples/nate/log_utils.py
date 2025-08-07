import logging

LOG_COLORS = {
    'DEBUG': '\033[94m',  # Blue
    'INFO': '\033[92m',  # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',  # Red
    'CRITICAL': '\033[95m',  # Magenta
}


class ColorFormatter(logging.Formatter):

    def format(self, record):
        color = LOG_COLORS.get(record.levelname, '\033[0m')
        record.levelname = f"{color}[{record.levelname}]\033[0m"
        return super().format(record)


def get_logger(name):
    """
    Get a logger with the specified name.

    :param name: The name of the logger.
    :return: A logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter("%(levelname)s %(message)s"))
        logger.addHandler(handler)
    return logger


formatter = ColorFormatter("%(levelname)s %(message)s")
logging.getLogger("pyniryo").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
