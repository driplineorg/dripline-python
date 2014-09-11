from abc import ABCMeta, abstractproperty, abstractmethod
from message import Message, RequestMessage
import constants
import pika

class Sensor(object):
    __metaclass__ = ABCMeta

    # when a sensor is bound to a connection, it will receive requests
    # in its handle_request method.
    @abstractmethod
    def handle_request(self, channel, method, properties, request):
        pass

class AutoReply(Sensor):
    __metaclass__ = ABCMeta

    def send_reply(self, channel, properties, result):
        channel.basic_publish(exchange='requests',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
                ),
            body=result)

    def handle_request(self, channel, method, properties, request):
        msg = Message.from_msgpack(request), Message()
        if msg.msgop == constants.OP_SENSOR_GET:
                result = self.on_get()
                self.send_reply(channel, properties, result)
                channel.basic_ack(delivery_tag = method.delivery_tag)

    @abstractmethod
    def on_get(self):
        raise NotImplementedError

    @abstractmethod
    def on_set(self):
        raise NotImplementedError
