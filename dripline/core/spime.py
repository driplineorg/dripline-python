'''
'''

from __future__ import absolute_import
import logging
import math

from .endpoint import Endpoint
from .data_logger import DataLogger

__all__ = ['Spime',
           'SimpleSCPISpime',
           'SimpleSCPIGetSpime',
           'SimpleSCPISetSpime',
          ]

logger = logging.getLogger(__name__)


class Spime(Endpoint, DataLogger):
    '''
    '''

    def __init__(self, name, log_interval=0.):
        # DataLogger stuff
        DataLogger.__init__(self, log_interval=log_interval)
        self.get_value = self.on_get
        self.store_value = self.report_log
        # Endpoint stuff
        self.name = name
        self.provider = None

    @staticmethod
    def report_log(value):
        logger.info("Should be logging value: {}".format(value))

    def on_config(self, attribute, value):
        '''
        simple access to setting attributes
        '''
        logger.info('setting attribute')
        setattr(self, attribute, value)


class SimpleSCPISpime(Spime):
    '''
    '''

    def __init__(self,
                 base_str,
                 cal_str='{}',
                 **kwargs):
        '''
        '''
        self._calib_str = cal_str
        self.cmd_base = base_str
        Spime.__init__(self, **kwargs)

    def on_get(self):
        result = self.provider.send(self.cmd_base + '?')
        return result

    def on_set(self, value):
        return self.provider.send(self.cmd_base + ' {};*OPC').format(value))

    def _calibrate(self, raw):
        globals = {"__builtins__": None,
                   "math": math,
                  }
        locals = {}
        result = eval(self._calib_str.format(raw), globals, locals)


class SimpleSCPIGetSpime(SimpleSCPISpime):
    '''
    '''

    def __init__(self, base_str, **kwargs)
        SimpleSCPISpime.__init__(self,
                                 base_str=base_str.rstrip('?'),
                                 **kwargs)

    @staticmethod
    def on_set():
        raise NotImplementedError('setting not available for {}'.format(self.name))


class SimpleSCPISetSpime(SimpleSCPISpime):
    '''
    '''

    def __init__(self, base_str, **kwargs)
        SimpleSCPISpime.__init__(self,
                                 base_str=base_str,
                                 **kwargs)

    @staticmethod
    def on_get():
        raise NotImplementedError('getting not available for {}'.format(self.name))

class Foo:
    pass
