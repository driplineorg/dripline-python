import datetime
import functools
import types

import numbers

import scarab

from .endpoint import Endpoint
from dripline.core import MsgAlert
__all__ = []

def _log_on_set_decoration(self, fun):
    '''
    requires get_on_set be true; log the result of the on_get via an alert message
    '''
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        result = fun(*args, **kwargs)

        values = {}
        if result != [u'']:
            if isinstance(result, dict):
                values.update(result)
            else:
                values.update({'value_raw': result})
        else:
            values.update({'value_raw': args[0]})
        print('set done, now log')
        self.log_a_value(values)
        return result
    return wrapper

def _get_on_set_decoration(self, fun):
    '''
    make a call to on_get immediately after on_set returns, returning the result
    '''
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)
        print("set, now get_on_set")
        result = self.on_get()
        return result
    return wrapper

__all__.append("Entity")
class Entity(Endpoint):
    '''
    Subclass of Endpoint which adds logic related to logging and confirming values.

    In particular, there is support for:
    get_on_set -> setting the endpoint's value returns a get() result rather than an empty success
                  (particularly useful for devices which may round assignment values)
    log_on_set -> further extends get_on_set to send an alert message in addtion to returning the value in a reply
    log_interval -> leverages the scheduler class to log the on_get result at a regular cadence
    '''
    #check_on_set -> allows for more complex logic to confirm successful value updates
    #                (for example, the success condition may be measuring another endpoint)
    def __init__(self, get_on_set=False, log_routing_key_prefix='sensor_value', log_interval=0, log_on_set=False, **kwargs):
        '''
        get_on_set: if true, calls to on_set are immediately followed by an on_get, which is returned
        log_routing_key_prefix: first term in routing key used in alert messages which log values
        log_interval: how often to log the Entity's value. If 0 then scheduled logging is disabled;
                      if a number, interpreted as number of seconds; if a dict, unpacked as arguments
                      to the datetime.time_delta initializer; if a datetime.timedelta taken as the new value
        log_on_set: if true, always call log_a_value() immediately after on_set
                    **Note:** requires get_on_set be true, overrides must be equivalent
        '''
        Endpoint.__init__(self, **kwargs)

        self.log_routing_key_prefix=log_routing_key_prefix

        # keep a reference to the on_set (possibly decorated in a subclass), needed for changing *_on_set configurations
        self.__initial_on_set = self.on_set

        self._get_on_set = None
        self._log_on_set = None
        self.get_on_set = get_on_set
        self.log_on_set = log_on_set

        self.log_interval = log_interval
        self._log_action_id = None

    @property
    def get_on_set(self):
        return self._get_on_set
    @get_on_set.setter
    def get_on_set(self, value):
        if value:
            self.on_set = _get_on_set_decoration(self, self.__initial_on_set)
            if self.log_on_set:
                self.on_set = _log_on_set_decoration(self.on_set)
        else:
            if self.log_on_set:
                raise ValueError("unable to disable get_on_set while log_on_set is enabled")
            self.on_set = self.__initial_on_set
        self._get_on_set = bool(value)

    @property
    def log_on_set(self):
        return self._log_on_set
    @log_on_set.setter
    def log_on_set(self, value):
        if value:
            if not self.get_on_set:
                raise ValueError("unable to enable log_on_set when get_on_set is disabled")
            self.on_set = _log_on_set_decoration(self, self.on_set)
        else:
            self.on_set = self.__initial_on_set
            if self.get_on_set:
                self.on_set = _get_on_set_decoration(self, self.on_set)
        self._log_on_set = bool(value)

    @property
    def log_interval(self):
        return self._log_interval
    @log_interval.setter
    def log_interval(self, new_interval):
        if isinstance(new_interval, numbers.Number):
            self._log_interval = datetime.timedelta(seconds=new_interval)
        elif isinstance(new_interval, dict):
            self._log_interval = datetime.timedelta(**new_interval)
        elif isinstance(new_interval, datetime.timedelta):
            self._log_interval = new_interval
        else:
            raise ValueError("unable to interpret a new_interval of type <{}>".format(type(new_interval)))

    def scheduled_log(self):
        print("in a scheduled log event")
        result = self.on_get()
        self.log_a_value(result)

    def log_a_value(self, the_value):
        print("value to log is:\n{}".format(the_value))
        the_alert = MsgAlert.create(payload=scarab.to_param(the_value), routing_key='{}.{}'.format(self.log_routing_key_prefix, self.name))
        alert_sent = self.service.send(the_alert)

    def start_logging(self):
        if self._log_action_id is not None:
            self.service.unschedule(self._log_action_id)
        if self.log_interval:
            print('should start logging every {}'.format(self.log_interval))
            self._log_action_id = self.service.schedule(self.scheduled_log, self.log_interval, datetime.datetime.now() + self.service.execution_buffer*3)
        else:
            raise ValueError('unable to start logging when log_interval evaluates false')
        print('log action id is {}'.format(self._log_action_id))

    def stop_logging(self):
        #TODO: should it be an error to stop_logging() when already not logging?
        if self._log_action_id is not None:
            self.service.unschedule(self._log_action_id)
        self._log_action_id = None
