from yaml import safe_load

class Config(object):
	def __init__(self, config_file = None):
		if config_file is not None:
			with open(config_file) as cf:
				self.from_yaml(cf.read())

	def nodename(self):
		return self.nodename

	def instrument_count(self):
		if self.instruments is not None:
			return len(self.instruments.keys())
		else:
			return 0

	def from_yaml(self, yaml_string):
		rep = safe_load(yaml_string)	
		self.nodename = rep['nodename']
		self.broker = rep['broker']
		if rep.has_key('instruments'):
			self.instruments = {}
			for instrument in rep['instruments']:
				instr_name = instrument.pop('name')
				self.instruments[instr_name] = instrument
		else:
			self.instruments = None