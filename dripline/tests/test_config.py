# boilerplate needed to get paths right
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest
from dripline.core import Config

# This section tests that a "good" configuration, where "good" means
# that a sane configuration can be generated from the yaml file,
# generates a sane instance of Config.
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
    assert good_conf.provider_count() == 2

def test_config_instrument_1(good_conf):
    instrument = good_conf.providers['box_with_knobs']
    assert instrument['model'] == 'black_magic_12'

def test_config_instrument_2(good_conf):
    instrument = good_conf.providers['another_box_with_knobs']
    assert instrument['model'] == 'black_magic_13'

# This section tests that various bad configurations return
# the expected (very informative) errors.
def test_identical_endpoints_error():
    """Verify that identically named endpoints are forbidden.
    Should this be a ValueError for the key name?"""
    with pytest.raises(ValueError):
        Config(myPath + "/identical_names_conf.yaml")

def test_identical_endpoints_info():
    """The error should contain information about where in the
    configuration file the error occurred, and why.  In this case,
    the name is already taken by another endpoint which is local
    to this node.  The error should therefore indicate that the name
    `endpoint` is unavailable, because it is already reserved by
    another endpoint.  Furthermore, the endpoint which already has
    the name is called out along with its provider.  The error should
    contain the string \"(origin endpoint: provider/endpoint)\"."""
    with pytest.raises(ValueError) as excinfo:
        Config(myPath + "/identical_names_conf.yaml")
    assert "(origin provider: abc/a_provider/none)" in excinfo.value.message
