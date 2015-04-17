'''
Basic abstraction for binding to the alerts exchange
'''

from __future__ import absolute_import

# standard libs
import logging
import traceback
import uuid

# 3rd party libs
import pika

# internal imports
from .connection import Connection
from .message import Message

__all__ = ['AlertConsumer']

logger = logging.getLogger(__name__)


class AlertConsumer:
    def __init__(self, broker_host='localhost', exchange='alerts', keys=['#']):
        logger.debug('AlertConsumer initializing')
        self.table = None
        self.dripline_connection = Connection(broker_host=broker_host)
        self.dripline_connection._setup_amqp()
        self.queue = self.dripline_connection.chan.queue_declare(queue=__name__+'-'+uuid.uuid1().hex[:12],
              exclusive=True,
              auto_delete=True,
             )
        for key in keys:
            self.dripline_connection.chan.queue_bind(exchange=exchange,
                                                     queue=self.queue.method.queue,
                                                     routing_key=key,
                                                    )
    def this_consume(self, message):
        raise NotImplementedError('you must set this_consume to a valid function')

    @staticmethod
    def _print_consume(message):
        logger.debug('using default message consumption')
        logger.info('{}'.format(message))
    def _postgres_consume(self, message):
        data = {}
        for key in ['value_raw', 'value_cal', 'memo']:
            try:
                data[key] = message['payload']['values'][key]
            except:
                pass

        insert_dict = {'endpoint_name': message['payload']['from'],
                       'timestamp': message['timestamp'],
                      }
        insert_dict.update(data)
        try:
            ins = self.table.insert().values(**insert_dict)
            ins.execute()
        except Exception as err:
            if err.message.startswith("(InternalError)"):
                if 'no known endpoint with name' in err.message:
                    logger.critical("Unable to log for <{}>, sensor not in SQL table".format(err.message.split('with name')[-1]))
                else:
                    logger.warning('unknown error during sqlalchemy insert:\n{}'.format(err))
                    logger.debug('traceback follows:\n{}'.format(traceback.format_exc()))
            else:
                raise


    def start(self):
        logger.debug("AlertConsmer consume starting")
        def process_message(channel, method, properties, message):
            logger.debug('in process_message callback')
            try:
                message_unpacked = Message.from_encoded(message, properties.content_encoding)
                self.this_consume(message_unpacked)
            except Exception as err:
                logger.warning('got an exception (trying to continue running):\n{}'.format(err.message))
                logger.debug('traceback follows:\n{}'.format(traceback.format_exc()))
                raise
        self.dripline_connection.chan.basic_consume(process_message,
                                                    queue=self.queue.method.queue,
                                                    no_ack=True
                                                   )
        self.dripline_connection.chan.start_consuming()
