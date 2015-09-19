'''
Base and derived classes for implementing the Project 8 wire protocol.

The Message class should implement the protocol generally, and the types of emssage represent types of messages that dripline expects to send, possibly with extra restrictions.

These classes are responsible both for enforcing compliance with the protocol, and with encoding and decoding support formats for AMQP payloads (currently json and yaml).
'''


from __future__ import absolute_import

# standard libs
from datetime import datetime
import json
import os
import pwd
import socket

# 3rd party libs
import msgpack

# internal imports
from . import constants
from . import exceptions
#from .utilities import fancy_doc
from .. import __version__, __commit__

import inspect

import logging
logger = logging.getLogger(__name__)


__all__ = ['ReplyMessage',
           'RequestMessage',
           'InfoMessage',
           'AlertMessage',
           'Message']


class Message(dict, object):
    '''Base message/wire protocol class

    Base class for enforcing the Project 8 wire protocol and responsible for encoding and decoding.

    Any actual instance should be a subclass of this class.

    '''

    def __init__(self,
                 timestamp=None,
                 payload=None,
                 sender_info=None,
                 **kwargs):
        '''
        timestamp (str): string representation of datetime object, reflecting the creation time of this message. Note that if the default value of None is provided, the current time will be used.
        payload (any): actual message content, usually a dict
        sender_info (dict): several fields providing information about the system which originally generated a message.
        '''
        for key,value in kwargs.items():
            logger.warning('got unexpected kwarg <{}> with value <{}>\nit will be dropped'.format(key, value))
        if timestamp is None:
            self.timestamp = datetime.utcnow().strftime(constants.TIME_FORMAT)
        else:
            self.timestamp = timestamp
        self.payload = payload
        if sender_info is None:
            this_exe = inspect.stack()[-1][1]
            this_host = socket.gethostname()
            this_username = pwd.getpwuid(os.getuid())[0]
            self.sender_info = {'package': 'dripline',
                                'exe': this_exe,
                                'version': __version__,
                                'commit': __commit__,
                                'hostname': this_host,
                                'username': this_username,
                               }
        else:
            self.sender_info = sender_info

    def __str__(self):
        return json.dumps(self, indent=4)

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
    def return_msg(self):
        return self['return_message']
    @return_msg.setter
    def return_msg(self, value):
        self['return_message'] = value

    @property
    def msgtype(self):
        return None
    @msgtype.setter
    def msgtype(self, value):
        raise AttributeError('msgtype cannot be changed')

    @property
    def sender_info(self):
        return self['sender_info']
        this_exe = inspect.stack()[-1][1]
        return {'package': 'dripline',
                'exe': this_exe,
                'version': __version__,
                'commit': __commit,
               }
    @sender_info.setter
    def sender_info(self, value):
        self['sender_info'] = value

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
            raise exceptions.DriplineDecodingError('encoding <{}> not recognized'.format(encoding))

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


#@fancy_doc
class ReplyMessage(Message):
    '''
    Derrived class for Reply type messages
    '''
    def __init__(self,
                 retcode=None,
                 return_msg=None,
                 **kwargs):
        '''
        retcode (int): indicates return value and/or error code (see exceptions)
        return_msg (str): human-readable explanation of the return code
        '''
        if retcode is None:
            retcode = 0
        if return_msg is None:
            return_msg = ''
        self.retcode = retcode
        self.return_msg = return_msg
        Message.__init__(self, **kwargs)

    @property
    def msgtype(self):
        return constants.T_REPLY


#@fancy_doc
class RequestMessage(Message):

    def __init__(self, msgop, **kwargs):
        '''
        msgop (int): only meaningful for Request messages, indicates the operation being requested
        '''
        self.msgop = msgop
        Message.__init__(self, **kwargs)

    @property
    def msgtype(self):
        return constants.T_REQUEST


#@fancy_doc
class InfoMessage(Message):
    @property
    def msgtype(self):
        return constants.T_INFO


#@fancy_doc
class AlertMessage(Message):
    @property
    def msgtype(self):
        return constants.T_ALERT
