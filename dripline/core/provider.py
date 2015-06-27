from __future__ import absolute_import

from .endpoint import Endpoint#, fancy_init_doc
from .spime import Spime

import logging
logger = logging.getLogger(__name__)

__all__ = ['Provider']


#@fancy_init_doc
class Provider(Endpoint):
    '''
    Abstraction/interpretation layer for grouping endpoints and/or representing an instrument.
    Providers must implement a send() which takes "RAW" messages, converts them as needed, sends them to hardware (or another provider), receives and parses the response, and sends a meaningful result back.
    '''

    def __init__(self, **kwargs):
        Endpoint.__init__(self, **kwargs)
        self._endpoints = {}

    def add_endpoint(self, endpoint):
        if endpoint.name in self._endpoints.keys():
            logger.warning('endpoint "{}" already present'.format(endpoint.name))
            return
        self._endpoints.update({endpoint.name:endpoint})
        endpoint.provider = self

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
                    logger.warning('got warning: {}'.format(err.message))
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
