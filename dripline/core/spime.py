'''
'''

from __future__ import absolute_import

import logging
import functools

from .scheduler import Scheduler
from .exceptions import *
from .endpoint import Endpoint, calibrate
from .utilities import fancy_doc

__all__ = ['Spime']

logger = logging.getLogger(__name__)


def _log_on_set_decoration(self, fun):
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        logger.debug('in log_on_set: {}({}, {})'.format(fun,args,kwargs))
        result = fun(*args, **kwargs)

        values = {}
        if result != [u'']:
            if isinstance(result, dict):
                values.update(result)
            else:
                values.update({'value_raw': result})
        else:
            values.update({'value_raw': args[0]})
        logger.debug('result is: {}'.format(result))
        logger.debug('values are: {}'.format(values))
        self.store_value(alert=values, severity=self.alert_routing_key)
        return result
    return wrapper


@fancy_doc
class Spime(Endpoint, Scheduler):
    '''
    From wikipedia (paraphrased): *A spime is a neologism for a futuristic object, characteristic to the Internet of Things, that can be tracked through space and time throughout its lifetime. A Spime is essentially virtual master objects that can, at various times, have physical incarnations of itself.*

    In the context of Dripline, a Spime is an object with which one interacts (Endpoint) and which is able to regularly report on its own state (Scheduler). Examples include obvious sensor readings such as the coldhead_temperature or bore_pressure and instrument settings such as heater_current or lo_ch1_cw_frequency.
    '''

    def __init__(self,
                 log_on_set=False,
                 **kwargs
                ):
        '''
        log_on_set (bool): flag to enable logging the new value whenever a new one is set
        '''
        # Endpoint stuff
        Endpoint.__init__(self, **kwargs)
        # Scheduler stuff
        Scheduler.__init__(self, **kwargs)
        self.get_value = self.on_get

        self._log_on_set = log_on_set
        if log_on_set:
            self.on_set = _log_on_set_decoration(self, self.on_set)
    @property
    def log_on_set(self):
        return self._log_on_set
    @log_on_set.setter
    def log_on_set(self, value):
        #if bool(value) != bool(self._log_on_set):
        #    return
        self._log_on_set = bool(value)
        if self._log_on_set:
            self.on_set = _log_on_set_decoration(self, super(Spime, self))
        else:
            self.on_set = super(Spime, self).on_set

    @staticmethod
    def store_value(alert, severity):
        logger.error("Should be logging (value,severity): ({},{})".format(alert, severity))
