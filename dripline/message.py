import constants
import msgpack
from utils import switch
from abc import ABCMeta, abstractproperty, abstractmethod

empty_msg_dict = {
    'msgtype': None,
    'msgop': None,
    'target': None,
    'timestamp': None,
    'payload': None,
    'exceptions': None
}

class Message(object):
    __metaclass__ = ABCMeta

    def __init__(self, msgop = None, target = None, timestamp = None, payload = None, exceptions = None):
        self.msgop = msgop
        self.target = target
        self.timestamp = timestamp
        self.payload = payload
        self.exceptions = exceptions
    
    @classmethod
    def from_dict(cls, msg):
        res = empty_msg_dict.copy()
        res.update(msg)

        msgtype = res.pop('msgtype', None)

        for case in switch(msgtype):
            if case(constants.T_REPLY):
                return ReplyMessage(**res)
            if case(constants.T_REQUEST):
                return RequestMessage(**res)
            if case(constants.T_INFO):
                return InfoMessage(**res)
            if case(constants.T_ALERT):
                return AlertMessage(**res)
            else:
                raise ValueError('msgtype must be defined as in spec!')

    @classmethod
    def from_msgpack(cls, msg):
        return msgpack.unpackb(msg, object_hook=cls.from_dict)

    def to_msgpack(self):
        d = {
            'msgtype': self.msgtype,
            'msgop': self.msgop,
            'target': self.target,
            'timestamp': self.timestamp,
            'payload': self.payload,
            'exceptions': self.exceptions,
        }
        return msgpack.packb(d)
    
class ReplyMessage(Message):
    @property
    def msgtype(self):
        return constants.T_REPLY

class RequestMessage(Message):
    @property
    def msgtype(self):
        return constants.T_REQUEST

class InfoMessage(Message):
    @property
    def msgtype(self):
        return constants.T_INFO

class AlertMessage(Message):
    @property
    def msgtype(self):
        return constants.T_ALERT
