'''
    Dripline is moving to the AMQP protocol.
'''

import pkg_resources
__version__ = pkg_resources.require("dripline")[0].version

from dripline.constants import *
from message import *
