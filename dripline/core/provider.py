from __future__ import absolute_import

from .endpoint import Endpoint

import logging
logger = logging.getLogger(__name__)

__all__ = ['Provider']

class Provider(Endpoint):

    def __init__(self, **kwargs):
        Endpoint.__init__(self, **kwargs)
        self._endpoints = {}

    def add_endpoint(self, endpoint):
        if endpoint.name in self._endpoints.keys():
            logger.warning('endpoint "{}" already present'.format(endpoint.name))
            return
        self._endpoints.update({endpoint.name:endpoint})
        endpoint.provider = self
        logger.info('endpoint list is now: {}'.format(self._endpoints.keys()))

    @property
    def logging_status(self):
        logger.info('getting logging status for endpoints of: {}'.format(self.name))
        results = []
        for (name,endpoint) in self._endpoints.items():
            logger.debug('getting status of: {}'.format(endpoint.name))
            if hasattr(endpoint, 'logging_status'):
                results.append((name,endpoint.logging_status))
        return results
    @logging_status.setter
    def logging_status(self, value):
        logger.info('setting logging status for endpoints of: {}'.format(self.name))
        results = []
        for (name,endpoint) in self._endpoints.items():
            logger.debug('trying to set for: {}'.format(endpoint.name))
            if hasattr(endpoint, 'logging_status'):
                results.append((name, setattr(endpoint, 'logging_status', value)))
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
