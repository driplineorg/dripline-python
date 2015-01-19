from __future__ import absolute_import

from abc import ABCMeta, abstractproperty, abstractmethod
from .message import Message, RequestMessage, ReplyMessage
from . import constants
import pika

__all__ = ['Endpoint', 'AutoReply']

class Endpoint(object):
    __metaclass__ = ABCMeta

    def __init__(self, name, cal_str=None, **kwargs):
        self.name = name
        self.provider = None
        self._calibration_str = cal_str

    # @abstractmethod
    def on_get(self):
        raise NotImplementedError

    # @abstractmethod
    def on_set(self, value):
        raise NotImplementedError

    # @abstractmethod
    def on_config(self):
        raise NotImplementedError

    def _send_reply(self, channel, properties, result):
        '''
        Send an AMQP reply
        '''
        reply = message.ReplyMessage(payload=result).to_msgpack()
        channel.basic_publish(exchange='requests',
                              routing_key=properties.reply_to,
                              properties=pika.BasicProperties(
                                correlation_id=properties.correlation_id
                              ),
                              body=reply,
                             )

    def _calibrate(self, raw):
        '''
        '''
        val_dict = {'value_raw':raw}
        if not self._calib_str is None:
            logger.info('adding calibrated value')
            globals = {"__builtins__": None,
                       "math": math,
                      }
            locals = {}
            val_dict['value_cal'] = eval(self._calib_str.format(raw), globals, locals)
        return val_dict

    def handle_request(self, channel, method, properties, request):
        '''
        '''
        msg = message.Message.from_msgpack(request)
        logger.debug('got a {} request: {}'.format(msg.msgop, msg.payload))

        # and this is somewhat gratuitus...
        #m_dict = {getattr(c,k):'on_'+k.lstrip('OP_SENSOR_').lower() for k in dir(constants) if k.startswith('OP_SENSOR_')}
        method_dict = {}
        for key in dir(constants):
            if k.startswith('OP_SENSOR_'):
                method_dict[getattr(constants, key)] = 'on_'+key.lstrip('OP_SENSOR_').lower()
                
        result = None
        try:
            value = msg.payload
            result = method_dict[msg.msgop](*value)
            if not self._calibration_str is None:
                result = self._calibrate(result)
            if result is None:
                result = "operation returned None"
        except Exception as err:
            logger.error('got an error: {}'.format(err.message))
            result = err.message
        self._send_reply(channel, properties, result)
        ########
#    elif msg.msgop == constants.OP_SENSOR_CONFIG:
#        logger.debug('got a {} request: {}'.format(msg.msgop, msg.payload))
#        result = None
#        try:
#            value = msg.payload
#            result = self.on_config(*value)
#        except Exception as err:
#            logger.warning("config failed: {}".format(err.message))
#            result = err.message
#        self._send_reply(channel, properties, result)
#    else:
#        logger.warning('Got an operation request of unsupported type')
#        self._send_reply(channel, properties, "operation unknown")
#        channel.basic_ack(delivery_tag=method.delivery_tag)

        
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

