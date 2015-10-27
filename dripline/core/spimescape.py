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
from .utilities import fancy_doc

__all__ = ['Spimescape']

import logging
logger = logging.getLogger(__name__)


@fancy_doc
class Spimescape(Service):
    """
    Like a node, but pythonic
    """
    def __init__(self, exchange=None, **kwargs):
        '''
        '''
        if exchange is None:
            exchange = 'requests'
        kwargs['exchange'] = exchange

        Service.__init__(self, **kwargs)
        
        self._responses = {}

    @property
    def keys(self):
        return [key+'.#' for key in self.endpoints.keys()]
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
        setattr(endpoint, 'portal', self)

    def on_request_message(self, channel, method, header, body):
        logger.info('request received by {}'.format(self.name))
        self.endpoints[method.routing_key.split('.')[0]].handle_request(channel, method, header, body)
        logger.info('request processing complete\n{}')

    def _handle_reply(self, channel, method, header, body):
        logger.info("got a reply")
        self._responses[header.correlation_id] = (method, header, body)
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.warning('ack-d')
        logger.info('reply processing complete\n{}'.format('-'*29))
