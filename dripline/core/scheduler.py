'''
'''

from __future__ import absolute_import
__docformat__ = 'reStructuredText'

import abc
import logging
import traceback

from .utilities import fancy_doc

__all__ = []
logger = logging.getLogger(__name__)


__all__.append('Scheduler')
@fancy_doc
class Scheduler(object):
    '''
    Base class for objects which need to call their own methods periodically.
    '''
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 schedule_interval=0.,
                 **kwargs):
        '''
        schedule_interval (float): time in seconds between scheduled events
        '''
        self._schedule_interval = schedule_interval
        self._is_looping = False
        self._timeout_handle = None

    def scheduled_action(self):
        raise NotImplementedError("scheduled_action must be defined in derived class")

    @property
    def schedule_interval(self):
        return self._schedule_interval
    @schedule_interval.setter
    def schedule_interval(self, value):
        value = float(value)
        if value < 0:
            raise ValueError('Schedule loop interval cannot be < 0')
        self._schedule_interval = value
        if self.schedule_status:
            logger.info('Restarting schedule loop with new interval')
            self._restart_loop()

    @property
    def schedule_status(self):
        return self._is_looping
    @schedule_status.setter
    def schedule_status(self, value):
        logger.info('setting schedule state to: {}'.format(value))
        if value in ['start', 'on']:
            self._start_loop()
        elif value in ['stop', 'off']:
            self._stop_loop()
        elif value in ['restart']:
            self._restart_loop()
        else:
            raise ValueError('unrecognized schedule state setting')

    def single_schedule(self, delay):
        if self._is_looping:
            logger.warning('single_schedule will break existing schedule loop')
            self._stop_loop()
        self._timeout_handle = self.service._connection.add_timeout(delay, self._process_schedule)

    def _process_schedule(self):
        logger.info("beginning scheduled sequence")
        try:
            result = self.scheduled_action()
        except Exception as err:
            logger.error('got a: {}'.format(str(err)))
            logger.error('traceback follows:\n{}'.format(traceback.format_exc()))
        logger.debug("scheduled sequence complete")
        if self._is_looping and (self._schedule_interval > 0):
            self._timeout_handle = self.service._connection.add_timeout(self._schedule_interval, self._process_schedule)

    def _start_loop(self):
        if self._schedule_interval <= 0:
            raise Warning("schedule loop interval must be > 0")
        self.service._connection.remove_timeout(self._timeout_handle)
        self._is_looping = True
        self._process_schedule()
        logger.info("schedule loop started")

    def _stop_loop(self):
        try:
            self.service._connection.remove_timeout(self._timeout_handle)
            self._is_looping = False
        except Warning:
            pass
        except:
            logger.error('something went wrong stopping')
            raise

    def _restart_loop(self):
        try:
            self._stop_loop()
        except Warning:
            pass
        self._start_loop()
