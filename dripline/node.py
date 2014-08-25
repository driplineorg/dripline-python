from connection import Connection
from factory import constructor_registry as cr

import logging
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(ch)


class Node(object):
	def __init__(self, configuration):
		self.conf = configuration
		logger.info('initiating connection to broker {}'.format(self.conf.broker))
		self.conn = Connection(self.conf.broker)
		self.providers = {}
		self._build_object_graph()

	def nodename(self):
		return self.conf.nodename

	def _build_object_graph(self):
		if self.conf.instrument_count() > 0:
			for name, items in self.conf.instruments.iteritems():
				instr_model = items['model']
				constructor = cr[instr_model]

				logger.info('adding instrument {}'.format(name))
				obj = constructor(name, items)
				
				for sensor in items['sensors']:
					handler = sensor.pop('handler')
					sensor_name = sensor.pop('name')
					s = cr[handler](sensor_name, **sensor)
					logger.info('adding sensor {} to instrument {}'.format(sensor_name, name))
					obj.add_endpoint(s)

					# oh god
					self.conn.bind(s)

				self.add_provider(obj)

	def provider_list(self):
		return self.providers.keys()

	def add_provider(self, provider):
		self.providers[provider.name] = provider

	def provider_endpoints(self, provider):
		return self.providers[provider].list_endpoints()

	def locate_provider(self, endpoint):
		for p, data in self.providers.iteritems():
			if endpoint in data.list_endpoints():
				return data
		return None