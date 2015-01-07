from abc import ABCMeta, abstractmethod

__all__ = ['Provider']

class Provider(object):
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self.name = name
        self._endpoints = []

    def add_endpoint(self, endpoint):
        endpoint.provider = self
        self._endpoints.append(endpoint)

    def endpoint(self, endpoint):
        raise NotImplementedError

    def list_endpoints(self):
        raise NotImplementedError
