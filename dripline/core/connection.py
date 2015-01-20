'''
A connection to the AMQP broker
'''


from __future__ import absolute_import

import pika
import uuid
from .endpoint import Endpoint
from .sensor import Sensor
from .message import AlertMessage

import logging
logger = logging.getLogger(__name__)

class Connection(object):
    def __init__(self, broker_host='localhost'):
        self.broker_host = broker_host
        conn_params = pika.ConnectionParameters(broker_host)
        self.conn = pika.BlockingConnection(conn_params)
        self.chan = self.conn.channel()

        self._setup_amqp()

    def __del__(self):
        if self.conn.is_open:
            self.conn.close()

    def _setup_amqp(self):
        '''
        ensures all exchanges are present and creates a response queue.
        '''
        self.chan.exchange_declare(exchange='requests', type='topic')
        self.queue = self.chan.queue_declare(exclusive=True, auto_delete=True)
        self.chan.queue_bind(exchange='requests',
                             queue=self.queue.method.queue,
                             routing_key=self.queue.method.queue)

        self.chan.exchange_declare(exchange='alerts', type='topic')
        self.all_alert_queue = self.chan.queue_declare(exclusive=True, auto_delete=True)
        self.chan.queue_bind(exchange='alerts',
                             queue=self.all_alert_queue.method.queue,
                             routing_key='#',
                            )

        self.chan.basic_consume(self._on_response, queue=self.queue.method.queue)

    def _on_response(self, channel, method, props, response):
        if self.corr_id == props.correlation_id:
            self.response = response

    def start(self):
        while True:
            self.conn.process_data_events()

    def send_request(self, target, request):
        '''
        send a request to a specific consumer.
        '''
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.chan.basic_publish(exchange='requests',
                                routing_key=target,
                                mandatory=True,
                                immediate=True,
                                properties=pika.BasicProperties(
                                    reply_to=self.queue.method.queue,
                                    correlation_id=self.corr_id),
                                body=request)
        while self.response is None:
            self.conn.process_data_events()
        return self.response

    def send_alert(self, alert, severity):
        '''
        send an alert
        '''
        message = AlertMessage()
        message.update({'target':severity, 'payload':alert})
        self.chan.basic_publish(exchange='alerts',
                               routing_key=severity,
                               mandatory=True,
                               immediate=True,
                               body=message.to_msgpack(),
                              )
