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
def good_node(good_conf, monkeypatch):
    class MockedSocket(object):
        def __init__(self, *args):
            pass
        def connect(self, a):
            return None
        def send(self, x):
            return None
        def recv(self, x):
            return 'MOCKED'

    monkeypatch.setattr('socket.socket', MockedSocket)
    monkeypatch.setattr('socket.socket.connect', MockedSocket.connect)
    monkeypatch.setattr('socket.socket.send', MockedSocket.send)
    monkeypatch.setattr('socket.socket.recv', MockedSocket.recv)

    class MockedBlockingConnection(object):
        def __init__(self,a):
            pass
        def channel(self):
            def queue_declare(*args, **kwargs):
                class MockedMethod(object):
                    queue = None
                return type('__queue',(),{'method': MockedMethod()})()
            def queue_bind(*args, **kwargs):
                return None
            def basic_consume(*args, **kwargs):
                return None
            return type('__chan',(),{'queue_declare': queue_declare,
                                     'queue_bind': queue_bind,
                                     'basic_consume': basic_consume})()
        def close(self):
            return None


    monkeypatch.setattr('pika.BlockingConnection', MockedBlockingConnection)
    monkeypatch.setattr('pika.BlockingConnection.channel', MockedBlockingConnection.channel)
    monkeypatch.setattr('connection.Connection._setup_amqp',lambda x: None)

    node = Node(good_conf)
    return node

@pytest.fixture
def bare_node(bare_conf, monkeypatch):
    class MockedSocket(object):
        def __init__(self, *args):
            pass
        def connect(self, a):
            return None
        def send(self, x):
            return None
        def recv(self, x):
            return 'MOCKED'

    monkeypatch.setattr('socket.socket', MockedSocket)
    monkeypatch.setattr('socket.socket.connect', MockedSocket.connect)
    monkeypatch.setattr('socket.socket.send', MockedSocket.send)
    monkeypatch.setattr('socket.socket.recv', MockedSocket.recv)

    class MockedBlockingConnection(object):
        def __init__(self,a):
            pass
        def channel(self):
            def queue_declare(*args, **kwargs):
                class MockedMethod(object):
                    queue = None
                return type('__queue',(),{'method': MockedMethod()})()
            def queue_bind(*args, **kwargs):
                return None
            def basic_consume(*args, **kwargs):
                return None
            return type('__chan',(),{'queue_declare': queue_declare,
                                     'queue_bind': queue_bind,
                                     'basic_consume': basic_consume})()
        def close(self):
            return None

    monkeypatch.setattr('pika.BlockingConnection', MockedBlockingConnection)
    monkeypatch.setattr('pika.BlockingConnection.channel', MockedBlockingConnection.channel)
    monkeypatch.setattr('connection.Connection._setup_amqp',lambda x: None)
    node = Node(bare_conf)
    return node

@pytest.fixture
def dcv():#
    c = constructor_registry['agilent34461a_voltage_input']
    return c('dcv')

def test_node_building_basic(good_node):
    assert good_node.nodename() == 'baz'

def test_node_provider_add(bare_node,dmm0):
    bare_node.add_provider(dmm0)
    assert bare_node.provider_list() == ['dmm0']

def test_node_provider_double_add(bare_node, dmm0, dmm1):
    bare_node.add_provider(dmm0)
    bare_node.add_provider(dmm1)
    assert bare_node.provider_list() == ['dmm0', 'dmm1']

def test_endpoint_add(bare_node, dmm0, abc_sensor):
    dmm0.add_endpoint(abc_sensor)
    bare_node.add_provider(dmm0)
    assert bare_node.provider_endpoints('dmm0') == ['abc']

def test_find_endpoint(bare_node, dmm0, abc_sensor):
    dmm0.add_endpoint(abc_sensor)
    bare_node.add_provider(dmm0)
    assert bare_node.locate_provider('abc') == dmm0

def test_object_graph_building_instruments(good_node):
    assert 'dmm0' in good_node.provider_list()
    assert 'dmm1' in good_node.provider_list()

def test_object_graph_building_sensors(good_node):
    p0 = good_node.locate_provider('dmm0_dcv')
    p1 = good_node.locate_provider('dmm1_dcv')
    assert p0.name == 'dmm0'
    assert p1.name == 'dmm1'

def test_object_graph_building_getters(good_node):
    p0 = good_node.locate_provider('dmm0_dcv')
    s0 = p0.endpoint('dmm0_dcv')
    p1 = good_node.locate_provider('dmm1_dcv')
    s1 = p1.endpoint('dmm1_dcv')
    p2 = good_node.locate_provider('dmm1_acv')
    s2 = p2.endpoint('dmm1_acv')
    assert s0.on_get() == 'MOCKED'
    assert s1.on_get() == 'MOCKED'
    assert s2.on_get() == 'MOCKED'
