import pytest
import msgpack
import constants as dc
from message import RequestMessage, Message

# boilerplate needed to get paths right
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

@pytest.fixture
def basic_request_msg():
    d = {
        'msgtype': dc.T_REQUEST,
        'msgop': dc.OP_SENSOR_GET,
        'target': 'foo'
    }
    return d

def test_message_packing_basic(basic_request_msg):
    m = msgpack.packb(basic_request_msg)
    assert msgpack.unpackb(m) == basic_request_msg

def test_message_from_msgpack_basic(basic_request_msg):
    m = msgpack.packb(basic_request_msg)
    up = Message.from_msgpack(m)

    assert up.msgtype == dc.T_REQUEST
    assert up.msgop == dc.OP_SENSOR_GET
    assert up.target == 'foo'

def test_msgpack_from_message_basic(basic_request_msg):
    msg = Message.from_dict(basic_request_msg)
    msg.set_msgop = dc.OP_SENSOR_GET
    msg.set_target = 'bar'

    p = msg.to_msgpack()
    up = Message.from_msgpack(p)
    assert up.msgtype == dc.T_REQUEST
    assert up.msgop == dc.OP_SENSOR_GET
    assert up.target == 'foo'
