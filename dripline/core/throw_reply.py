__all__ = []

import scarab
from _dripline.core import DL_Success, set_reply_cache
from .return_codes import get_return_codes_dict

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
        return_code (_dripline.core.ReturnCode || string) : instance of subclass of ReturnCode, or the string name of a return code;
                it must be an instance which is already registered and is used to determine various header fields of the resulting dripline message.
        message (string) : provides more specific information about the particular exception (beyond the fixed ReturnCode's description
        payload (scarab.Param) : any data to include in the payload of the reply message (in a Warning, should match the normal success data)
        '''
        Exception.__init__(self, message)
        if isinstance(return_code, str):
            return_code = get_return_codes_dict()[return_code]
        set_reply_cache(return_code, message, payload)
