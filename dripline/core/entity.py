import datetime
import numbers

from .endpoint import Endpoint
__all__ = []

__all__.append("Entity")
class Entity(Endpoint):
    '''
    Subclass of Endpoint for programatic objects which represent a narrow notion of state.

    In particular, it adds support for "logging" in the form of dripline alert messages
    '''
    def __init__(self, log_interval=0, **kwargs):
        '''
        log_interval: how often to log the Entity's value. If 0 then scheduled logging is disabled;
                      if a number, interpreted as number of seconds; if a dict, unpacked as arguments
                      to the datetime.time_delta initializer; if a datetime.timedelta taken as the new value
        '''
        Endpoint.__init__(self, **kwargs)
        self.log_interval = log_interval
        self._log_action_id = None

    @property
    def log_interval(self):
        return self._log_interval
    @log_interval.setter
    def log_interval(self, new_interval):
        if isinstance(new_interval, numbers.Number):
            self.new_interval = datetime.timedelta(seconds=new_interval)
        elif isinstance(new_interval, dict):
            self.new_interval = datetime.timedelta(**new_interval)
        elif isinstance(new_interval, datetime.timedelta):
            self.new_interval = new_interval
        else:
            raise ValueError("unable to interpret a new_interval of type <{}>".format(type(new_interval)))

    def log_a_value(self):
        result = self.on_get()
        print("value to log is:\n{}".format(result))

    def start_logging(self):
        self._log_action_id = self.service.schedule(self.log_a_value, self._log_interval)
