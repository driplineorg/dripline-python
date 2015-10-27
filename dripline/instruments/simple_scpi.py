from __future__ import absolute_import

import socket
from ..core import Provider, Endpoint#, AutoReply

__all__ = ['simple_scpi_instrument', 'simple_scpi_sensor']

class simple_scpi_instrument(Provider):
    def __init__(self, name, ip_addr='10.0.0.60', scpi_port=5025, **kwargs):
        Provider.__init__(self, name=name)
        self.ip_addr = ip_addr
        self.scpi_port = scpi_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip_addr,scpi_port))

    def list_endpoints(self):
        return self.endpoints.keys()

    def endpoint(self, endpoint):
        if endpoint in self.list_endpoints():
            return self.endpoints[endpoint]

    def send_sync(self, to_send):
        self.sock.send(to_send + '\r\n')
        data = self.sock.recv(1024)
        return data

class simple_scpi_sensor(Endpoint):
    def __init__(self, name, on_get=None, on_set=None):
        self.name = name
        self._provider = None
        self._on_get = on_get
        self._on_set = on_set

    def on_get(self):
        result = self._provider.send(self._on_get)
        return result

    def on_set(self, value):
        result = self._provider.send(self._on_set.format(value))
        return result

    def on_config(self):
        raise NotImplementedError

    def provider(self):
        return self._provider

    def set_provider(self, provider):
        self._provider = provider
