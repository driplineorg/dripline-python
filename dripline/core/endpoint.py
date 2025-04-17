__all__ = []

from _dripline.core import _Endpoint
from .request_receiver import RequestHandler

import logging

logger = logging.getLogger(__name__)

__all__.append('Endpoint')


class Endpoint(_Endpoint, RequestHandler):
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
        '''
        Default function for handling an OP_GET request message addressed to this endpoint.

        .. note: For dripline extension developers -- This function, as defined in RequestHandler, implements the characteristic 
        dripline-python behavior for an endpoint receiving a get request, including using the specifier to access attributes, 
        and calling on_get() when there is no specifier.  
        As an extension author you might typically override RequestReciever.on_get(), but leave this function alone.

        .. note: For core dripline developers -- This function has to be here to correctly receive trampolined calls from 
        the C++ base class.  It intentionally just calls the version of do_get_request() in RequestHandler.

        Args:
            a_request_message (MsgRequest): the message receveived by this endpoint
        '''

        return RequestHandler.do_get_request(self, a_request_message)

    def do_set_request(self, a_request_message):
        '''
        Default function for handling an OP_SET request message addressed to this endpoint.

        .. note: For dripline extension developers -- This function, as defined in RequestHandler, implements the characteristic 
        dripline-python behavior for an endpoint receiving a set request, including using the specifier to access attributes, 
        and calling on_set() when there is no specifier.  
        As an extension author you might typically override RequestReciever.on_set(), but leave this function alone.

        .. note: For core dripline developers -- This function has to be here to correctly receive trampolined calls from 
        the C++ base class.  It intentionally just calls the version of do_set_request() in RequestHandler.

        Args:
            a_request_message (MsgRequest): the message receveived by this endpoint
        '''

        return RequestHandler.do_set_request(self, a_request_message)

    def do_cmd_request(self, a_request_message):
        '''
        Default function for handling an OP_CMD request message addressed to this endpoint.

        .. note: For dripline extension developers -- This function, as defined in RequestHandler, implements the characteristic 
        dripline-python behavior for an endpoint receiving a cmd request, namesly using the specifier to call endpoint methods.

        .. note: For core dripline developers -- This function has to be here to correctly receive trampolined calls from 
        the C++ base class.  It intentionally just calls the version of do_cmd_request() in RequestHandler.

        Args:
            a_request_message (MsgRequest): the message receveived by this endpoint
        '''

        return RequestHandler.do_cmd_request(self, a_request_message)
