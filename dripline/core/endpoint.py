__all__ = []

from _dripline.core import _Endpoint
from .request_receiver import RequestReceiver

import logging

logger = logging.getLogger(__name__)

__all__.append('Endpoint')


class Endpoint(_Endpoint, RequestReceiver):
    '''
    Base class for all objects which can be sent dripline requests.
    Every object described in a runtime configuration passed to `dl-serve` should derive from this class (either directly or indirectly).
    '''

    def __init__(self, name):
        '''
        Args:
            name (str) : the name of the endpoint, specifies the binding key for request messages to which this object should reply
        '''
        _Endpoint.__init__(self, name)
    