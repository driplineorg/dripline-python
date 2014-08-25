# boilerplate needed to get paths right
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest
from config import Config
from factory import constructor_registry
from node import Node
from simple_scpi import SimpleSCPISensor

@pytest.fixture
def good_conf():
	filename = myPath + '/test_graph.yaml'
	c = Config(filename)
	return c 

@pytest.fixture
def bare_conf():
	filename = myPath + '/bare_config.yaml'
	c = Config(filename)
	return c

@pytest.fixture
def abc_sensor():
	s = SimpleSCPISensor('abc')
	return s

@pytest.fixture
def dmm0(monkeypatch):
	class MockedSocket(object):
		def __init__(self, a, b):
			pass
		def connect(self, a):
			return None
	monkeypatch.setattr('socket.socket', MockedSocket)
	monkeypatch.setattr('socket.socket.connect', MockedSocket.connect)
	c = constructor_registry['agilent34461a']
	return c('dmm0')

@pytest.fixture
def dmm1(monkeypatch):
	class MockedSocket(object):
		def __init__(self, a, b):
			pass
		def connect(self, a):
			return None

	monkeypatch.setattr('socket.socket', MockedSocket)
	monkeypatch.setattr('socket.socket.connect', MockedSocket.connect)
	c = constructor_registry['agilent34461a']
	return c('dmm1')

@pytest.fixture
def dcv():#
	c = constructor_registry['agilent34461a_voltage_input']
	return c('dcv')

def test_node_building_basic(good_conf):
	node = Node(good_conf)
	assert node.nodename() == 'baz'

def test_node_provider_add(bare_conf,dmm0):
	node = Node(bare_conf)
	node.add_provider(dmm0)
	assert node.provider_list() == ['dmm0']

def test_node_provider_double_add(bare_conf, dmm0, dmm1):
	node = Node(bare_conf)
	node.add_provider(dmm0)
	node.add_provider(dmm1)
	assert node.provider_list() == ['dmm0', 'dmm1']

def test_endpoint_add(bare_conf, dmm0, abc_sensor):
	node = Node(bare_conf)
	dmm0.add_endpoint(abc_sensor)
	node.add_provider(dmm0)
	assert node.provider_endpoints('dmm0') == ['abc']

def test_find_endpoint(bare_conf, dmm0, abc_sensor):
	node = Node(bare_conf)
	dmm0.add_endpoint(abc_sensor)
	node.add_provider(dmm0)
	assert node.locate_provider('abc') == dmm0

def test_call_endpoint_getter(bare_conf, dmm0, abc_sensor):
	node = Node(bare_conf)
	dmm0.add_endpoint(abc_sensor)
	node.add_provider(dmm0)

	p = node.locate_provider('abc')
	s = p.endpoint('abc')
	assert s.on_get() == None

def test_object_graph_building_instruments(good_conf, monkeypatch):
	class MockedSocket(object):
		def __init__(self, a, b):
			pass
		def connect(self, a):
			return None
	monkeypatch.setattr('socket.socket', MockedSocket)
	monkeypatch.setattr('socket.socket.connect', MockedSocket.connect)
	node = Node(good_conf)
	assert 'dmm0' in node.provider_list()
	assert 'dmm1' in node.provider_list()

def test_object_graph_building_sensors(good_conf, monkeypatch):
	class MockedSocket(object):
		def __init__(self, a, b):
			pass
		def connect(self, a):
			return None
	monkeypatch.setattr('socket.socket', MockedSocket)
	monkeypatch.setattr('socket.socket.connect', MockedSocket.connect)
	node = Node(good_conf)
	p0 = node.locate_provider('dmm0_dcv')
	p1 = node.locate_provider('dmm1_dcv')
	assert p0.name == 'dmm0'
	assert p1.name == 'dmm1'

def test_object_graph_building_getters(good_conf, monkeypatch):
	class MockedSocket(object):
		def __init__(self, a, b):
			pass
		def connect(self, a):
			return None

	monkeypatch.setattr('socket.socket', MockedSocket)
	monkeypatch.setattr('socket.socket.connect', MockedSocket.connect)
	node = Node(good_conf)
	p0 = node.locate_provider('dmm0_dcv')
	s0 = p0.endpoint('dmm0_dcv')
	p1 = node.locate_provider('dmm1_dcv')
	s1 = p1.endpoint('dmm1_dcv')
	p2 = node.locate_provider('dmm1_acv')
	s2 = p2.endpoint('dmm1_acv')
	assert s0.on_get() == 'MEAS:VOLT:DC?'
	assert s1.on_get() == 'MEAS:VOLT:DC?'
	assert s2.on_get() == 'MEAS:VOLT:AC?'
