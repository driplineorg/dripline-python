'''
Base and derived classes for implementing the Project 8 wire protocol.

The Message class should implement the protocol generally, and the types of emssage represent types of messages that dripline expects to send, possibly with extra restrictions.

These classes are responsible both for enforcing compliance with the protocol, and with encoding and decoding support formats for AMQP payloads (currently json).
'''


from __future__ import absolute_import

# standard libs
from datetime import datetime
import json
import os
import pwd
import socket
import traceback

# internal imports
from . import constants
from . import exceptions
from .utilities import fancy_doc
from .. import __version__, __commit__

import inspect

import logging
logger = logging.getLogger(__name__)


__all__ = ['ReplyMessage',
           'RequestMessage',
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
        # determine default sender info
        this_exe = inspect.stack()[-1][1]
        this_host = socket.gethostname()
        this_username = pwd.getpwuid(os.getuid())[0]
        this_sender_info = {'package': 'dripline',
                            'exe': this_exe,
                            'version': __version__,
                            'commit': __commit__,
                            'hostname': this_host,
                            'username': this_username,
                            'service_name': '',
                           }
        # replace default sender info with anything provided
        this_sender_info.update(sender_info or {})
        self.sender_info = this_sender_info
        #if self.msgtype == constants.T_REPLY:
        #    import ipdb;ipdb.set_trace()

    def __str__(self):
        return json.dumps(self, indent=4)

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
        return self['return_msg']
    @return_msg.setter
    def return_msg(self, value):
        self['return_msg'] = value

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
        }
        try:
            msg_type = int(msg_dict.pop('msgtype'))
            logger.debug('msgtype is {}'.format(msg_type))
            if 'target' in msg_dict:
                logger.warning('this is a hack & should not happen')
                msg_dict.pop('target')
            return subclasses_dict[msg_type](**msg_dict)
        except KeyError:
            logger.debug('present keys are: {}'.format(msg_dict.keys()))
            raise ValueError('msgtype must be defined as in spec!')

    @classmethod
    def from_json(cls, msg):
        logger.debug('original msg was: {}'.format(msg))
        try:
            message_dict = json.loads(msg)
            message = cls.from_dict(message_dict)
        except Exception as e:
            logger.error('error while decoding message:\n{}'.format(msg))
            raise exceptions.DriplineDecodingError('unable to decode message; received: {}'.format(msg))
        return message

    @classmethod
    def from_encoded(cls, msg, encoding):
        if encoding is None:
            logger.warning("No encoding is provided: will try with json")
            return cls.from_json(msg)
        elif encoding.endswith('json'):
            return cls.from_json(msg)
        else:
            raise exceptions.DriplineDecodingError('encoding <{}> not recognized'.format(encoding))

    def to_json(self):
        temp_dict = self.copy()
        temp_dict.update({'msgtype': self.msgtype})
        return json.dumps(temp_dict)

    def to_encoding(self, encoding):
        if encoding is None:
            logger.warning("No encoding is provided: will try with json")
            return self.to_json()
        elif encoding.endswith('json'):
            return self.to_json()
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

    @property
    def payload(self):
        return self['payload']
    @payload.setter
    def payload(self, value):
        if not isinstance(value, dict):
            value = {'values': [value]}
        self['payload'] = value


#@fancy_doc
class RequestMessage(Message):

    def __init__(self, msgop, lockout_key=None, **kwargs):
        '''
        msgop (int): only meaningful for Request messages, indicates the operation being requested
        '''
        self.msgop = msgop
        self.lockout_key = lockout_key
        Message.__init__(self, **kwargs)

    @property
    def msgop(self):
        return self['msgop']
    @msgop.setter
    def msgop(self, value):
        self['msgop'] = int(value)

    @property
    def msgtype(self):
        return constants.T_REQUEST

    @property
    def lockout_key(self):
        value = None
        if 'lockout_key' in self:
            value = self['lockout_key']
        return value
    @lockout_key.setter
    def lockout_key(self, value):
        self['lockout_key'] = value
        if value is None:
            self.pop('lockout_key')

#@fancy_doc
class AlertMessage(Message):
    @property
    def msgtype(self):
        return constants.T_ALERT
