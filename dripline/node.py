from connection import Connection
from factory import constructor_registry as cr
from binding import Binding
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
        logger.info('connecting to broker {}'.format(self.conf.broker))
        # TODO: what happens if the connection fails
        self.conn = Connection(self.conf.broker)

        # TODO: bind nodename/providers/endpoints to connection
        self.bind_endpoint('nodename', on_get=self.nodename)
        self.bind_endpoint('providers', on_get=self.provider_list)
        self.bind_endpoint('endpoints', on_get=self.provider_endpoints)

        self.providers = {}

        self._build_object_graph()

    def nodename(self):
        return self.conf.nodename

    def _build_object_graph(self):
        if self.conf.provider_count() > 0:
            for name, items in self.conf.providers.iteritems():
                provider_module = items['module']
                constructor = cr[provider_module]

                logger.info('adding provider {}'.format(name))
                obj = constructor(name, items)

                for endpoint in items['endpoints']:
                    handler = endpoint.pop('module')
                    endpoint_name = endpoint.pop('name')
                    s = cr[handler](endpoint_name, **endpoint)
                    logger.info('adding endpoint {} to provider {}'.format(endpoint_name, name))
                    obj.add_endpoint(s)

                    self.conn.bind(s)

                self.add_provider(obj)

    def bind_endpoint(self, name, on_get=None, on_set=None, on_config=None):
        """
        Bind an endpoint to the dripline node.  Once an endpoint is bound by
        name, it has an address and may be found on the dripline node by
        that name.
        """
        ep_queue = self.conn.chan.queue_declare(exclusive=True)
        binding = Binding(name, on_get, on_set, on_config)

        self.conn.chan.queue_bind(exchange='requests',
                                  queue=ep_queue.method.queue,
                                  routing_key=name)
        self.conn.chan.basic_consume(binding.handle_request,
                                     queue=ep_queue.method.queue)

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

    def start_event_loop(self):
        """
        Start the event loop for processing messages.
        """
        logger.info('starting event loop for node {}'.format(self.nodename()))
        self.conn.start()
