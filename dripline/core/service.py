'''
This file is based upon the example in the pika docs.
'''

from __future__ import absolute_import


import json
import logging
import multiprocessing
import os
import uuid

import pika

from .message import Message, AlertMessage, RequestMessage, ReplyMessage
from . import exceptions

logger = logging.getLogger(__name__)

__all__ = ['Service']

class Service(object):
    """This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """
    EXCHANGE_TYPE = 'topic'

    def __init__(self, amqp_url, exchange, keys, name=None):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with

        """
        if name is None:
            name = 'unknown_service_' + str(uuid.uuid4())[1:12]
        self.name = name
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._broker = amqp_url
        self._exchange = exchange
        self.keys = keys

    def __get_credentials(self):
        '''
        read the '~/.project8_authentications.json' file and parse out the amqp credentials
        '''
        credentials = {'username':'guest','password':'guest'}
        try:
            credentials = json.loads(open(os.path.expanduser('~')+'/.project8_authentications.json').read())['amqp']
        except:
            logger.warning('unable to read project8 authentications file, trying default')
            pass
        return pika.PlainCredentials(**credentials)

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        logger.info('Connecting to %s', self._broker)
        return pika.SelectConnection(pika.ConnectionParameters(host=self._broker, credentials=self.__get_credentials()),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """
        logger.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        """This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """
        logger.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:

            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        logger.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self._exchange)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        logger.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def setup_exchange(self, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        logger.info('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.EXCHANGE_TYPE)

    def on_exchange_declareok(self, unused_frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

        """
        logger.info('Exchange declared')
        self.setup_queue(self.name)

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        logger.info('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok,
                                    queue_name,
                                    exclusive=True,
                                    auto_delete=True,
                                   )

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        for key in self.keys:
            logger.info('Binding %s to %s with %s',
                        self._exchange, self.name, key)
            self._channel.queue_bind(self.on_bindok, self.name,
                                     self._exchange, key)

    def on_bindok(self, unused_frame):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame

        """
        logger.info('Queue bound')
        self.start_consuming()

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """
        logger.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.name)

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        logger.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        logger.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body

        """
        try:
            decoded = Message.from_encoded(body, properties.content_encoding)
        except exceptions.DriplineDecodingError as err:
                pass
        logger.log(35, # NOTICE, between INFO and WARNING
                   'Received message # {} from {}: {}'.format(basic_deliver.delivery_tag,
                                                              properties.app_id,
                                                              decoded or body,
                                                             )
                  )
        self.acknowledge_message(basic_deliver.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        logger.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        logger.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        logger.info('Closing the channel')
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        logger.info('Stopping')
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()
        logger.info('Stopped')

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        logger.info('Closing connection')
        self._connection.close()

    def send_message(self, target, message, return_queue=None, properties=None, exchange=None, return_connection=False):
        '''
        '''
        if exchange is None:
            exchange = self._exchange
        if not isinstance(message, Message):
            raise TypeError('message must be a dripline.core.Message')
        parameters = pika.ConnectionParameters(host=self._broker, credentials=self.__get_credentials())
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        result = channel.queue_declare(queue='request_reply'+str(uuid.uuid4()),
                                       exclusive=True,
                                       auto_delete=True,
                                      )
        channel.queue_bind(exchange=exchange,
                           queue=result.method.queue,
                           routing_key=result.method.queue,
                          )
        
        correlation_id = str(uuid.uuid4())
        self.__ret_val = None
        def on_response(ch, method, props, body):
            if correlation_id == props.correlation_id:
                return_queue.put(Message.from_encoded(body, props.content_encoding))

        channel.basic_consume(on_response, no_ack=True, queue=result.method.queue)

        if properties is None:
            properties = pika.BasicProperties(reply_to=result.method.queue,
                                              content_encoding='application/msgpack',
                                              correlation_id=correlation_id,
                                              app_id='dripline.core.Service'
                                             )
        channel.basic_publish(exchange=exchange,
                              routing_key=target,
                              body=message.to_msgpack(),
                              properties=properties,
                             )
        if not return_connection:
            connection.close()
            return
        return connection

    def send_request(self, target, request, timeout=10):
        '''
        It seems like there should be a way to do this with the existing SelectConnection.
        The problem is that the message handler needs to send a request and then be called
        not block the reply from being processed, and needs to get the reply from that processed response.
        The non-blocking part seems tricky. I'm sure there exists a good solution for this,
        maybe within asyncio and/or asyncore, but I don't know where it is. This seems to work.
        '''
        logger.info('sending a request')
        logger.debug('request to <{}> is: {}'.format(target, request))
        if not isinstance(request, RequestMessage):
            raise TypeError('request must be a dripline.core.RequestMessage')
        result_queue = multiprocessing.Queue()
        connection = self.send_message(target, request, return_queue=result_queue, return_connection=True, exchange='requests')
        self.__ret_val = None
        def _get_result(result_queue):
            while result_queue.empty():
                connection.process_data_events()
        process = multiprocessing.Process(target=_get_result, kwargs={'result_queue':result_queue})
        process.start()
        process.join(timeout)
        if process.is_alive():
            process.terminate()
            raise exceptions.DriplineTimeoutError('request response timed out')
        connection.close()
        return result_queue.get()

    def send_alert(self, alert, severity):
        '''
        '''
        logger.info('sending an alert')
        logger.debug('to {} sending {}'.format(severity,alert))
        if not isinstance(alert, AlertMessage):
            alert = AlertMessage(payload=alert)
        self.send_message(target=severity, message=alert, exchange='alerts')

    def send_reply(self, properties, reply):
        '''
        '''
        logger.info("sending a reply")
        if not isinstance(reply, Message):
            reply = ReplyMessage(payload=reply)
        self.send_message(target=properties.reply_to, message=reply, properties=properties)
