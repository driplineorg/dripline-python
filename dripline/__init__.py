'''
Dripline is moving to the AMQP protocol.
'''

from __future__ import absolute_import

import pkg_resources
__version__ = pkg_resources.require("dripline")[0].version

from . import core
from . import instruments
