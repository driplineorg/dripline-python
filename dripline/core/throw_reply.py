__all__ = []

import scarab
from _dripline.core import _ThrowReply, DL_Success, set_reply_cache

__all__.append('ThrowReply')
class ThrowReply(Exception):
    '''
    Exception class for use throughout the codebase for exceptions which do not fatally interrupt a running dripline service.
    These exceptions are caught in the top of the message handling call stack and result in an reply message being sent indicating an error.
    The preferred way to send a reply indicating an error (or warning) is to raise an instance of ThrowReply.
    In cases where a dependency library throws a custom exception, or any piece of code throws a standard python exception, if the expected behavior is an error reply and continued service operation, that exception must be handled and ThrowReply raised instead.
    '''
    def __init__(self, return_code=DL_Success(), message=DL_Success().description, payload=scarab.Param()):
        '''
        return_code (_dripline.core.ReturnCode) : instance of subclass of ReturnCode, it must be an instance which is already registered and is
                                                  used to determine various header fields of the resulting dripline message.
        message (string) : provides more specific information about the particular exception (beyond the fixed ReturnCode's description
        payload (scarab.Param) : optional data to populate the ReplyMessage's payload, especially useful in cases of Warnings, where there is
                                 potentially valid data to return in response to the request.
        '''
        Exception.__init__(self)
        set_reply_cache(return_code, message, payload)
