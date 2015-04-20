'''
'''

from __future__ import absolute_import
import logging

import abc
import datetime
import threading
import traceback
import uuid

from .endpoint import Endpoint

__all__ = ['DataLogger',
          ]
logger = logging.getLogger(__name__)


class DataLogger(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, log_interval=0., max_interval=0, max_fractional_change=0, **kwargs):
        self._data_logger_lock = threading.Lock()
        self._log_interval = log_interval
        self._max_interval = max_interval
        self._max_fractional_change = max_fractional_change
        self._is_logging = False
        self._loop_process = threading.Timer([], {})

        self._last_log_time = None
        self._last_log_value = None

    def get_value(self):
        raise NotImplementedError('get value in derrived class')

    def store_value(self, value, severity='sensor_value'):
        raise NotImplementedError('store value in derrived class')

    @property
    def log_interval(self):
        return self._log_interval
    @log_interval.setter
    def log_interval(self, value):
        value = float(value)
        if value < 0:
            raise ValueError('Log interval cannot be < 0')
        self._log_interval = value

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

    def _conditionally_send(self, to_send):
        this_value = float(to_send['values']['value_raw'])
        if self._last_log_value is None:
            logger.debug("log b/c no last log")
        elif (datetime.datetime.utcnow() - self._last_log_time).seconds > self._max_interval:
            logger.debug('log b/c too much time')
        elif (abs(self._last_log_value - this_value)/self._last_log_value) > self.max_fractional_change:
            logger.debug('log b/c change is too large')
        else:
            logger.debug('no log condition met, not logging')
            return
        self.store_value(to_send, severity='sensor_value')
        self._last_log_time = datetime.datetime.utcnow()
        self._last_log_value = this_value

    def _log_a_value(self):
        self._data_logger_lock.acquire()
        try:
            val = self.get_value()
            if val is None:
                raise UserWarning
                logger.warning('get returned None')
                if hasattr(self, 'name'):
                    logger.warning('for: {}'.format(self.name))
            to_send = {'from':self.name,
                       'values':val,
                      }
            self._conditionally_send(to_send)
        except UserWarning:
            logger.warning('get returned None')
            if hasattr(self, 'name'):
                logger.warning('for: {}'.format(self.name))
        except Exception as err:
            logger.error('got a: {}'.format(err.message))
            logger.error('traceback follows:\n{}'.format(traceback.format_exc()))
        finally:
            self._data_logger_lock.release()
        logger.info('value sent')
        if (self._log_interval <= 0) or (not self._is_logging):
            return
        self._loop_process = threading.Timer(self._log_interval, self._log_a_value, ())
        self._loop_process.name = 'logger_{}_{}'.format(self.name, uuid.uuid1().hex[:16])
        self._loop_process.start()

    def _stop_loop(self):
        self._data_logger_lock.acquire()
        try:
            self._is_logging = False
            if self._loop_process.is_alive():
                self._loop_process.cancel()
            else:
                raise Warning("loop process not running")
        except:
            logger.error('something went wrong stopping')
            raise
        finally:
            self._data_logger_lock.release()

    def _start_loop(self):
        self._is_logging = True
        if self._loop_process.is_alive():
            raise Warning("loop process already started")
        elif self._log_interval <= 0:
            raise Exception("log interval must be > 0")
        else:
            self._log_a_value()
            logger.info("log loop started")

    def _restart_loop(self):
        try:
            self._stop_loop()
        except Warning:
            pass
        self._start_loop()

    @property
    def logging_status(self):
        translator = {True: 'running',
                      False: 'stopped'
                     }
        return translator[self._loop_process.is_alive()]
    @logging_status.setter
    def logging_status(self, value):
        logger.info('setting logging state to: {}'.format(value))
        if value in ['start', 'on']:
            self._start_loop()
        elif value in ['stop', 'off']:
            self._stop_loop()
        elif value in ['restart']:
            self._restart_loop()
        else:
            raise ValueError('unrecognized logger status setting')

