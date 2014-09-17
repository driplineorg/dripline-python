from __future__ import absolute_import

from abc import ABCMeta, abstractproperty, abstractmethod
from .message import Message, RequestMessage
from . import constants
import pika

__all__ = ['Endpoint', 'AutoReply']

class Endpoint(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_get(self):
        raise NotImplementedError

    @abstractmethod
    def on_set(self, value):
        raise NotImplementedError

    @abstractmethod
    def on_config(self):
        raise NotImplementedError
        
class AutoReply(Endpoint):
    __metaclass__ = ABCMeta

    def send_reply(self, channel, properties, result):
        channel.basic_publish(exchange='requests',
                              routing_key=properties.reply_to,
                              properties=pika.BasicProperties(
                                  correlation_id=properties.correlation_id
                                  ),
                              body=result)

    def handle_request(self, channel, method, properties, request):
        msg = Message.from_msgpack(request)
        if msg.msgop == constants.OP_SENSOR_GET:
            result = self.on_get()
            self.send_reply(channel, properties, result)
            channel.basic_ack(delivery_tag=method.delivery_tag)

