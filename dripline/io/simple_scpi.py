from sensor import AutoReply
from factory import constructor_registry as reg

import socket
from provider import Provider

class SimpleSCPIInstrument(Provider):
    def __init__(self, name, ip_addr='10.0.0.60', scpi_port=5025):
        self.name = name
        self.endpoints = {}
        self.ip_addr = ip_addr
        self.scpi_port = scpi_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip_addr,scpi_port))

    def add_endpoint(self, endpoint):
        self.endpoints[endpoint.name] = endpoint
        endpoint.set_provider(self)

    def list_endpoints(self):
        return self.endpoints.keys()

    def endpoint(self, endpoint):
        if endpoint in self.list_endpoints():
            return self.endpoints[endpoint]

    def send_sync(self, to_send):
        self.sock.send(to_send + '\r\n')
        data = self.sock.recv(1024)
        return data

class SimpleSCPISensor(AutoReply):
    def __init__(self,name,on_get=None,on_set=None):
        self.name = name
        self._provider = None
        self._on_get = on_get
        self._on_set = on_set

    def on_get(self):
        result = self._provider.send_sync(self._on_get)
        return result

    def on_set(self, value):
        result = self._provider.send_sync(self._on_set.format(value))
        return result

    def on_config(self):
        raise NotImplementedError

    def provider(self):
        return self._provider

    def set_provider(self, provider):
        self._provider = provider

reg['simple_scpi_instrument'] = SimpleSCPIInstrument
reg['simple_scpi_sensor'] = SimpleSCPISensor
