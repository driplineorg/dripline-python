'''
this is funamentally a clone of node.py
I don't like the way it works and am going to try and make something that is cleaner
'''

from __future__ import absolute_import

import threading
import time
import traceback
import uuid

import pika

from .message import Message, AlertMessage, RequestMessage
from .provider import Provider
from .endpoint import Endpoint

__all__ = ['Portal']

import logging
logger = logging.getLogger(__name__)


class Portal(object):
    """
    Like a node, but pythonic
    """
    def __init__(self, name, broker):
        self.name = name
        self.__request_in_lock = threading.Lock()
        self.__alert_out_lock = threading.Lock()

        self.providers = {}
        self.endpoints = {}
        self._responses = {}
        self.broker = broker
        self.reconnect()

    def reconnect(self):
        '''
        '''
        logger.info('connecting to broker {}'.format(self.broker))
        try:
            self.conn = pika.BlockingConnection(pika.ConnectionParameters(self.broker))
            self.channel = self.conn.channel()
            self.reply_channel = self.conn.channel()
            self.channel.exchange_declare(exchange='requests', type='topic')
            self.channel.confirm_delivery()
            queue_name = 'requests-{}'.format(self.name)
            self.queue = self.channel.queue_declare(queue=queue_name,
                                                    exclusive=True,
                                                    auto_delete=True,
                                                   )
            self.channel.basic_consume(self._handle_request,
                                       queue=self.queue.method.queue,
                                       no_ack=False,
                                      )
            self.reply_queue = self.channel.queue_declare(queue='reply-{}'.format(self.name),
                                                          exclusive=True,
                                                          auto_delete=True,
                                                         )
            self.channel.basic_consume(self._handle_reply,
                                       queue=self.reply_queue.method.queue,
                                       no_ack=False,
                                      )
            self.channel.queue_bind(exchange='requests',
                                    queue=self.reply_queue.method.queue,
                                    routing_key=self.reply_queue.method.queue,
                                   )
            self.create_bindings()
        except Exception as err:
            logger.error('connection to broker failed!!')
            logger.error('traceback:\n{}'.format(traceback.format_exc()))
            raise err
        logger.info('connected')


    def add_endpoint(self, endpoint):
        '''
        '''
        if endpoint.name in self.endpoints:
            raise ValueError('endpoint ({}) already present'.format(endpoint.name))
        self.endpoints[endpoint.name] = endpoint

    def create_bindings(self):
        '''
        '''
        for endpoint in self.endpoints.keys():
            self._bind_endpoint(self.endpoints[endpoint])

    def _bind_endpoint(self, endpoint):
        """
        Bind an endpoint to the dripline node.  Once an endpoint is bound by
        name, it has an address and may be found on the dripline node by
        that name.
        """
        self.channel.queue_bind(exchange='requests',
                                queue=self.queue.method.queue,
                                routing_key=endpoint.name,
                               )
        setattr(endpoint, 'store_value', self.send_alert)
        endpoint.report_log = self.send_alert
        endpoint.portal = self

    def send_alert(self, alert, severity):
        '''
        send a notification to the alert exchange
        '''
        self.__alert_out_lock.acquire()
        try:
            logger.info('sending an alert message: {}'.format(repr(alert)))
            message = AlertMessage()
            message.update({'payload':alert})
            packed = message.to_msgpack()
            pr = self.channel.basic_publish(exchange='alerts',
                                            routing_key=severity,
                                            body=packed,
                                            properties=pika.BasicProperties(
                                                content_encoding='application/msgpack',
                                            ),
                                           )
            if not pr:
                logger.error('alert unable to send')
                logger.warning('publish result is: {}'.format(pr))
        except KeyError as err:
            if err.message == 'Basic.Ack':
                logger.warning("pika screwed up...\nit's probably fine")
            else:
                raise
        except Exception as err:
            logger.error('an error while sending alert')
            logger.error('traceback follows:\n{}'.format(traceback.format_exc()))
        finally:
            self.__alert_out_lock.release()

    def send_reply(self, properties, reply):
        '''
        send a notification to the alert exchange
        '''
        logger.info('sending a reply message: {}'.format(repr(reply)))
        try:
            if not isinstance(reply, Message):
                reply = message.ReplyMessage(payload=reply)
            body = reply.to_encoding(properties.content_encoding)
            pr = self.reply_channel.basic_publish(exchange='requests',
                                            routing_key=properties.reply_to,
                                            body=body,
                                            properties=pika.BasicProperties(
                                                content_encoding='application/msgpack',
                                                correlation_id=properties.correlation_id,
                                            ),
                                            mandatory=True,
                                           )
            if not pr:
                logger.error('alert unable to send')
                logger.warning('publish result is: {}'.format(pr))
        except KeyError as err:
            if err.message == 'Basic.Ack':
                logger.warning("pika screwed up...\nit's probably fine")
            else:
                raise
        except Exception as err:
            logger.error('an error while sending alert')
            logger.error('traceback follows:\n{}'.format(traceback.format_exc()))
        finally:
            logger.debug('release lock')
        logger.debug('send reply complete')

    def start_event_loop(self):
        """
        Start the event loop for processing messages.
        """
        logger.info('starting event loop for node {}\n{}'.format(self.name,'-'*29))

        try:
            while True:
                try:
                    logger.debug('starting new consume')
                    self.channel.start_consuming()
                except pika.exceptions.ConnectionClosed:
                    self.reconnect()
                    logger.critical('had to reconnect')
                    continue
                logger.info('should break out now')
                break
                
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            del(self.conn)
        logger.debug("loop ended")

    def _handle_request(self, channel, method, header, body):
        while not self.__request_in_lock.acquire(False):
            logger.warning('unable to get lock')
            time.sleep(0.1)
        try:
            logger.info('request received by {}'.format(self.name))
            self.endpoints[method.routing_key].handle_request(channel, method, header, body)
            logger.info('request processing complete\n{}'.format('-'*29))
            self.channel.basic_ack(delivery_tag=method.delivery_tag)
        finally:
            self.__request_in_lock.release()

    def _handle_reply(self, channel, method, header, body):
        logger.info("got a reply")
        self._responses[header.correlation_id] = (method, header, body)
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.warning('ack-d')
        logger.info('reply processing complete\n{}'.format('-'*29))

    def config(self):
        """
        Return the YAML string representation of this dripline Node's
        configuration.
        """
        return self.conf.yaml_conf
