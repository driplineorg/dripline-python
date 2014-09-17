from __future__ import absolute_import

from .connection import Connection
from .binding import Binding
from . import message
import logging

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(ch)

__all__ = ['Node']

class Node(object):
    """
    The Node is the core abstraction in the dripline model.  A Node object
    represents an entity on the dripline mesh which can send and receive
    messages.  Providers 'belong' to the Node, and endpoints are attached
    to the Node through the bind and bind_endpoint methods for a given Node
    instance.
    """
    def __init__(self, configuration):
        self.conf = configuration
        logger.info('connecting to broker {}'.format(self.conf.broker))
        # TODO: what happens if the connection fails
        try:
            self.conn = Connection(self.conf.broker)
        except Exception as err:
            logger.error('connection to broker failed!')
            raise err

        # TODO: bind nodename/providers/endpoints to connection
        self.bind('nodename', on_get=self.nodename)
        self.bind('providers', on_get=self.provider_list)
        self.bind('endpoints', on_get=self.provider_endpoints)

        self.providers = {}

    def nodename(self):
        """
        Returns the name of the node on the dripline mesh.
        """
        return self.conf.nodename

    def _build_object_graph(self):
        """
        From the configuration data, this method constructs an object graph in
        memory.  The object graph connects objects which are related by a
        provider -> endpoint relationship.  During the process of building
        the object graph, class instances which are responsible for the
        providers and endpoints are instantiated.  Bindings are also created
        for endpoints during this process.  Once this method returns, all
        providers and endpoints have been bound to the node.
        """
        if self.conf.provider_count() > 0:
            for name, items in self.conf.providers.iteritems():
                provider_module = items['module']
                constructor = cr[provider_module]

                logger.info('adding provider {}'.format(name))
                obj = constructor(name, items)

                for endpoint in items['endpoints']:
                    handler = endpoint.pop('module')
                    endpoint_name = endpoint.pop('name')
                    endpoint_instance = cr[handler](endpoint_name, **endpoint)
                    log_msg = 'adding endpoint {} to provider {}'
                    logger.info(log_msg.format(endpoint_name, name))
                    obj.add_endpoint(endpoint_instance)
                    self.bind_endpoint(endpoint_instance)

                self.add_provider(obj)

    def extend_object_graph(self, provider, endpoints=[]):
        '''
        Add a provider and its endpoints, extend the object graph.

        The object graph connects objects which are related by a provider
        -> endpoint relationship. During the process of building the
        object graph, bindings are created for endpoints.
        '''
        for endpoint in endpoints:
            provider.add_endpoint(endpoint)
            self.bind_endpoint(endpoint)
        self.add_provider(provider)

    # TODO: what happens when some params are None?
    def bind(self, name, on_get=None, on_set=None, on_config=None):
        """
        Bind an arbitrary set of set/get/config functions to the
        dripline node.  Note that currently this cannot be called
        directly in a configuration file!  It is only used internally
        by dripline.
        """
        ep_queue = self.conn.chan.queue_declare(exclusive=True)
        binding = Binding(name, on_get, on_set, on_config)

        self.conn.chan.queue_bind(exchange='requests',
                                  queue=ep_queue.method.queue,
                                  routing_key=name)
        self.conn.chan.basic_consume(binding.handle_request,
                                     queue=ep_queue.method.queue)

    def bind_endpoint(self, endpoint):
        """
        Bind an endpoint to the dripline node.  Once an endpoint is bound by
        name, it has an address and may be found on the dripline node by
        that name.
        """
        self.bind(endpoint.name,
                  on_get=endpoint.on_get,
                  on_set=endpoint.on_set,
                  on_config=endpoint.on_config)

    # TODO: god these names are awkward, who came up with this???
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

    def send_sync(self, to_send):
        """
        Send a message synchronously to an endpoint which is connected
        to the dripline mesh.  This method will wait for a reply and return
        it synchronously to the caller.  The provided message to be sent
        should subclass dripline.Message such that it can be serialized to
        msgpack via a to_msgpack method.  The result of calling this function
        will also subclass Message.
        """
        reply = self.conn.send_request(to_send.target, to_send.to_msgpack())
        return message.Message.from_msgpack(reply)

    def config(self):
        """
        Return the YAML string representation of this dripline Node's
        configuration.
        """
        return self.conf.yaml_conf
