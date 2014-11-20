'''
'''

from __future__ import absolute_import
import logging
logger = logging.getLogger(__name__)

import abc
import multiprocessing
import time

__all__ = ['DataLogger']

class DataLogger(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        logger.debug('in data_logger init')
        self._log_interval = 0
        self._loop_process = multiprocessing.Process()

#    @abc.abstractmethod
    def get_value(self):
        raise NotImplementedError('get value in derrived class')

#    @abc.abstractmethod
    def store_value(self, value):
        raise NotImplementedError('store value in derrived class')

    @property
    def log_interval(self):
        return self._log_interval
    @log_interval.setter
    def log_interval(self, value):
        value = int(value)
        if value < 0:
            raise ValueError('Log interval cannot be < 0')
        self._log_interval = value

    def _log_loop(self):
        while True:
            self.store_value(self.get_value())
            time.sleep(self._log_interval)

    def _stop_loop(self):
        if self._loop_process.is_alive():
            self._loop_process.terminate()
        else:
            raise Warning("loop process not running")

    def _start_loop(self):
        if self._loop_process.is_alive():
            raise Warning("loop process already started")
        elif not self._log_interval:
            raise Exception("log interval must be > 0")
        else:
            self._loop_process = multiprocessing.Process(target=self._log_loop)
            self._loop_process.start()

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
        if value in ['start', 'on']:
            self._start_loop()
        elif value in ['stop', 'off']:
            self._stop_loop()
        elif value in ['restart']:
            self._restart_loop()
        else:
            raise ValueError('unrecognized logger status setting')
