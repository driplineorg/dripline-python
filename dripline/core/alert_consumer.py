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
        logger.debug('AlertConsumer initializing')
        self.dripline_connection = Connection(broker_host=broker_host)
        self.dripline_connection._setup_amqp()
        self.queue = self.dripline_connection.chan.queue_declare(auto_delete=True)
        for key in keys:
            self.dripline_connection.chan.queue_bind(exchange=exchange,
                                                     queue=self.queue.method.queue,
                                                     routing_key=key,
                                                    )

    @staticmethod
    def custom_consume(message):
        logger.debug('using default message consumption')
        logger.info('{}'.format(message))

    def start(self):
        logger.debug("AlertConsmer consume starting")
        def process_message(channel, method, properties, message):
            logger.debug('in process_message callback')
            message_unpacked = Message.from_msgpack(message)
            message_unpacked.payload = msgpack.unpackb(message_unpacked.payload)
            self.custom_consume(message_unpacked)
        self.dripline_connection.chan.basic_consume(process_message,
                                                     queue=self.queue.method.queue,
                                                     no_ack=True
                                                   )
        self.dripline_connection.chan.start_consuming()
