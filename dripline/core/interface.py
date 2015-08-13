'''
Creating an interface class, intended for use in scripting runs
'''

from __future__ import absolute_import

import logging

from .service import Service
from .constants import *
from .message import RequestMessage


__all__ = []

logger = logging.getLogger(__name__)

__all__.append('Interface')
class Interface(Service):
    def __init__(self, amqp_url, name=None):
        if name is None:
            name = 'scripting_interface_' + str(uuid.uuid4())[1:12]
        Service.__init__(self, amqp_url, exchange='requests', keys='', name=name)
    
    def _send_request(self, target, msgop, payload):
        request = RequestMessage(msgop=msgop, payload=payload)
        reply = self.send_request(target, request)
        return reply

    def get(self, endpoint):
        msgop = OP_GET
        payload = {'values':[]}
        self._send_request(target=endpoint, msgop=msgop, payload=payload)

    def set(self, endpoint, value):
        msgop = OP_SET
        payload = {'values':[value]}
        self._send_request(target=endpoint, msgop=msgop, payload=payload)

    def config(self, endpoint, property, value=None):
        msgop = OP_CONFIG
        payload = {'values':[property]}
        if value is not None:
            payload['values'].append(value)
        self._send_request(target=endpoint, msgop=msgop, payload=payload)

    def cmd(self, endpoint, method_name, *args, **kwargs):
        msgop = OP_CMD
        payload = {'values':[method_name] + args}
        payload.update(kwargs)
        self._send_request(target=endpoint, msgop=msgop, payload=payload)


__all__.append('_InternalInterface')
class _InternalInterface(Interface):
    def __init__(self, *args, **kwargs):
        if kwargs['name'] is None:
            kwargs['name'] = 'internal_interface_' + str(uuid.uuid4())[1:12]
        Interface.__init__(self, *args, **kwargs)

    def send(self, endpoint, *commands):
        msgop = OP_SEND
        payload = {'values': commands}
        self._send_request(target=endpoint, msgop=msgop, payload=payload)
