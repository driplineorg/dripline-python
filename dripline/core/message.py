'''
Meta and derived classes for dripline messages
'''

from __future__ import absolute_import

__all__ = ['ReplyMessage', 'RequestMessage', 'InfoMessage', 'AlertMessage',
           'Message']

from datetime import datetime
import msgpack
from abc import ABCMeta

from . import constants


class Message(dict, object):
    '''
    metaclass for dripline messages
    '''
    __metaclass__ = ABCMeta

    def __init__(self, msgop=None, target=None, timestamp=None,
                 payload=None, exceptions=None):
        self.msgop = msgop
        self.target = target
        if timestamp is None:
            self.timestamp = datetime.utcnow().strftime(constants.TIME_FORMAT)
        else:
            self.timestamp = timestamp
        self.payload = payload
        self.exceptions = exceptions

    @property
    def msgop(self):
        return self['msgop']

    @msgop.setter
    def msgop(self, value):
        self['msgop'] = value

    @property
    def target(self):
        return self['target']

    @target.setter
    def target(self, value):
        self['target'] = value

    @property
    def timestamp(self):
        return self['timestamp']

    @timestamp.setter
    def timestamp(self, value):
        self['timestamp'] = value

    @property
    def payload(self):
        return self['payload']

    @payload.setter
    def payload(self, value):
        self['payload'] = value

    @property
    def exceptions(self):
        return self['exceptions']

    @exceptions.setter
    def exceptions(self, value):
        self['exceptions'] = value

    @property
    def msgtype(self):
        return None

    @msgtype.setter
    def msgtype(self, value):
        raise AttributeError('msgtype cannot be changed')

    @staticmethod
    def from_dict(msg_dict):
        subclasses_dict = {
            constants.T_REPLY: ReplyMessage,
            constants.T_REQUEST: RequestMessage,
            constants.T_ALERT: AlertMessage,
            constants.T_INFO: InfoMessage,
        }
        try:
            msg_type = msg_dict.pop('msgtype')
            return subclasses_dict[msg_type](**msg_dict)
        except KeyError:
            raise ValueError('msgtype must be defined as in spec!')

    @staticmethod
    def from_msgpack(msg):
        return msgpack.unpackb(msg, object_hook=Message.from_dict)

    def to_msgpack(self):
        temp_dict = self.copy()
        temp_dict.update({'msgtype': self.msgtype})
        return msgpack.packb(temp_dict)


class ReplyMessage(Message):
    '''
    Derrived class for Reply type messages
    '''
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
