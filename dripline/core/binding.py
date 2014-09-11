""" binding.py
A class which represents the binding between dripline name
and the functions which are called when that name is addressed
on the dripline mesh.
"""
import message
import constants
import pika

__all__ = ['Binding']

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
        if msg.msgop == constants.OP_SENSOR_GET:
            result = self.on_get()
            self._send_reply(channel, properties, result)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        elif msg.msgop == constants.OP_SENSOR_SET:
            result = None
            try:
                value = msg.payload
                self.on_set(value)
                result = 'complete'
            except ValueError as err:
                result = err.message
            self._send_reply(channel, properties, result)
            channel.basic_ack(delivery_tag=method.delivery_tag)
