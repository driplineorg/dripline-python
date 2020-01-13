__all__ = []

import scarab
from _dripline.core import DL_Success, set_reply_cache
from .return_codes import get_return_codes_dict

__all__.append('ThrowReply')
class ThrowReply(Exception):
    def __init__(self, return_code=DL_Success(), message=DL_Success().description, payload=scarab.Param()):
        '''
        return_code (_dripline.core.ReturnCode || string) : either a ReturnCode object, or the string name of a return code
        message (string) : string to pass into the exception object, provides clarification of the particular exception
        payload (scarab.Param) : any data to include in the payload of the reply message (in a Warning, should match the normal success data)
        '''
        Exception.__init__(self, message)
        if isinstance(return_code, str):
            return_code = get_return_codes_dict()[return_code]
        set_reply_cache(return_code, message, payload)
