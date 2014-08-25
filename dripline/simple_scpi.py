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

	def add_endpoint(self, endpoint):
		self.endpoints[endpoint.name] = endpoint

	def list_endpoints(self):
		return self.endpoints.keys()

	def endpoint(self, endpoint):
		if endpoint in self.list_endpoints():
			return self.endpoints[endpoint]

class SimpleSCPISensor(AutoReply):
	def __init__(self,name,on_get=None,on_set=None):
		self.name = name
		self._on_get = on_get
		self._on_set = on_set

	def on_get(self):
		return self._on_get

	def on_set(self, value):
		return self._on_set.format(value)

reg['simple_scpi_instrument'] = SimpleSCPIInstrument
reg['simple_scpi_sensor'] = SimpleSCPISensor