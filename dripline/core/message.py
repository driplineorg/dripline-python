'''
Meta and derived classes for dripline messages
'''


from __future__ import absolute_import

# standard libs
from abc import ABCMeta
from datetime import datetime
import json

# 3rd party libs
import msgpack

# internal imports
from . import constants

__all__ = ['ReplyMessage', 'RequestMessage', 'InfoMessage', 'AlertMessage',
           'Message']

import logging
logger = logging.getLogger(__name__)

class Message(dict, object):
    '''
    metaclass for dripline messages
    '''
    __metaclass__ = ABCMeta

    def __init__(self, msgop=None, timestamp=None, payload=None, retcode=None):
        if msgop is not None:
            self.msgop = msgop
        if timestamp is None:
            self.timestamp = datetime.utcnow().strftime(constants.TIME_FORMAT)
        else:
            self.timestamp = timestamp
        self.payload = payload
        self.retcode = retcode

    @property
    def msgop(self):
        return self['msgop']
    @msgop.setter
    def msgop(self, value):
        self['msgop'] = int(value)

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
    def retcode(self):
        return self['retcode']
    @retcode.setter
    def retcode(self, value):
        self['retcode'] = value

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
            msg_type = int(msg_dict.pop('msgtype'))
            logger.debug('msgtype is {}'.format(msg_type))
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

    @classmethod
    def from_encoded(cls, msg, encoding):
        if encoding.endswith('json'):
            return cls.from_json(msg)
        elif encoding.endswith('msgpack'):
            return cls.from_msgpack(msg)
        else:
            raise ValueError('encoding <{}> not recognized'.format(encoding))

    def to_msgpack(self):
        temp_dict = self.copy()
        temp_dict.update({'msgtype': self.msgtype})
        return msgpack.packb(temp_dict)

    def to_json(self):
        temp_dict = self.copy()
        temp_dict.update({'msgtype': self.msgtype})
        return json.dumps(temp_dict)

    def to_encoding(self, encoding):
        if encoding.endswith('json'):
            return self.to_json()
        elif encoding.endswith("msgpack"):
            return self.to_msgpack()
        else:
            raise ValueError('encoding <{}> not recognized'.format(encoding))


class ReplyMessage(Message):
    '''
    Derrived class for Reply type messages
    '''
    def __init__(self, retcode=None, **kwargs):
        if retcode is None:
            retcode=0
        kwargs.update({'retcode':retcode})
        Message.__init__(self, **kwargs)

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
