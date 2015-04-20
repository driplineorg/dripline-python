'''
'''

from __future__ import absolute_import

import logging
import math
import functools
import types

from .endpoint import Endpoint, calibrate
from .data_logger import DataLogger

__all__ = ['Spime',
           'SimpleSCPISpime',
           'SimpleSCPIGetSpime',
           'SimpleSCPISetSpime',
           'FormatSCPISpime',
          ]

logger = logging.getLogger(__name__)


def _log_on_set(self, fun):
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        try:
            result = fun(*args, **kwargs)
        except TypeError as err:
            return err.message
            
        values = {}
        if result is not None:
            if isinstance(result, types.DictType):
            #import pdb; pdb.set_trace()
                values.update(result)
            else:
                values.update({'value_raw': result})
        else:
            values.update({'value_raw': args[0]})
        to_log = {'from': self.name,
                  'value': values,
                 }
        self.report_log(to_log, 'sensor_value')
        return result
    return wrapper


class Spime(Endpoint, DataLogger):
    '''
    '''

    def __init__(self, 
                 log_interval=0.,
                 log_on_set=False,
                 **kwargs
                ):
        # DataLogger stuff
        DataLogger.__init__(self, log_interval=log_interval)
        self.get_value = self.on_get
        self.store_value = self.report_log
        # Endpoint stuff
        Endpoint.__init__(self, **kwargs)

        if log_on_set:
            self.on_set = _log_on_set(self, self.on_set)

    @staticmethod
    def report_log(value, severity):
        logger.info("Should be logging (value,severity): ({},{})".format(value, severity))


class SimpleSCPISpime(Spime):
    '''
    '''

    def __init__(self,
                 base_str,
                 **kwargs):
        '''
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


class SimpleSCPIGetSpime(SimpleSCPISpime):
    '''
    '''

    def __init__(self, base_str, **kwargs):
        SimpleSCPISpime.__init__(self,
                                 base_str=base_str.rstrip('?'),
                                 **kwargs)

    @staticmethod
    def on_set():
        raise NotImplementedError('setting not available for {}'.format(self.name))


class SimpleSCPISetSpime(SimpleSCPISpime):
    '''
    '''

    def __init__(self, base_str, **kwargs):
        SimpleSCPISpime.__init__(self,
                                 base_str=base_str,
                                 **kwargs)

    @staticmethod
    def on_get():
        raise NotImplementedError('getting not available for {}'.format(self.name))

class FormatSCPISpime(Spime):
    '''
    '''
    def __init__(self, get_str=None, set_str=None, **kwargs):
        '''
        '''
        Spime.__init__(self, **kwargs)
        self._get_str = get_str
        self._set_str = set_str

    @calibrate
    def on_get(self):
        if self._get_str is None:
            raise NotImplementedError('<{}> has no get string available'.format(self.name))
        result = self.provider.send(self._get_str)
        return result

    def on_set(self, value):
        if self._set_str is None:
            raise NotImplementedError('<{}> has no set string available'.format(self.name))
        result = self.provider.send(self._set_str.format(value))
        return result
