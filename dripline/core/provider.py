from __future__ import absolute_import

from .constants import *
from .endpoint import Endpoint
from .message import RequestMessage
from .spime import Spime
from .utilities import fancy_doc
from .exceptions import exception_map

import logging
logger = logging.getLogger(__name__)

__all__ = ['Provider']


@fancy_doc
class Provider(Endpoint):
    '''
    Abstraction/interpretation layer for grouping endpoints and/or representing an instrument.
    Providers must implement a send() which takes a list of messages, converts them as needed,
      sends them to hardware (or another provider), receives and parses the response, and sends a meaningful result back.
    '''

    def __init__(self, **kwargs):
        Endpoint.__init__(self, **kwargs)
        self._endpoints = {}

    def add_endpoint(self, endpoint):
        if endpoint.name in self._endpoints:
            logger.warning('endpoint "{}" already present'.format(endpoint.name))
            return
        self._endpoints.update({endpoint.name:endpoint})
        endpoint.provider = self

    def lock(self, *args, **kwargs):
        this_key = Endpoint.lock(self, *args, **kwargs)['key']
        kwargs.update({'lockout_key':this_key})
        for name, endpoint in self.endpoints.items():
            if endpoint.is_locked:
                continue
            logger.info('calling <{}>.lock'.format(name))
            endpoint.lock(*args, **kwargs)

    def unlock(self, *args, **kwargs):
        logger.info("hey hey hey hey")
        Endpoint.unlock(self, *args, **kwargs)
        for name, endpoint in self.endpoints.items():
            if name == self.name:
                continue
            logger.info('calling <{}>.unlock'.format(name))
            endpoint.unlock(*args, **kwargs)

    def on_send(self, *commands):
        these_cmds = commands
        return self.send(list(commands))

    def on_set(self, *args, **kwargs):
        return self._on_set(*args, **kwargs)

    @property
    def endpoint_names(self):
        return self._endpoints.keys()
    @endpoint_names.setter
    def endpoint_names(self, value):
        raise AttributeError('endpoint name list cannot be directly modified')

    @property
    def logging_status(self):
        if isinstance(self, Spime):
            return Spime.logging_status.fget(self)
        logger.info('getting logging status for endpoints of: {}'.format(self.name))
        results = []
        for (name,endpoint) in self._endpoints.items():
            logger.debug('getting status of: {}'.format(endpoint.name))
            if hasattr(endpoint, 'logging_status'):
                results.append((name,endpoint.logging_status))
        return results
    @logging_status.setter
    def logging_status(self, value):
        if isinstance(self, Spime):
            Spime.logging_status.fset(self, value)
            return
        logger.info('setting logging status for endpoints of: {}'.format(self.name))
        results = []
        for (name,endpoint) in self._endpoints.items():
            logger.debug('trying to set for: {}'.format(endpoint.name))
            if hasattr(endpoint, 'logging_status'):
                try:
                    results.append((name, setattr(endpoint, 'logging_status', value)))
                except Warning as err:
                    logger.warning('got warning: {}'.format(str(err)))
        return results

    @property
    def endpoints(self):
        return self._endpoints
    @endpoints.setter
    def endpoints(self, value):
        raise NotImplementedError('direct assignment not allowed')

    def endpoint(self, endpoint):
        raise NotImplementedError

    def list_endpoints(self):
        raise NotImplementedError

    def _send_request(self, target, msgop, payload, timeout=None, lockout_key=False, ignore_retcode=False):
        request = RequestMessage(msgop=msgop, payload=payload)
        request_kwargs = {'target':target, 'request':request}
        if timeout is not None:
            request_kwargs.update({'timeout':timeout})
        if lockout_key:
            request.lockout_key = lockout_key
        reply = self.service.send_request(**request_kwargs)
        if (not reply.retcode == 0) and (not ignore_retcode):
            raise exception_map[reply.retcode](reply.return_msg, result=reply.payload)
        return reply

    def get(self, target, timeout=None, ignore_retcode=False):
        request_args = {'target': target,
                        'msgop': OP_GET,
                        'payload': {'values':[]},
                        'timeout': timeout,
                       }
        reply = self._send_request(**request_args)
        return reply.payload

    def set(self, target, value, lockout_key=False, timeout=None, ignore_retcode=False):
        request_args = {'target': target,
                        'msgop': OP_SET,
                        'payload': {'values':[value]},
                        'lockout_key': lockout_key,
                        'timeout': timeout,
                       }
        reply = self._send_request(**request_args)
        return reply.payload

    def cmd(self, target, method_name, lockout_key=False, timeout=None, ignore_retcode=False, *args, **kwargs):
        request_args = {'target': endpoint + '.' + method_name,
                        'msgop':OP_CMD,
                        'payload': {'values': list(args)},
                        'lockout_key': lockout_key,
                        'timeout': timeout,
                       }
        reply = self._send_request(**request_args)
        return reply.payload
