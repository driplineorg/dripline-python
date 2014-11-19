'''
Log (application status, not sensor logs) master configuration
'''

from __future__ import print_function, absolute_import
import logging

# crate logger for 'dripline'
logger = logging.getLogger('dripline')
logger.setLevel(logging.DEBUG)
# create the console log handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# apply formatter and add handlers tot he loggers
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
