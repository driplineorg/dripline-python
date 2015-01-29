from __future__ import absolute_import

from abc import ABCMeta, abstractproperty, abstractmethod
from .message import Message, RequestMessage, ReplyMessage
from . import constants

import math
import traceback
import pika

__all__ = ['Endpoint', 'AutoReply', 'calibrate']

import logging
logger = logging.getLogger(__name__)


# This doesn't belong in core... at all;
# but i haven't figured out how to reasonably pass it
# into the calibration decorator in a way doesn't suck
def cernox_calibration(resistance, serial_number):
    data = {
            1912:[(45.5, 297), (167.5, 77), (310.9, 40), (318.2, 39), (433.4, 28)],
            1929:[(45.5, 297), (187.5, 77), (440.9, 30.5), (1922, 6.7), (2249, 5.9), (3445, 4.3), (4611, 3.5), (6146, 3), (8338, 2.5), (11048, 2.1), (11352, 2)],
            33122:[(47.6, 300), (81.1, 200), (149, 100), (180, 80), (269, 50), (598, 20)],
            31305:[(62.8, 300), (186, 78), (4203, 4.2)],
            43022:[(68.6, 300), (248, 78), (3771, 4.2)],
            87771:[(68.3, 305), (211, 77), (1572, 4.2)],
            87791:[(66.9, 305), (209, 79), (1637, 4.2)],
            87820:[(69.2, 305), (212, 77), (1522, 4.2)],
            87821:[(68.7, 305), (218, 77), (1764, 4.2)],
            #87821:[(56.21, 276.33), (133.62, 77), (1764, 4.2)], #recal
           }
    this_data = data[serial_number]
    this_data.sort()
    last = ()
    next = ()
    for pt in this_data:
        if pt[0] < resistance:
            last = pt
        elif pt[0] == resistance:
            return pt[1]
        else:
            next = pt
            break
    if not next or not last:
        return None
    m = (math.log(next[1])-math.log(last[1])) / (math.log(next[0])-math.log(last[0]))
    b = math.log(next[1]) - m * math.log(next[0])
    return math.exp(math.log(resistance)*m+b)


def calibrate(fun):
    def wrapper(self):
        val_dict = {'value_raw':fun(self)}
        if not self._calibration_str is None:
            logger.debug('adding calibrated value')
            globals = {"__builtins__": None,
                       "math": math,
                       "cernox_calibration": cernox_calibration,
                      }
            locals = {}
            cal = eval(self._calibration_str.format(val_dict['value_raw']), globals, locals)
            if cal is not None:
                val_dict['value_cal'] = cal
        return val_dict
    return wrapper


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
                              immediate=True,
                              mandatory=True,
                              routing_key=properties.reply_to,
                              properties=pika.BasicProperties(
                                correlation_id=properties.correlation_id
                              ),
                              body=reply.to_msgpack(),
                             )

    def handle_request(self, channel, method, properties, request):
        '''
        '''
        msg = Message.from_msgpack(request)
        logger.debug('got a {} request: {}'.format(msg.msgop, msg.payload))

        result = None
        try:
            value = msg.payload
            result = self.methods[msg.msgop](*value)
            if result is None:
                result = "operation returned None"
        except Exception as err:
            logger.error('got an error: {}'.format(err.message))
            logger.debug('traceback follows:\n{}'.format(traceback.format_exc()))
            result = err.message
        reply = ReplyMessage(payload=result)
        self._send_reply(channel, properties, reply)
        channel.basic_ack(delivery_tag = method.delivery_tag)
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

