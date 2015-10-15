from __future__ import absolute_import

from abc import ABCMeta, abstractproperty, abstractmethod

import functools
import inspect
import math
import time
import traceback
import types

import pika
import yaml

from .message import Message, RequestMessage, ReplyMessage
from . import exceptions
from . import constants


__all__ = ['Endpoint',
           'calibrate',
          ]

import logging
logger = logging.getLogger(__name__)


def calibrate(cal_functions=None):
    if callable(cal_functions):
        cal_functions = {cal_functions.__name__: cal_functions}
    elif isinstance(cal_functions, list):
        cal_functions = {f.__name__:f for f in cal_functions}
    elif cal_functions is None:
        cal_functions = {}
    def calibration(fun):
        @functools.wraps(fun)
        def wrapper(self):
            val_dict = {'value_raw':fun(self)}
            logger.debug('attempting to calibrate')
            if val_dict['value_raw'] is None:
                return None
            if self._calibration is None:
                pass
            elif isinstance(self._calibration, str):
                globals = {
                           "math": math,
                          }
                locals = cal_functions
                eval_str = self._calibration.format(val_dict['value_raw'].strip())
                logger.debug("formated cal is:\n{}".format(eval_str))
                try:
                    cal = eval(eval_str, globals, locals)
                except OverflowError:
                    logger.debug('GOT AN OVERFLOW ERROR')
                    cal = None
                except Exception as e:
                    raise exceptions.DriplineValueError(repr(e), result=val_dict)
                if cal is not None:
                    val_dict['value_cal'] = cal
            elif isinstance(self._calibration, dict):
                logger.debug('calibration is dictionary, looking up value')
                if val_dict['value_raw'] in self._calibration:
                    val_dict['value_cal'] = self._calibration[val_dict['value_raw']]
                else:
                    raise exceptions.DriplineValueError('raw value <{}> not in cal dict'.format(repr(val_dict['value_raw'])), result=val_dict)
            else:
                logger.warning('the _calibration property is of unknown type')
            return val_dict
        return wrapper
    return calibration


def _get_on_set(self, fun):
    #@functools.wraps(fun)
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)
        result = self.on_get()
        return result
    return wrapper


class Endpoint(object):

    def __init__(self, name, calibration=None, get_on_set=False, **kwargs):
        '''
        name (str): unique identifier across all dripline services (used to determine routing key)
        calibration (str||dict): string use to process raw get result (with .format(raw)) or a dict to use for the same purpose where raw must be a key
        get_on_set (bool): flag to toggle running 'on_get' after each 'on_set'
        '''
        self.name = name
        self.provider = None
        self.portal = None
        self._calibration = calibration

        def raiser(self, *args, **kwargs):
            raise exceptions.DriplineMethodNotSupportedError('requested method not supported by this endpoint')

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
        return_msg = None
        try:
            these_args = []
            if 'values' in msg.payload:
                these_args = msg.payload['values']
            these_kwargs = {k:v for k,v in msg.payload.items() if k!='values'}
            logger.debug('args are:\n{}'.format(these_args))
            result = endpoint_method(*these_args, **these_kwargs)
            logger.debug('\n endpoint method returned \n')
            if result is None:
                result = "operation completed silently"
        except exceptions.DriplineException as err:
            logger.debug('got a dripine exception')
            retcode = err.retcode
            result = err.result
            return_msg = str(err)
        except Exception as err:
            logger.error('got an error: {}'.format(str(err)))
            logger.debug('traceback follows:\n{}'.format(traceback.format_exc()))
            return_msg = str(err)
            retcode = 999
        logger.debug('request method execution complete')
        reply = ReplyMessage(payload=result, retcode=retcode, return_msg=return_msg)
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
