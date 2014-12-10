from abc import ABCMeta, abstractmethod

__all__ = ['Provider']

class Provider(object):
    __metaclass__ = ABCMeta

    def add_endpoint(self, endpoint):
        raise NotImplementedError

    def endpoint(self, endpoint):
        raise NotImplementedError

    def list_endpoints(self):
        raise NotImplementedError
