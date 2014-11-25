'''
Basic abstraction for binding to the alerts exchange
'''

from __future__ import absolute_import
import logging

import pika
import msgpack

from .connection import Connection
from .message import Message

__all__ = ['AlertConsumer']
logger = logging.getLogger(__name__)


class AlertConsumer:
   
    def __init__(self, broker_host='localhost', exchange='alerts', keys=['#']):
        self.dripline_connection = Connection(broker_host=broker_host)
        self.dripline_connection._setup_amqp()
        self.queue = self.dripline_connection.conne

    @staticmethod
    def custom_consume(message):
        logger.info('{}'.format(message))

    def start(self):
        def process_message(channel, method, properties, message):
            message_unpacked = Message.from_msgpack(message)
            message_unpacked.payload = msgpack.unpackb(message_unpacked.payload)
            message.payload.name = method.routing_key
            self.custom_consume(message)
        self.dripline_connection.chan.basic_consume(process_message,
                                                     queue=self.queue_name,
                                                     no_ack=True
                                                   )
        self.dripline_connection.chan.start_consuming()
