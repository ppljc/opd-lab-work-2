# Python модули
from logging.handlers import TimedRotatingFileHandler

import logging
import os


# Функционал
if not os.path.exists('./logs'):
    os.makedirs('./logs')

logger = logging.getLogger('base')
logger.setLevel(logging.DEBUG)

file_handler = TimedRotatingFileHandler(
    filename='./logs/base.log',
    when="midnight",
    interval=1,
    encoding='utf-8'
)

console_handler = logging.StreamHandler()

formatter = logging.Formatter(
    fmt='[%(asctime)s] %(levelname)s [%(filename)s; %(funcName)s]: %(message)s;',
    datefmt='%H:%M:%S'
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
