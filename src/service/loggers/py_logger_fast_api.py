import logging

from config import file_log_fast_api as filename
from src.service.loggers.time_formatter import KyivTimeFormatter

_format = f"%(asctime)s [%(levelname)s] - %(name)s - %(funcName)s(%(lineno)d) - %(message)s"

file_handler = logging.FileHandler(filename=filename)
file_handler.setLevel(level=logging.INFO)
file_handler.setFormatter(fmt=KyivTimeFormatter(_format))

stream_handler = logging.StreamHandler()
stream_handler.setLevel(level=logging.DEBUG)
stream_handler.setFormatter(fmt=KyivTimeFormatter(_format))


def get_logger(name):
    logger = logging.getLogger(name=name)
    logger.setLevel(level=logging.DEBUG)
    logger.addHandler(hdlr=file_handler)
    logger.addHandler(hdlr=stream_handler)
    return logger
