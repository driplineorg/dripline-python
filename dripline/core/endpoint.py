from __future__ import absolute_import

from abc import ABCMeta, abstractproperty, abstractmethod

import functools
import inspect
import math
import time
import traceback
import types
import uuid

import asteval
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
        def wrapper(self, *args, **kwargs):
            very_raw = fun(self)
            if isinstance(very_raw, list):
                very_raw = very_raw[0]
            val_dict = {'value_raw':very_raw}
            logger.debug('attempting to calibrate')
            if val_dict['value_raw'] is None:
                return None
            if self._calibration is None:
                pass
            elif isinstance(self._calibration, str):
                #globals = {
                #           "math": math,
                #          }
                locals = cal_functions
                evaluator = asteval.Interpreter(symtable=locals)
                if isinstance(val_dict['value_raw'],float):
                    eval_str = self._calibration.format(val_dict['value_raw'])
                else:
                    eval_str = self._calibration.format(val_dict['value_raw'].strip())
                logger.debug("formated cal is:\n{}".format(eval_str))
                try:
                    cal = evaluator(eval_str)
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
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)
        result = self.on_get()
        return result
    return wrapper


class Endpoint(object):

    def __init__(self, name=None, calibration=None, get_on_set=False, **kwargs):
        '''
        name (str): unique identifier across all dripline services (used to determine routing key)
        calibration (str||dict): string use to process raw get result (with .format(raw)) or a dict to use for the same purpose where raw must be a key
        get_on_set (bool): flag to toggle running 'on_get' after each 'on_set'
        '''
        if name is None:
            raise exceptions.DriplineValueError('Endpoint __init__ requres name not be None')
        else:
            self.name = name
        self.provider = None
        self.service = None
        self._calibration = calibration
        self.__lockout_key = None

        def raiser(self, *args, **kwargs):
            raise exceptions.DriplineMethodNotSupportedError('requested method not supported by this endpoint')

        for key in dir(constants):
            if key.startswith('OP_'):
                method_name = 'on_' + key.split('_')[-1].lower()
                if not hasattr(self, method_name):
                    setattr(self, method_name, types.MethodType(raiser, self, Endpoint))
                if not hasattr(self, '_'+method_name):
                    setattr(self, '_'+method_name, getattr(self, method_name))

        if get_on_set:
            self.on_set = _get_on_set(self, self.on_set)

    def _check_lockout_conditions(self, msg, these_args, these_kwargs):
        operation_allowed = False
        # execute because unlocked
        if self.__lockout_key is None:
            logger.debug('operation allowed because not locked')
            operation_allowed = True
        # execute because OP_GET is always allowed
        elif msg.msgop == constants.OP_GET:
            logger.debug('operation allowed because it is Get')
            operation_allowed = True
        # execute if lockout key is present and correct
        elif msg.get('lockout_key', '').replace('-', '') == self.__lockout_key:
            logger.debug('operation allowed because correct lockout key')
            operation_allowed = True
        # execute because is OP_COMD to unlock with force
        elif msg.msgop == constants.OP_CMD:
            if these_kwargs.get('routing_key_specifier') == 'unlock' or these_args[0:1] == ['unlock']:
                if msg.payload.get('force', False):
                    operation_allowed = True
                    logger.debug('operation allowed because forcing unlock')
                else:
                    raise exceptions.DriplineAccessDenied('cannot unlock without valid lockout_key or force==True')
        # reject because no acceptable conditions met
        if not operation_allowed:
            raise exceptions.DriplineAccessDenied('Endpoint <{}> is locked; lockout_key required'.format(self.name))

    def handle_request(self, channel, method, properties, request):
        logger.debug('handling request:{}'.format(request))
        result = None
        retcode = None
        return_msg = None
        try:
            routing_key_specifier = method.routing_key.replace(self.name, '', 1).lstrip('.')
            logger.debug('routing key specifier is: {}'.format(routing_key_specifier))

            msg = Message.from_encoded(request, properties.content_encoding)
            if msg.payload is None:
                msg.payload = {}
            logger.info('got a {} request: {}'.format(msg.msgop, msg.payload))
            lockout_key = msg.get('lockout_key', None)

            # construction action
            these_args = []
            if 'values' in msg.payload:
                these_args = msg.payload['values']
            these_kwargs = {k:v for k,v in msg.payload.items() if k!='values'}
            if routing_key_specifier:
                these_kwargs.update({'routing_key_specifier':routing_key_specifier})
            if lockout_key and msg.msgop == constants.OP_CMD:
                these_kwargs.update({'lockout_key': lockout_key})
            method_name = ''
            for const_name in dir(constants):
                if getattr(constants, const_name) == msg.msgop:
                    method_name = '_on_' + const_name.split('_')[-1].lower()
            endpoint_method = getattr(self, method_name)
            logger.debug('method is: {}'.format(endpoint_method))

            self._check_lockout_conditions(msg, these_args, these_kwargs)
            logger.debug('args are:\n{}'.format(these_args))
            logger.debug('kwargs are:\n{}'.format(these_kwargs))
            result = endpoint_method(*these_args, **these_kwargs)
            if isinstance(result, types.MethodType):
                raise exceptions.DriplineValueError('endpoint returned a method reference; perhaps OP_GET was used for a cmd?', result=repr(result))
            logger.debug('\n endpoint method returned \n')
            if result is None and return_msg is None:
                return_msg = "operation completed silently"
        except exceptions.DriplineException as err:
            logger.debug('got a dripine exception')
            retcode = err.retcode
            result = err.result
            return_msg = str(err)
        except Exception as err:
            logger.error('got an error: {}'.format(str(err)))
            logger.error('traceback follows:\n{}'.format(traceback.format_exc()))
            return_msg = str(err)
            retcode = 999
        logger.debug('request method execution complete')
        reply = ReplyMessage(payload=result, retcode=retcode, return_msg=return_msg)
        self.service.send_reply(properties, reply)
        logger.debug('reply sent')

    def _on_get(self, *args, **kwargs):
        '''
        WARNING! you should *NOT* override this method
        '''
        result = None
        attribute = kwargs.get('routing_key_specifier', [''][0]).replace('-','_')
        if attribute:
            if hasattr(self, attribute):
                result = getattr(self, attribute)
            else:
                raise exceptions.DriplineValueError('{}({}) has no <{}> attribute'.format(self.name, self.__class__.__name__, attribute))
        else:
            result = self.on_get()
        return result

    def _on_set(self, *args, **kwargs):
        '''
        WARNING! you should *NOT* override this method
        '''
        result = None
        value = args
        attribute = ''
        if 'routing_key_specifier' in kwargs:
            attribute = kwargs['routing_key_specifier'].replace('-','_')
            value = args[0]
        if attribute:
            if hasattr(self, attribute):
                setattr(self, attribute, value)
            else:
                raise exceptions.DriplineValueError('{}({}) has no <{}> attribute'.format(self.name, self.__class__.__name__, attribute))
        else:
            result = self.on_set(value[0])
        return result

    def on_config(self, attribute, value=None):
        '''
        configure a property again

        WARNING! if you override this method, you must ensure you deal with lockout properly
        '''
        raise exceptions.DriplineDeprecated('on_config use is deprecated')
        #result = None
        #if hasattr(self, attribute):
        #    if value is not None:
        #        setattr(self, attribute, value)
        #        logger.info('set {} of {} to {}'.format(attribute, self.name, value))
        #    else:
        #        result = getattr(self, attribute)
        #else:
        #    raise exceptions.DriplineValueError("No attribute: {}".format(attribute))
        #return result

    def on_cmd(self, *args, **kwargs):
        '''
        WARNING! if you override this method, you must ensure you deal with lockout properly
        '''
        logger.debug('args are: {}'.format(args))
        logger.debug('kwargs are: {}'.format(kwargs))
        method_name = None
        if kwargs.get('routing_key_specifier'):
            method_name = kwargs.pop('routing_key_specifier').replace('-', '_')
        else:
            raise exceptions.DriplineDeprecated('specifying cmd name in values array is deprecated (use an RKS)')
            #method_name = args[0:1][0].replace('-', '_')
            #args = args[1:len(args)]
        if method_name != 'lock' and 'lockout_key' in kwargs:
            kwargs.pop('lockout_key')
        result = getattr(self, method_name)(*args, **kwargs)
        return result

    def ping(self, *args, **kwargs):
        '''
        ignore all details and respond with an empty message
        '''
        return None

    def set_condition(self, *args, **kwargs):
        '''
        ignore all details and respond with an empty message
        To actually do something inside a class, the set_condition should be implemented in the class itself.
        '''
        return None

    @property
    def is_locked(self):
        return bool(self.__lockout_key)

    @property
    def lockout_key(self):
        return self.__lockout_key

    def lock(self, lockout_key=None, *args, **kwargs):
        logger.debug('locking <{}>'.format(self.name))
        if lockout_key is None:
            lockout_key = uuid.uuid4().get_hex()
        lockout_key = lockout_key.replace('-', '')
        self.__lockout_key = lockout_key
        return {'key': self.__lockout_key}

    def unlock(self, *args, **kwargs):
        logger.debug('unlocking <{}>'.format(self.name))
        self.__lockout_key = None
        #raise exceptions.DriplineWarning('unlocked')
