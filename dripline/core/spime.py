'''
'''

from __future__ import absolute_import

import logging
import math
import functools
import types

from .exceptions import *
from .endpoint import Endpoint, calibrate
from .data_logger import DataLogger

__all__ = ['Spime',
           'SimpleSCPISpime',
           'SimpleSCPIGetSpime',
           'SimpleSCPISetSpime',
           'FormatSCPISpime',
          ]

logger = logging.getLogger(__name__)


def _log_on_set_decoration(self, fun):
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        result = fun(*args, **kwargs)
            
        values = {}
        if result is not None:
            if isinstance(result, types.DictType):
                values.update(result)
            else:
                values.update({'value_raw': result})
        else:
            values.update({'value_raw': args[0]})
        to_log = {'from': self.name,
                  'values': values,
                 }
        self.store_value(alert=to_log, severity=self.alert_routing_key)
        return result
    return wrapper


class Spime(Endpoint, DataLogger):
    '''
    From wikipedia (paraphrased): *A spime is a neologism for a futuristic object, characteristic to the Internet of Things, that can be tracked through space and time throughout its lifetime. A Spime is essentially virtual master objects that can, at various times, have physical incarnations of itself.*

    In the context of Dripline, a Spime is an object with which one interacts (Endpoint) and which is able to regularly report on its own state (DataLogger). Examples include obvious sensor readings such as the coldhead_temperature or bore_pressure and instrument settings such as heater_current or lo_ch1_cw_frequency.
    '''

    def __init__(self,
                 log_on_set=False,
                 **kwargs
                ):
        '''
        Keyword Args:
            log_on_set (bool): flag to enable logging the new value whenever a new one is set

        See :class:`Endpoint <dripline.core.endpoint.Endpoint>` and :class:`DataLogger <dripline.core.data_logger.DataLogger>` for additional parameters

        '''
        # Endpoint stuff
        Endpoint.__init__(self, **kwargs)
        # DataLogger stuff
        DataLogger.__init__(self, **kwargs)
        self.get_value = self.on_get

        self._log_on_set = log_on_set
        if log_on_set:
            self.on_set = _log_on_set_decoration(self, self.on_set)
    @property
    def log_on_set(self):
        return self._log_on_set
    @log_on_set.setter
    def log_on_set(self, value):
        if bool(value) != bool(self._log_on_set):
            return
        self._log_on_set = bool(value)
        if log_on_set:
            self.on_set = _log_on_set_decoration(self, super(Spime, self))
        else:
            self.on_set = super(Spime, self).on_set
        

    @staticmethod
    def store_value(alert, severity):
        logger.error("Should be logging (value,severity): ({},{})".format(alert, severity))


#@fancy_init_doc
class SimpleSCPISpime(Spime):

    def __init__(self,
                 base_str,
                 **kwargs):
        '''
        Keyword ARgs:
            base_str (str): string used to generate SCPI commands
                            get will be of the form "base_str?"
                            set will be of the form "base_str <value>;*OPC?"


        '''
        self.cmd_base = base_str
        Spime.__init__(self, **kwargs)

    @calibrate
    def on_get(self):
        result = self.provider.send(self.cmd_base + '?')
        logger.debug('result is: {}'.format(result))
        return result

    def on_set(self, value):
        return self.provider.send(self.cmd_base + ' {};*OPC?'.format(value))


#@fancy_init_doc
class SimpleSCPIGetSpime(SimpleSCPISpime):
    '''
    Identical to SimpleSCPISpime, but with an explicit exception if on_set is attempted
    '''

    def __init__(self, **kwargs):
        SimpleSCPISpime.__init__(self, **kwargs)

    @staticmethod
    def on_set():
        raise DriplineMethodNotSupportedError('setting not available for {}'.format(self.name))


class SimpleSCPISetSpime(SimpleSCPISpime):
    '''
    Identical to SimpleSCPISpime, but with an explicit exception if on_get is attempted
    '''

    def __init__(self, **kwargs):
        SimpleSCPISpime.__init__(self, **kwargs)

    @staticmethod
    def on_get():
        raise DriplineMethodNotSupportedError('getting not available for {}'.format(self.name))

class FormatSCPISpime(Spime):
    def __init__(self, get_str=None, set_str=None, set_value_map=None, set_value_lowercase=False, **kwargs):
        '''
        Keyword Args:
            get_str (str): if not None, sent verbatim in the event of on_get; (exception if None)
            set_str (str): if not None, sent as set_str.format(value) in the event of on_set (exception if None)
            set_value_map (dict): dictionary of mappings for values to on_set; note that the result of set_value_map[value] will be used as the input to set_str.format(value) if this dict is present
            set_value_lowercase (bool): convenience option to use .lower() on set value if it is a string
        

        '''
        Spime.__init__(self, **kwargs)
        self._get_str = get_str
        self._set_str = set_str
        self._set_value_map = set_value_map

    @calibrate
    def on_get(self):
        if self._get_str is None:
            raise DriplineMethodNotSupportedError('<{}> has no get string available'.format(self.name))
        result = self.provider.send(self._get_str)
        return result

    def on_set(self, value):
        if self._set_str is None:
            raise DriplineMethodNotSupportedError('<{}> has no set string available'.format(self.name))
        if isinstance(value, types.StringTypes):
            value = value.lower()
        logger.debug('value is: {}'.format(value))
        if isinstance(self._set_value_map, types.DictType):
            mapped_value = self._set_value_map[value]
        elif self._set_value_map is None:
            mapped_value = value
        else:
            raise DriplineInternalError('set_value_map of unsupported type')
        logger.debug('mapped value is: {}'.format(mapped_value))
        result = self.provider.send(self._set_str.format(mapped_value))
        return result
