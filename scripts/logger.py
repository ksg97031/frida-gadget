"""logger.py"""
import logging
from colorlog import ColoredFormatter

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = ColoredFormatter(
    "%(log_color)s[%(levelname)s] %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'white,bold',
        'INFOV':    'cyan,bold',
        'WARNING':  'yellow',
        'ERROR':    'red,bold',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)
ch.setFormatter(formatter)
logger = logging.getLogger('frida-gadget')
logger.setLevel(logging.DEBUG)
logger.addHandler(ch)
