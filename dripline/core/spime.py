'''
'''

from __future__ import absolute_import

import datetime
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
                 max_interval=0,
                 max_fractional_change=0,
                 alert_routing_key='sensor_value',
                 **kwargs
                ):
        '''
        log_on_set (bool): flag to enable logging the new value whenever a new one is set
        max_interval (float): If > 0, any log event exceding this number of seconds since the last broadcast will trigger a broadcast.
        max_fractional_change (float): If > 0, any log event which produces a value which differs from the previous value by more than this amount (expressed as a fraction, ie 10% change is 0.1) will trigger a broadcast
        alert_routing_key (str): routing key for the alert message send when broadcasting a logging event result. The default value of 'sensor_value' is valid for DataLoggers which represent physical quantities being stored to the slow controls database tables
        '''
        if 'log_interval' in kwargs:
            if 'schedule_interval' in kwargs:
                logger.error('Cannot define both log_interval and loop_interval for Spime <{}>'.format(kwargs['name']))
            kwargs['schedule_interval'] = kwargs.pop('log_interval')

        Endpoint.__init__(self, **kwargs)
        Scheduler.__init__(self, **kwargs)

        self.alert_routing_key=alert_routing_key + '.' + self.name
        self._max_interval = max_interval
        self._max_fractional_change = max_fractional_change
        self._last_log_time = None
        self._last_log_value = None
        self._log_on_set = log_on_set
        if log_on_set:
            self.on_set = _log_on_set_decoration(self, self.on_set)

    @property
    def log_on_set(self):
        return self._log_on_set
    @log_on_set.setter
    def log_on_set(self, value):
        self._log_on_set = bool(value)
        if self._log_on_set:
            self.on_set = _log_on_set_decoration(self, super(Spime, self))
        else:
            self.on_set = super(Spime, self).on_set

    # Redirect logging_status to scheduler schedule_status for backwards compatibility
    @property
    def logging_status(self):
        return self.schedule_status
    @logging_status.setter
    def logging_status(self, value):
        self.schedule_status = value

    # Redirect log_interval to scheduler schedule_interval for backwards compatibility
    @property
    def log_interval(self):
        return self.schedule_interval
    @log_interval.setter
    def log_interval(self, value):
        self.schedule_interval = value

    @property
    def max_interval(self):
        return self._max_interval
    @max_interval.setter
    def max_interval(self, value):
        value = float(value)
        if value < 0:
            raise ValueError('max log interval cannot be < 0')
        self._max_interval = value

    @property
    def max_fractional_change(self):
        return self._max_fractional_change
    @max_fractional_change.setter
    def max_fractional_change(self, value):
        value = float(value)
        if value < 0:
            raise ValueError('fractional change cannot be < 0')
        self._max_fractional_change = value

    @staticmethod
    def store_value(alert, severity):
        '''
        This method automatically overridden in Spimescape add_endpoint
        '''
        logger.error("Should be logging (value,severity): ({},{})".format(alert, severity))

    def scheduled_action(self):
        '''
        Override Scheduler method with Spime-specific get and log
        '''
        result = self.on_get()
        if result is None:
            logger.warning('Spime scheduled get returned None for <{}>'.format(self.name))
            return
        # Create float cast of value_raw for max_fractional_change test
        try:
            this_value = float(result['value_raw'])
        except (TypeError, ValueError):
            this_value = False
        # Check if this value should be logged
        if self._last_log_value is None:
            logger.debug("log b/c no last log")
        elif (datetime.datetime.utcnow() - self._last_log_time).seconds > self._max_interval:
            logger.debug('log b/c too much time')
        elif this_value and (abs(self._last_log_value - this_value)/self._last_log_value)>self.max_fractional_change:
            logger.debug('log b/c change is too large')
        else:
            logger.debug('no log condition met, not logging')
            return
        self.store_value(result, severity=self.alert_routing_key)
        self._last_log_time = datetime.datetime.utcnow()
        self._last_log_value = this_value
