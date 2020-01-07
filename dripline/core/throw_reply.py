__all__ = []

import scarab
from _dripline.core import _ThrowReply, DL_Success, set_reply_cache

#from _dripline.core import _Base

__all__.append('ThrowReply')
class ThrowReply(Exception):
    def __init__(self, return_code=DL_Success(), message=DL_Success().description, payload=scarab.Param()):
        Exception.__init__(self)
        set_reply_cache(return_code, message, payload)
        #self.internal = _ThrowReply(return_code, payload)
        #self.internal.return_message(message)
        #set_reply_cache(self)



#__all__.append('Derived')
#class Derived(_Base):
#    def label(self):
#        return "Derived"
#
#    def throw_exception(self):
#        raise Exception('Thrown from derived')

#__all__.append('Derived2')
#class Derived2(_Base):
#    def label(self):
#        return "Derived2"
#
#    def throw_exception(self):
#        raise ThrowReply()


