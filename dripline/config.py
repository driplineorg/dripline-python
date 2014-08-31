""" config.py

This module contains the definition of the Config class.  The Config class
is the in-memory representation of the configuration of a dripline node.

"""

from yaml import safe_load


class Config(object):

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
