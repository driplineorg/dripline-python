from __future__ import absolute_import

from abc import ABCMeta, abstractproperty, abstractmethod
from .message import Message, RequestMessage, ReplyMessage
from . import constants

import math
import traceback
import pika

__all__ = ['Endpoint', 'AutoReply']

import logging
logger = logging.getLogger(__name__)

class Endpoint(object):
    __metaclass__ = ABCMeta

    def __init__(self, name, cal_str=None, **kwargs):
        self.name = name
        self.provider = None
        self._calibration_str = cal_str

        method_dict = {}
        for key in dir(constants):
            if key.startswith('OP_SENSOR_'):
                method_name = 'on_'+key.replace('OP_SENSOR_','').lower()
                method = getattr(self, method_name)
                method_dict[getattr(constants, key)] = method
        self.methods = method_dict

    # @abstractmethod
    def on_get(self):
        raise NotImplementedError

    # @abstractmethod
    def on_set(self, value):
        raise NotImplementedError

    # @abstractmethod
    def on_config(self, attribute, value):
        raise NotImplementedError

    def _send_reply(self, channel, properties, reply):
        '''
        Send an AMQP reply
        '''
        if not isinstance(reply, ReplyMessage):
            logger.warn('should be providing a ReplyMessage')
            reply = ReplyMessage(payload=reply)
        channel.basic_publish(exchange='requests',
                              routing_key=properties.reply_to,
                              properties=pika.BasicProperties(
                                correlation_id=properties.correlation_id
                              ),
                              body=reply.to_msgpack(),
                             )

    def _calibrate(self, raw):
        '''
        '''
        val_dict = {'value_raw':raw}
        if not self._calibration_str is None:
            logger.debug('adding calibrated value')
            globals = {"__builtins__": None,
                       "math": math,
                      }
            locals = {}
            val_dict['value_cal'] = eval(self._calibration_str.format(raw), globals, locals)
        return val_dict

    def handle_request(self, channel, method, properties, request):
        '''
        '''
        msg = Message.from_msgpack(request)
        logger.debug('got a {} request: {}'.format(msg.msgop, msg.payload))

        result = None
        try:
            value = msg.payload
            result = self.methods[msg.msgop](*value)
            if (msg.msgop == constants.OP_SENSOR_GET):
                if (not self._calibration_str is None):
                    result = self._calibrate(result)
                else:
                    result = {'value_raw': result}
            if result is None:
                result = "operation returned None"
        except Exception as err:
            logger.error('got an error: {}'.format(err.message))
            logger.debug('traceback follows:\n{}'.format(traceback.format_exc()))
            result = err.message
        reply = ReplyMessage(payload=result)
        self._send_reply(channel, properties, reply)
        logger.debug('reply sent')

        
class AutoReply(Endpoint):
    __metaclass__ = ABCMeta

    def send_reply(self, channel, properties, result):
        logger.debug('trying to send result: {}'.format(result))
        channel.basic_publish(exchange='requests',
                              routing_key=properties.reply_to,
                              properties=pika.BasicProperties(
                                  correlation_id=properties.correlation_id
                                  ),
                              body=result.to_msgpack())

    def handle_request(self, channel, method, properties, request):
        msg = Message.from_msgpack(request)
        if msg.msgop == constants.OP_SENSOR_GET:
            result = self.on_get()
            self.send_reply(channel, properties, result)
            channel.basic_ack(delivery_tag=method.delivery_tag)

