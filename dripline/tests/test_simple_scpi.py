import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import mock

import pytest
from simple_scpi import SimpleSCPISensor, SimpleSCPIInstrument
from factory import constructor_registry

@pytest.fixture
def good_get_set():
	return {'on_get': 'MEAS:VOLT:DC?', 'on_set': 'MEAS:VOLT:DC {}'}

def test_simple_scpi_get(good_get_set):
	class MockedInstrument(object):
		def __init__(self):
			pass
		def send_sync(self, data):
			return 'MOCKED'

	s = SimpleSCPISensor('scpi',**good_get_set)
	s.set_provider(MockedInstrument())
	assert s.on_get() == 'MOCKED'

def test_simple_scpi_set(good_get_set):
	class MockedInstrument(object):
		def __init__(self):
			pass
		def send_sync(self, data):
			return 'MOCKED'
	s = SimpleSCPISensor('scpi',**good_get_set)
	s.set_provider(MockedInstrument())
	assert s.on_set(1.0) == 'MOCKED'

def test_simple_scpi_registry(good_get_set):
	class MockedInstrument(object):
		def __init__(self):
			pass
		def send_sync(self, data):
			return 'MOCKED'

	c = constructor_registry['simple_scpi_sensor']
	s = c('scpi', **good_get_set)
	s.set_provider(MockedInstrument())
	assert s.on_get() == 'MOCKED'
	assert s.on_set(9) == 'MOCKED'

def test_simple_scpi_instrument(good_get_set, monkeypatch):
	class MockedSocket(object):
		def __init__(self, a, b):
			pass
		def connect(self, a):
			return None

	monkeypatch.setattr('socket.socket', MockedSocket)
	monkeypatch.setattr('socket.socket.connect', MockedSocket.connect)

	s = SimpleSCPIInstrument('nobody')
	assert s.name == 'nobody'

def test_simple_scpi_instrument_add(good_get_set, monkeypatch):
	class MockedSocket(object):
		def __init__(self, a, b):
			pass
		def connect(self, a):
			return None

	monkeypatch.setattr('socket.socket', MockedSocket)
	monkeypatch.setattr('socket.socket.connect', MockedSocket.connect)

	instr_c  = constructor_registry['simple_scpi_instrument']
	i = instr_c('nobody')
	sensor_c = constructor_registry['simple_scpi_sensor']
	s = sensor_c('scpi',**good_get_set)

	i.add_endpoint(s)
	assert i.endpoint('scpi') == s