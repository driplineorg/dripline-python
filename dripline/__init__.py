'''
Dripline is moving to the AMQP protocol.
'''

from __future__ import absolute_import

import pkg_resources
__version__ = pkg_resources.require("dripline")[0].version.split('-')[0]
__commit__ = pkg_resources.require("dripline")[0].version.split('-')[-1]

from . import core
from . import instruments
