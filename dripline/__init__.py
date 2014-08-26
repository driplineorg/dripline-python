'''
    Dripline is moving to the AMQP protocol.
'''

import pkg_resources

from dripline.constants import *
__version__ = pkg_resources.require("dripline")[0].version
