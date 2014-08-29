# boilerplate needed to get paths right
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest
from config import Config

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
    assert good_conf.instrument_count() == 2

def test_config_instrument_1(good_conf):
    instrument = good_conf.instruments['box_with_knobs']
    assert instrument['model'] == 'black_magic_12'

def test_config_instrument_2(good_conf):
    instrument = good_conf.instruments['another_box_with_knobs']
    assert instrument['model'] == 'black_magic_13'

# This section tests that various bad configurations return
# the expected (very informative) errors.
@pytest.fixture
def identical_names_conf():
    """A configuration that has two endpoints with the same name.
    Trying to generate a Config object from this configuration
    should produce an error indicating that another endpoint
    with that name is already defined, and point to the section that
    it is defined in.
    """
    conf = """
    broker: foo.bar.baz
    nodename: boff
    endpoints:
    - name: endpoint0
    - name: endpoint0
    """
    return conf

@pytest.mark.xfail(raises=ValueError)
def test_identical_endpoints_error(identical_names_conf):
    """Verify that identically named endpoints are forbidden.
    Should this be a ValueError for the key name?"""
    Config.from_string(identical_names_conf)

def test_identical_endpoints_info(identical_names_conf):
    """The error should contain information about where in the
    configuration file the error occurred, and why.  In this case,
    the name is already taken by another endpoint which is local
    to this node.  The error should therefore indicate that the name
    `endpoint` is unavailable, because it is already reserved by
    another endpoint.  Furthermore, the endpoint which already has
    the name is called out along with its provider.  The error should
    contain the string \"(origin endpoint: provider/endpoint)\"."""
    with pytest.raises(ValueError) as excinfo:
        Config.from_string(identical_names_conf)
        assert "(origin endpoint: boff/endpoint0)" in excinfo.value.message

@pytest.mark.xfail(raises=ValueError)
def test_identical_providers_error(identical_names_conf):
    """Verify that identically named providers are forbidden.
    Should this be a ValueError for the key name?"""
    Config.from_string(identical_names_conf)

def test_identical_providers_info(identical_names_conf):
    """Identical provider names is also an error.  The error message
    should contain the string \"(origin provider: provider_name)\"."""
    with pytest.raises(ValueError) as excinfo:
        Config.from_string(identical_names_conf)
        assert "(origin provider: provider0)" in excinfo.value.message





