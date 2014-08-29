# boilerplate needed to get paths right
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest
from config import Config

@pytest.fixture
def good_conf():
    filename = myPath + '/test_config.yaml'
    c = Config(filename)
    return c

def test_node_name(good_conf):
    assert good_conf.nodename == 'baz'

def test_host_config(good_conf):
    assert good_conf.broker == 'foo.bar.org'

def test_config_has_instruments(good_conf):
    assert good_conf.instrument_count() == 2

def test_config_instrument_1(good_conf):
    instrument = good_conf.instruments['box_with_knobs']
    assert instrument['model'] == 'black_magic_12'

def test_config_instrument_2(good_conf):
    instrument = good_conf.instruments['another_box_with_knobs']
    assert instrument['model'] == 'black_magic_13'
