import datetime
import functools
import types

import numbers

from .endpoint import Endpoint
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
        self.log_a_value(alert=values)
        return result
    return wrapper

def _get_on_set_decoration(self, fun):
    '''
    make a call to on_get immediately after on_set returns, returning the result
    '''
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)
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
    check_on_set -> allows for more complex logic to confirm successful value updates
                    (for example, the success condition may be measuring another endpoint)
    '''
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
        result = self.on_get()
        self.log_a_value(self, result)

    def log_a_value(self, the_value):
        print("value to log is:\n{}".format(the_value))

    def start_logging(self):
        self._log_action_id = self.service.schedule(self.log_a_value, self._log_interval)
