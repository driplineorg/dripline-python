'''
Log (application status messages from python's logging, not sensor value logs) master configuration

Similar to arg_parse, this is a utility primarily for scripts/applications so that they can configure themselves to print using the same format etc... could potentially be incorporated into that module.
'''

from __future__ import print_function, absolute_import

from ..core import constants

import logging

# crate logger for 'dripline'
logger = logging.getLogger('dripline')
logger.setLevel(logging.DEBUG)
# create the console log handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
# create formatter
try:
    import colorlog
    formatter = colorlog.ColoredFormatter(
            "%(asctime)s%(log_color)s[%(levelname)-8s]%(name)s(%(lineno)d) -> %(purple)s%(message)s",
            datefmt = constants.TIME_FORMAT,
            reset=True,
            )
except ImportError:
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s(%(lineno)d) -> %(message)s', constants.TIME_FORMAT)

# apply formatter and add handlers tot he loggers
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
