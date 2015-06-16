from __future__ import absolute_import

from abc import ABCMeta, abstractproperty, abstractmethod

import functools
import inspect
import math
import threading
import time
import traceback
import types

import pika
import yaml

from .message import Message, RequestMessage, ReplyMessage
from .connection import Connection
from . import exceptions
from . import constants


__all__ = ['Endpoint',
           'calibrate',
           'fancy_init_doc',
          ]

import logging
logger = logging.getLogger(__name__)


# This doesn't belong in core... at all;
# but i haven't figured out how to reasonably pass it
# into the calibration decorator in a way doesn't suck
def cernox_calibration(resistance, serial_number):
    data = {
            1912:[(45.5, 297), (167.5, 77), (310.9, 40), (318.2, 39), (433.4, 28)],
            1929:[(11.29, 350), (45.5, 297), (187.5, 77), (440.9, 30.5), (1922, 6.7), (2249, 5.9), (3445, 4.3), (4611, 3.5), (6146, 3), (8338, 2.5), (11048, 2.1), (11352, 2)], #note that the (11.29, 350 value is a linear extension of the next two points, not an empirical value... the function should actually be changed to use the first or last interval for out of range readings)
            33122:[(30.85, 350), (47.6, 300), (81.1, 200), (149, 100), (180, 80), (269, 50), (598, 20)], #note that the (30.85,350 value is a linear extension of the next two points, not an empirical value... the function should actually be changed to use the first or last interval for out of range readings)
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


def pt100_calibration(resistance):
    r = resistance
    value = ((r < 2.2913) * (0) +
        (2.2913 <= r and r < 3.65960) *((3.65960-r)*(-6.95647+r/0.085)/1.36831 + (r-2.2913)*(10.83979+r/.191)/1.36831 ) +
        (3.6596 <= r and r < 9.38650) *((9.38650-r)*(10.83979+r/0.191)/5.72690 + (r-3.6596)*(23.92640+r/.360)/5.72690) +
        (9.3865 <= r and r < 20.3800) *((20.3800-r)*(23.92640+r/0.360)/10.9935 + (r-9.3865)*(29.17033+r/.423)/10.9935) +
        (20.380 <= r and r < 29.9290) *((29.9890-r)*(29.17033+r/0.423)/9.54900 + (r-20.380)*(29.10402+r/.423)/9.54900) +
        (29.989 <= r and r < 50.7880) *((50.7880-r)*(29.10402+r/0.423)/20.7990 + (r-29.989)*(25.82396+r/.409)/20.7990) +
        (50.788 <= r and r < 71.0110) *((71.0110-r)*(25.82396+r/0.409)/20.2230 + (r-50.788)*(22.47250+r/.400)/20.2230) +
        (71.011 <= r and r < 90.8450) *((90.8450-r)*(22.47250+r/0.400)/19.8340 + (r-71.011)*(18.84224+r/.393)/19.8340) +
        (90.845 <= r and r < 110.354) *((110.354-r)*(18.84224+r/0.393)/19.5090 + (r-90.845)*(14.84755+r/.387)/19.5090) +
        (110.354 <= r and r < 185) * (14.84755+r/.387) +
        (185. <= r) * (0))
    if value == 0:
        value = None
    return value


def calibrate(fun):
    @functools.wraps(fun)
    def wrapper(self):
        val_dict = {'value_raw':fun(self)}
        if val_dict['value_raw'] is None:
            return None
        if not self._calibration_str is None:
            globals = {
                       "math": math,
                       "cernox_calibration": cernox_calibration,
                       "pt100_calibration": pt100_calibration,
                      }
            locals = {}
            eval_str = self._calibration_str.format(val_dict['value_raw'].strip())
            logger.debug("formated cal is:\n{}".format(eval_str))
            try:
                cal = eval(eval_str, globals, locals)
            except OverflowError:
                cal = None
            if cal is not None:
                val_dict['value_cal'] = cal
        return val_dict
    return wrapper

def fancy_init_doc(cls):
    '''
    note that this was a hack and I'm pulling it back out

    The idea isn't bad, but it doesn't work well with Google's style doc strings, which sphinx renders well
    '''
    params = {}
    for a_cls in inspect.getmro(cls):
        if a_cls == object:
            continue
        this_doc = a_cls.__init__.__func__.__doc__
        if this_doc is None:
            continue
        if len(this_doc.split('~Params')) != 3:
            continue
        params.update(yaml.load(this_doc.split('~Params')[1]))
    this_doc = cls.__init__.__doc__
    param_block = '\n'.join([' '*12 + '{}: {}'.format(k,v) for k,v in params.items()])
    if this_doc is None:
        this_doc = ''
    if len(this_doc.split("~Params")) != 3:
        this_doc = this_doc + '\n\n' + param_block
    else:
        doc_list = this_doc.split('~Params')
        this_doc = (doc_list[0] +
                    '~Params\n' + param_block + '\n' + ' '*8 + '~Params\n\n' +
                    doc_list[2].lstrip('\n')
                   )
    cls.__init__.__func__.__doc__ = this_doc
    return cls


def _get_on_set(self, fun):
    #@functools.wraps(fun)
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)
        result = self.on_get()
        return result
    return wrapper


class Endpoint(object):

    def __init__(self, name, cal_str=None, get_on_set=False, **kwargs):
        '''
        Keyword Args:
            name (str): unique identifier across all dripline services (used to determine routing key)
            cal_str (str): string use to process raw get result
            get_on_set (bool): flag to toggle running 'on_get' after each 'on_set'

        '''
        self.name = name
        self.provider = None
        self.portal = None
        self._calibration_str = cal_str
        self.__request_lock = threading.Lock()

        def raiser(self, *args, **kwargs):
            raise NotImplementedError

        for key in dir(constants):
            if key.startswith('OP_'):
                method_name = 'on_' + key.split('_')[-1].lower()
                if not hasattr(self, method_name):
                    setattr(self, method_name, types.MethodType(raiser, self, Endpoint))

        if get_on_set:
            self.on_set = _get_on_set(self, self.on_set)

    def handle_request(self, channel, method, properties, request):
        logger.debug('handling requst:{}'.format(request))
        msg = Message.from_msgpack(request)
        logger.debug('got a {} request: {}'.format(msg.msgop, msg.payload))

        method_name = ''
        for const_name in dir(constants):
            if getattr(constants, const_name) == msg.msgop:
                method_name = 'on_' + const_name.split('_')[-1].lower()
        endpoint_method = getattr(self, method_name)
        logger.debug('method is: {}'.format(endpoint_method))

        result = None
        retcode = None
        try:
            these_args = msg.payload['values']
            these_kwargs = {k:v for k,v in msg.payload.items() if k!='values'}
            logger.debug('args are:\n{}'.format(these_args))
            result = endpoint_method(*these_args, **these_kwargs)
            if result is None:
                result = "operation returned None"
        except NotImplementedError as err:
            logger.warning('method {} is not implemented'.format(method_name))
        except exceptions.DriplineException as err:
            logger.debug('got a dripine exception')
            retcode = err.retcode
            result = err.message
        except Exception as err:
            logger.error('got an error: {}'.format(err.message))
            logger.debug('traceback follows:\n{}'.format(traceback.format_exc()))
            result = err.message
        logger.debug('request method execution complete')
        reply = ReplyMessage(payload=result, retcode=retcode)
        self.portal.send_reply(properties, reply)
        logger.debug('reply sent')

    def on_config(self, attribute, value=None):
        '''
        configure a property again
        '''
        result = None
        if hasattr(self, attribute):
            if value is not None:
                setattr(self, attribute, value)
                logger.info('set {} of {} to {}'.format(attribute, self.name, value))
            else:
                result = getattr(self, attribute)
        else:
            raise exceptions.DriplineValueError("No attribute: {}".format(attribute))
        return result

    def on_cmd(self, *args, **kwargs):  
        logger.debug('args are: {}'.format(args))
        logger.debug('kwargs are: {}'.format(kwargs))
        try:
            method = getattr(self, args[0])
        except:
            raise
        try:
            result = method(*args[1:], **kwargs)
        except:
            raise
        return result
