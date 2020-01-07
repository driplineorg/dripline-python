__all__ = []

import scarab
from _dripline.core import _ThrowReply, DL_Success, set_reply_cache

__all__.append('ThrowReply')
class ThrowReply(Exception):
    def __init__(self, return_code=DL_Success(), message=DL_Success().description, payload=scarab.Param()):
        Exception.__init__(self)
        set_reply_cache(return_code, message, payload)
