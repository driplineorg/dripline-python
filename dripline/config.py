""" config.py

This module contains the definition of the Config class.  The Config class
is the in-memory representation of the configuration of a dripline node.

"""

from yaml import safe_load


class Config(object):
    """
    The Config class contains all of the configuration data that is relevant
    to a dripline node, and is in fact how a dripline object graph is created.
    An instance of Config is created from a YAML string which describes a
    hierarchical graph of objects.  Each object has a unique name, and has zero
    or more descendents which form a tree-like structure.  The node level object
    may have descendents which are Providers (see provider.py) or Endpoints
    (see endpoint.py), and Providers may have descendents which are Endpoints.

    The Config object is responsible for the run-time checking of the YAML
    document which describes the dripline node configuration.  The rules which
    are checked are straightforward:

    * Names within categories must be unique - no two providers may have the
        same name, and no two endpoints may have the same name.

    * No object may have a name which contains a period.

    * Every object must be constructable.  This means that there is a
        module or function which can be called by dripline at runtime to handle
        requests which are addressed to that object.

    With these considerations in mind, the following YAML description of a
    dripline node is acceptable:

        nodename: example
        broker: foo.bar.baz
        providers:
        - name: provider0
          module: a_provider_module
          endpoints:
          - name: endpoint0
            module: an_endpoint_module
          - name: endpoint1
            module: another_endpoint_module
        - name: provider1
          module: a_provider_module
          endpoints:
          - name: endpoint2
            module: an_endpoint_module
          - name: endpoint3
            module: yet_another_endpoint_module

    For further examples of configuration files, see the configuration.yaml
    file in the examples directory.
    # TODO configuration.yaml file a la rebar.config demo file.

    """

    def __init__(self, config_file=None):
        self.nodename = None
        self.broker = None
        self.instruments = {}
        if config_file is not None:
            with open(config_file) as cf:
                self.from_yaml(cf.read())

    def instrument_count(self):
        if self.instruments is not None:
            return len(self.instruments.keys())
        else:
            return 0

    def from_yaml(self, yaml_string):
        rep = safe_load(yaml_string)
        self.nodename = rep['nodename']
        self.broker = rep['broker']
        if 'instruments' in rep:
            for instrument in rep['instruments']:
                instr_name = instrument.pop('name')
                if self.instruments.has_key(instr_name):
                    msg = """
                    duplicate definition: provider with name {} already defined!
                    (origin provider: {}/{})
                    """.format(instr_name, self.nodename, instr_name)
                    raise ValueError(msg)

                # TODO repeat the check inside the provider to catch duplicate
                # endpoint names.
                self.instruments[instr_name] = instrument
        else:
            self.instruments = None
