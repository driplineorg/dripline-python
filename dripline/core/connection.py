'''
A connection to the AMQP broker
'''


from __future__ import absolute_import

import pika
import threading
import traceback
import uuid

from .endpoint import Endpoint
from .message import Message, AlertMessage, ReplyMessage

__all__ = ['Connection']

import logging
logger = logging.getLogger(__name__)

class Connection(object):
    def __init__(self, broker_host='localhost', queue_name=None):
        if queue_name is None:
            queue_name = "reply_queue-{}".format(uuid.uuid1().hex[:12])
        self._queue_name = queue_name
        self.broker_host = broker_host
        conn_params = pika.ConnectionParameters(broker_host)
        self.conn = pika.BlockingConnection(conn_params)
        self.chan = self.conn.channel()
        self.chan.confirm_delivery()
        self.__alert_lock = threading.Lock()
        self._response = None
        self._response_encoding = None

        self._setup_amqp()

    def _ensure_connection(self):
        if not self.conn.is_open:
            logger.warning('amqp connection seems to have broken, reconnecting')
            self.conn.connect()
            self.chan = self.conn.channel()
            self.chan.confirm_delivery()

    def __del__(self):
        if hasattr(self, 'conn') and self.conn.is_open:
            self.conn.close()

    def _setup_amqp(self):
        '''
        ensures all exchanges are present and creates a response queue.
        '''
        self.chan.exchange_declare(exchange='requests', type='topic')
        self.queue = self.chan.queue_declare(queue=self._queue_name,
                                             exclusive=True,
                                             auto_delete=True,
                                            )
        self.chan.queue_bind(exchange='requests',
                             queue=self.queue.method.queue,
                             routing_key=self.queue.method.queue,
                            )

        self.chan.exchange_declare(exchange='alerts', type='topic')

        self.chan.basic_consume(self._on_response, queue=self.queue.method.queue)

    def _on_response(self, channel, method, props, response):
        if self.corr_id == props.correlation_id:
            self._response = response
            self._response_encoding = props.content_encoding

    def start(self):
        while True:
            self.conn.process_data_events()

    def send_request(self, target, request, decode=False):
        '''
        send a request to a specific consumer.
        '''
        if isinstance(request, Message):
            to_send = request.to_msgpack()
            decode = True
        else:
            to_send = request

        self._ensure_connection()
        self._response = None
        self._response_encoding = None
        self.corr_id = str(uuid.uuid4())
        pr = self.chan.basic_publish(exchange='requests',
                                     routing_key=target,
                                     mandatory=True,
                                     immediate=True,
                                     properties=pika.BasicProperties(
                                       reply_to=self.queue.method.queue,
                                       content_encoding='application/msgpack',
                                       correlation_id=self.corr_id,
                                     ),
                                     body=to_send
                                    )
        logger.debug('publish success is: {}'.format(pr))
        if not pr:
            self._response = ReplyMessage(exceptions='no such queue', payload='key: {} not matched'.format(target)).to_msgpack()
        while self._response is None:
            self.conn.process_data_events()

        if decode:
            if self._response_encoding.endswith('json'):
                to_return = Message.from_json(self._response)
            elif self._response_encoding.endswith('msgpack'):
                to_return = Message.from_msgpack(self._response)
            else:
                to_return = self._response
        else:
            to_return = self._response
        return to_return

    def send_alert(self, alert, severity):
        '''
        send an alert
        '''
        self.__alert_lock.acquire()
        self._ensure_connection()
        try:
            logger.info('sending an alert message: {}'.format(repr(alert)))
            message = AlertMessage()
            message.update({'payload':alert})
            packed = message.to_msgpack()
            pr = self.chan.basic_publish(exchange='alerts',
                                         properties=pika.BasicProperties(
                                           content_encoding='application/msgpack',
                                         ),
                                         routing_key=severity,
                                         body=packed,
                                        )
            if not pr:
                logger.error('alert unable to send')
            logger.info('alert sent, returned:{}'.format(pr))
        except KeyError as err:
            if err.message == 'Basic.Ack':
                logger.warning("pika screwed up...\nit's probably fine")
            else:
                raise
        except Exception as err:
            logger.error('an error while sending alert')
            logger.error('traceback follows:\n{}'.format(traceback.format_exc()))
            raise
        finally:
            self.__alert_lock.release()
