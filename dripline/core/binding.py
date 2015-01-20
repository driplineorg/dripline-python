""" binding.py
A class which represents the binding between dripline name
and the functions which are called when that name is addressed
on the dripline mesh.
"""
from __future__ import absolute_import

import pika
import logging

from ..core import message
from ..core import constants

__all__ = ['Binding']
logger = logging.getLogger(__name__)

class Binding(object):
    """
    Represents the binding between dripline names and local functions.
    """
    def __init__(self, name, on_get, on_set, on_config):
        self.endpoint_name = name
        self.on_get = on_get
        self.on_set = on_set
        self.on_config = on_config

    def _send_reply(self, channel, properties, result):
        """
        Send an AMQP reply
        """
        reply = message.ReplyMessage(payload=result).to_msgpack()
        channel.basic_publish(exchange='requests',
                              routing_key=properties.reply_to,
                              immediate=True,
                              properties=pika.BasicProperties(
                                  correlation_id=properties.correlation_id
                                  ),
                              body=reply)

    def handle_request(self, channel, method, properties, request):
        """
        The entry point for a request which is addressed to the
        endpoint which is bound by this binding.
        """
        msg = message.Message.from_msgpack(request)
        # TODO: this is a really messy abstraction, the endpoint baseclass 
        # should be able to handle this with with a dict mapping constant values
        # to abstract methods
        # (ie add OP_SENSOR_<whatever> to constants, add a abstract method for
        # it, and add an entry to the constant->method dict)
        if msg.msgop == constants.OP_SENSOR_GET:
            logger.debug('got a {} request: {}'.format(msg.msgop, msg.payload))
            try:
                result = self.on_get()
            except Exception as err:
                logger.error('got: {}'.format(err.message))
                result = err.message
            self._send_reply(channel, properties, result)
        elif msg.msgop == constants.OP_SENSOR_SET:
            logger.debug('got a {} request: {}'.format(msg.msgop, msg.payload))
            result = None
            try:
                value = msg.payload
                result = self.on_set(*value)
                logger.info('set returned: {}'.format(result))
                result = 'complete'
            except Exception as err:
                logger.error('got: {}'.format(err.message))
                result = err.message
            self._send_reply(channel, properties, result)
        elif msg.msgop == constants.OP_SENSOR_CONFIG:
            logger.debug('got a {} request: {}'.format(msg.msgop, msg.payload))
            result = None
            try:
                value = msg.payload
                result = self.on_config(*value)
            except Exception as err:
                logger.warning("config failed: {}".format(err.message))
                result = err.message
            self._send_reply(channel, properties, result)
        else:
            logger.warning('Got an operation request of unsupported type')
            self._send_reply(channel, properties, "operation unknown")
        channel.basic_ack(delivery_tag=method.delivery_tag)
