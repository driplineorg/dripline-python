'''
Creating an interface class, intended for use in scripting runs
'''

from __future__ import absolute_import

import logging

from .constants import *
from .exceptions import exception_map, DriplineTimeoutError
from .message import ReplyMessage, RequestMessage
from .service import Service


__all__ = []

logger = logging.getLogger(__name__)

__all__.append('Interface')
class Interface(Service):
    def __init__(self, amqp_url, name=None, confirm_retcodes=True):
        '''
        Keywords:
            confirm_retcodes (bool): if True and if retcode!=0, raise exception
        '''
        if name is None:
            name = 'scripting_interface_' + str(uuid.uuid4())[1:12]
        Service.__init__(self, amqp_url, exchange='requests', keys='', name=name)
        self._confirm_retcode = confirm_retcodes
    
    def _send_request(self, target, msgop, payload):
        request = RequestMessage(msgop=msgop, payload=payload)
        try:
            reply = self.send_request(target, request)
        except DriplineTimeoutError as err:
            reply = ReplyMessage(retcode=DriplineTimeoutError.retcode, payload=str(err))
        if self._confirm_retcode:
            if not reply.retcode == 0:
                raise exception_map[reply.retcode]
        return reply

    def get(self, endpoint):
        msgop = OP_GET
        payload = {'values':[]}
        reply = self._send_request(target=endpoint, msgop=msgop, payload=payload)
        return reply

    def set(self, endpoint, value):
        msgop = OP_SET
        payload = {'values':[value]}
        reply = self._send_request(target=endpoint, msgop=msgop, payload=payload)
        return reply

    def config(self, endpoint, property, value=None):
        msgop = OP_CONFIG
        payload = {'values':[property]}
        if value is not None:
            payload['values'].append(value)
        reply = self._send_request(target=endpoint, msgop=msgop, payload=payload)
        return reply

    def cmd(self, endpoint, method_name, *args, **kwargs):
        msgop = OP_CMD
        payload = {'values':[method_name] + args}
        payload.update(kwargs)
        reply = self._send_request(target=endpoint, msgop=msgop, payload=payload)
        return reply


__all__.append('_InternalInterface')
class _InternalInterface(Interface):
    def __init__(self, **kwargs):
        if kwargs['name'] is None:
            kwargs['name'] = 'internal_interface_' + str(uuid.uuid4())[1:12]
        Interface.__init__(self, confirm_retcodes=False, **kwargs)

    def send(self, endpoint, *commands):
        msgop = OP_SEND
        payload = {'values': commands}
        reply = self._send_request(target=endpoint, msgop=msgop, payload=payload)
        return reply
