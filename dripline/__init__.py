'''
Dripline is moving to the AMQP protocol.
'''

import pkg_resources
__version__ = pkg_resources.require("dripline")[0].version

import core
import io
import instruments
