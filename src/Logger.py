import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    file_handler = RotatingFileHandler("log.txt", maxBytes=100_000, backupCount=1)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    return log
