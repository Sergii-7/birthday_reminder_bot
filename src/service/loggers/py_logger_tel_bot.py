import logging
from config import file_log_tel_bot as filename


_format = f"%(asctime)s [%(levelname)s] - %(name)s - %(funcName)s(%(lineno)d) - %(message)s"

# filename = 'logs/fast_api_admin_panel.log'

file_handler = logging.FileHandler(filename=filename, encoding='utf-8')
file_handler.setLevel(level=logging.INFO)
file_handler.setFormatter(logging.Formatter(fmt=_format))

stream_handler = logging.StreamHandler()
stream_handler.setLevel(level=logging.DEBUG)
stream_handler.setFormatter(logging.Formatter(fmt=_format))


def get_logger(name):
    logger = logging.getLogger(name=name)
    logger.setLevel(level=logging.DEBUG)
    logger.addHandler(hdlr=file_handler)
    logger.addHandler(hdlr=stream_handler)
    return logger