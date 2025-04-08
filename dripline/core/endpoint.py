__all__ = []

import scarab
from _dripline.core import _Endpoint
from .throw_reply import ThrowReply
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

    def do_get_request(self, a_request_message): 
        return self._do_get_request(a_request_message)

    def do_set_request(self, a_request_message): 
        return self._do_set_request(a_request_message)

    def do_cmd_request(self, a_request_message): 
        return self._do_cmd_request(a_request_message)
    
    def on_get(self):
        return self._on_get()
    
    def on_set(self, value):
        return self._on_set(value)