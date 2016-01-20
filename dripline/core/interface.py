'''
Creating an interface class, intended for use in scripting runs
'''

from __future__ import absolute_import

import logging

from .constants import *
from .exceptions import exception_map, DriplineTimeoutError, DriplineDeprecated
from .message import ReplyMessage, RequestMessage
from .service import Service
from .utilities import fancy_doc


__all__ = []

logger = logging.getLogger(__name__)

__all__.append('Interface')
@fancy_doc
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
    
    def _send_request(self, target, msgop, payload, timeout=None, lockout_key=False):
        request = RequestMessage(msgop=msgop, payload=payload)
        request_kwargs = {'target':target,
                          'request':request,
                         }
        if timeout is not None:
            request_kwargs.update({'timeout':timeout})
        if lockout_key:
            request.lockout_key = lockout_key
        try:
            reply = self.send_request(**request_kwargs)#target, request)
        except DriplineTimeoutError as err:
            reply = ReplyMessage(retcode=DriplineTimeoutError.retcode, payload=str(err))
        if self._confirm_retcode:
            if not reply.retcode == 0:
                raise exception_map[reply.retcode](reply.return_msg)
        return reply

    def get(self, endpoint, timeout=None):
        msgop = OP_GET
        payload = {'values':[]}
        request_args = {'target': endpoint,
                        'msgop':msgop,
                        'payload':payload
                       }
        if timeout is not None:
            request_args.update({'timeout':timeout})
        reply = self._send_request(**request_args)
        return reply

    def set(self, endpoint, value, lockout_key=False, **kwargs):
        msgop = OP_SET
        payload = {'values':[value]}
        payload.update(kwargs)
        reply = self._send_request(target=endpoint, msgop=msgop, payload=payload, lockout_key=lockout_key)
        return reply

    def config(self, endpoint, property, value=None):
        raise DriplineDeprecated('op config is deprecated, you should use get/set endpoint.<property>')
        #msgop = OP_CONFIG
        #payload = {'values':[property]}
        #if value is not None:
        #    payload['values'].append(value)
        #reply = self._send_request(target=endpoint, msgop=msgop, payload=payload)
        #return reply

    def cmd(self, endpoint, method_name, lockout_key=False, *args, **kwargs):
        '''
        Send a request to call endpoint.methodname(*args, **kwargs)

        Note that while a request message expects the method name to be provided as an RKS,
        here it is a separate argument which is combined with the endpoint name.
        '''
        msgop = OP_CMD
        payload = {'values': list(args)}
        payload.update(kwargs)
        target = endpoint + '.' + method_name
        reply = self._send_request(target=target, msgop=msgop, payload=payload, lockout_key=lockout_key)
        return reply


__all__.append('_InternalInterface')
@fancy_doc
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
