from __future__ import absolute_import

from abc import ABCMeta, abstractmethod

import logging
logger = logging.getLogger(__name__)

__all__ = ['Provider']

class Provider(object):
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self.name = name
        self._endpoints = {}

    def add_endpoint(self, endpoint):
        if endpoint.name in self._endpoints.keys():
            logger.warning('endpoint "{}" already present'.format(endpoint.name))
            return
        self._endpoints.update({endpoint.name:endpoint})
        endpoint.provider = self
        logger.info('endpoint list is now: {}'.format(self._endpoints.keys()))

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
