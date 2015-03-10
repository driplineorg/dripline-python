""" kv_store.py
A simple key-value store which is a dripline provider.
The endpoints of this provider are associated with
keys, and are determined by the configuration file.
For example, if the configuration file has a provider
section that looks like this:
providers:
    - name: kv_example
      module: kv_store
      endpoints:
        -name: 'foo'
         module: 'kv_store_key'
        -name: 'bar'
         module: 'kv_store_key'
        -name: 'baz'
         module: 'kv_store_key'
Then the KV store will have three keys, foo, bar, and
baz, which are associated with it.  They can be addressed
as such on the network, or can also be addressed using their
fully qualified hierarchical address e.g. somenode.kv.foo.
"""

from __future__ import absolute_import
import logging

from ..core import Provider, Spime, calibrate

__all__ = ['kv_store', 'kv_store_key']


logger = logging.getLogger(__name__)
class kv_store(Provider):
    """
    The KV store.  This is just a wrapper around a dict.
    """
    def __init__(self, **kwargs):
        Provider.__init__(self, **kwargs)

    def endpoint(self, endpoint):
        """
        Return the endpoint associated with some key.
        """
        return self.endpoints[endpoint]

    def list_endpoints(self):
        """
        List all endpoints associated with this KV store.
        This is the same as enumerating the keys in the
        dict.
        """
        return self.keys()


class kv_store_key(Spime):
    """
    A key in the KV store.
    """
    def __init__(self, initial_value=None, **kwargs):
        Spime.__init__(self, **kwargs)
        self._value = initial_value
        self.get_value = self.on_get
        self.store_value = self.report_log

    @staticmethod
    def report_log(value):  
        logger.info("Should be logging value: {}\n".format(value))

    @calibrate
    def on_get(self):
        """
        Return the value associated with this
        key.
        """
        value = self._value
        return value

    def on_set(self, value):
        """
        Set the value associated with this key
        to some new value.
        """
        try:
            value = float(value)
            self._value = value
        except ValueError:
            raise ValueError('argument to set must be a float!')

    def on_config(self, attribute, value):
        """
        Configuring a key is not defined.
        """
        if hasattr(self, attribute):
            setattr(self, attribute, value)
            logger.info('set {} to {}'.format(attribute, value))
        else:
            raise AttributeError("No attribute: {}".format(attribute))
