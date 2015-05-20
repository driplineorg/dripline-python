'''
Implementation for the agilent 34461 DMM
'''

from __future__ import absolute_import
import socket

from ..core import Provider, Endpoint

__all__ = ['agilent34461a', 'agilent34461a_voltage_input']


class agilent34461a(Provider):
    module_key = 'agilent34461a'
    def __init__(self, name, ip_addr='10.0.0.60', scpi_port=5025, **kwargs):
        #self.name = name
        Provider.__init__(self, name=name, **kwargs)
        self.sensors = {}
        self.ip_addr = ip_addr
        self.scpi_port = scpi_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip_addr,scpi_port))

    def add_endpoint(self, sensor):
        self.sensors[sensor.name] = sensor
        sensor.set_provider(self)

    def endpoint(self, sensorname):
        return self.sensors[sensorname]

    def list_endpoints(self):
        return self.sensors.keys()

    def send_sync(self, to_send):
        self.sock.send(to_send + '\r\n')
        data = self.sock.recv(1024)
        return data


class agilent34461a_voltage_input(Endpoint):
    module_key = 'agilent34461a_voltage_input'
    def __init__(self,name,*args,**kwargs):
        self.name = name

    def on_get(self):
        result = self.provider.send_sync("MEAS:VOLT:DC?")
        return result

    def on_set(self):
        raise NotImplementedError

    def on_config(self):
        raise NotImplementedError

    def provider(self):
        return self.provider

    def set_provider(self, provider):
        self.provider = provider
