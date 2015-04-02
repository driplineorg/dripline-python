'''
Meta and derived classes for dripline messages
'''

from __future__ import absolute_import

__all__ = ['ReplyMessage', 'RequestMessage', 'InfoMessage', 'AlertMessage',
           'Message']

# standard libs
from abc import ABCMeta
from datetime import datetime
import json
import logging

# 3rd party libs
import msgpack

# internal imports
from . import constants


logger = logging.getLogger(__name__)

class Message(dict, object):
    '''
    metaclass for dripline messages
    '''
    __metaclass__ = ABCMeta

    def __init__(self, msgop=None, timestamp=None,
                 payload=None, exceptions=None):
        self.msgop = msgop
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

    @classmethod
    def from_dict(cls, msg_dict):
        logger.debug('from_dict is: {}'.format(msg_dict))
        subclasses_dict = {
            constants.T_REPLY: ReplyMessage,
            constants.T_REQUEST: RequestMessage,
            constants.T_ALERT: AlertMessage,
            constants.T_INFO: InfoMessage,
        }
        try:
            msg_type = msg_dict.pop('msgtype')
            if 'target' in msg_dict:
                logger.warning('this is a hack')
                msg_dict.pop('target')
            return subclasses_dict[msg_type](**msg_dict)
        except KeyError:
            logger.debug('present keys are: {}'.format(msg_dict.keys()))
            raise ValueError('msgtype must be defined as in spec!')

    @classmethod
    def from_msgpack(cls, msg):
        message_dict = msgpack.unpackb(msg)
        message = cls.from_dict(message_dict)
        return message

    @classmethod
    def from_json(cls, msg):
        message_dict = json.loads(msg)
        message = cls.from_dict(message_dict)
        return message

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
