from abc import ABCMeta, abstractmethod

__all__ = ['Provider']

class Provider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def add_endpoint(self, endpoint):
        raise NotImplementedError

    @abstractmethod
    def endpoint(self, endpoint):
        raise NotImplementedError

    @abstractmethod
    def list_endpoints(self):
        raise NotImplementedError
