'''
The portal abstraction is a bit of a mess. Generally speaking it is the crossroad
between abstractions relating to communicating via AMQP and communicating with hardware.
'''

from __future__ import absolute_import

import datetime
import json
import os
import time
import traceback
import uuid

import pika

from .endpoint import Endpoint
from .message import Message, AlertMessage, RequestMessage
from .provider import Provider
from .service import Service

__all__ = ['Portal']

import logging
logger = logging.getLogger(__name__)


class Portal(Service):
    """
    Like a node, but pythonic
    """
    def __init__(self, name, broker):
        '''
        Args:
            name (str): name for the portal instance, represents an AMQP binding key
            broker (str): as always, the network resolvable path to the AMQP broker
        '''
        # need before Service.__init__ b/c keys is a prop here
        self.endpoints = {}
        Service.__init__(self, amqp_url=broker, exchange='requests', keys=[], name=name)
        
        self.providers = {}
        self._responses = {}

    @property
    def keys(self):
        return self.endpoints.keys()
    @keys.setter
    def keys(self, value):
        logger.debug('cannot set keys, use self.endpoints')
        return

    def add_endpoint(self, endpoint):
        '''
        '''
        if endpoint.name in self.endpoints:
            raise ValueError('endpoint ({}) already present'.format(endpoint.name))
        self.endpoints[endpoint.name] = endpoint
        setattr(endpoint, 'store_value', self.send_alert)
        setattr(endpoint, 'report_log', self.send_alert)
        setattr(endpoint, 'portal', self)

    def start_event_loop(self):
        """
        Start the event loop for processing messages.
        """
        logger.info('starting event loop for node {}\n{}'.format(self.name,'-'*29))

        try:
            self.run()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            del(self.conn)
        logger.debug("loop ended")

    def on_message(self, channel, method, header, body):
        try:
            logger.info('request received by {}'.format(self.name))
            self.endpoints[method.routing_key].handle_request(channel, method, header, body)
            logger.info('request processing complete\n{}'.format('-'*29))
        finally:
            self._channel.basic_ack(delivery_tag=method.delivery_tag)

    def _handle_reply(self, channel, method, header, body):
        logger.info("got a reply")
        self._responses[header.correlation_id] = (method, header, body)
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.warning('ack-d')
        logger.info('reply processing complete\n{}'.format('-'*29))
