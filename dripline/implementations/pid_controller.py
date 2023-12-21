'''
Implementation of a PID control loop
'''

from __future__ import print_function
__all__ = []

import time
import datetime
from dripline.core import AlertConsumer
from dripline.core import Interface
from dripline.core import ThrowReply 

import logging
logger = logging.getLogger(__name__)

__all__.append('PidController')
class PidController(AlertConsumer):
    '''
    Implementation of a PID control loop with constant offset. That is, the PID equation
    is used to compute the **change** to the value of some channel and not the value
    itself. In the case of temperature control, this makes sense if the loop is working
    against some fixed load (such as a cryocooler).

    The input sensor can be anything which broadcasts regular values on the alerts
    exchange (using the standard sensor_value.<name> routing key format). Usually
    this would be a temperature sensor, but it could be anything. Similarly, the
    output is anything that can be set to a float value, though a current output
    is probably most common. After setting the new value of current, this value is checked
    to be within a range around the desired value.

    **NOTE**
    The "exchange" and "keys" arguments list below come from the Service class but
    are not valid for this class. Any value provided will be ignored
    '''

    def __init__(self,
                 input_channel,
                 output_channel,
                 check_channel,
                 status_channel,
                 payload_field='value_cal',
                 tolerance = 0.01,
                 target_value=110,
                 proportional=0.0, integral=0.0, differential=0.0,
                 maximum_out=1.0, minimum_out=1.0, delta_out_min= 0.001,
                 enable_offset_term=True,
                 minimum_elapsed_time=0,
                 **kwargs
                ):
        '''
        input_channel (str): name of the logging sensor to use as input to PID (this will override any provided values for keys)
        output_channel (str): name of the endpoint to be set() based on PID
        check_channel (str): name of the endpoint to be checked() after a set()
        status_channel (str): name of the endpoint which controls the status of the heater (enabled/disabled output)
        payload_field (str): name of the field in the payload when the sensor logs (default is 'value_cal' and 'value_raw' is the only other expected value)
        target_value (float): numerical value to which the loop will try to lock the input_channel
        proportional (float): coefficient for the P term in the PID equation
        integral (float): coefficient for the I term in the PID equation
        differential (float): coefficient for the D term in the PID equation
        maximum_out (float): max value to which the output_channel may be set; if the PID equation gives a larger value this value is used instead
        delta_out_min (float): minimum value by which to change the output_channel; if the PID equation gives a smaller change, the value is left unchanged (no set is attempted)
        tolerance (float): acceptable difference between the set and get values (default: 0.01)
        minimum_elapsed_time (float): minimum time interval to perform PID calculation over
        '''
        #kwargs.update({'keys':['sensor_value.'+input_channel]})
        AlertConsumer.__init__(self, **kwargs)

        self._set_channel = output_channel
        self._check_channel = check_channel
        self._status_channel = status_channel
        self.payload_field = payload_field
        self.tolerance = tolerance

        self._last_data = {'value':None, 'time':datetime.datetime.utcnow()}
        self.target_value = target_value

        self.Kproportional = proportional
        self.Kintegral = integral
        self.Kdifferential = differential

        self._integral= 0

        self.max_current = maximum_out
        self.min_current = minimum_out
        self.min_current_change = delta_out_min

        self.enable_offset_term = enable_offset_term
        self.minimum_elapsed_time = minimum_elapsed_time

        self.__validate_status()
        self._old_current = self.__get_current()
        logger.info('starting current is: {}'.format(self._old_current))

    def __get_current(self):
        connection={
            "broker": "rabbit-broker",
            "auth-file": "/root/authentications.json"
        }

        con = Interface(connection)
        value = con.get(self._check_channel).payload[self.payload_field].as_string()
        logger.info('current get is {}'.format(value))

        try:
            value = float(value)
            
        except Exception as err: ##TODO correct exceptions
            raise ThrowReply('value get ({}) is not floatable'.format(value))    
        return value

    def __validate_status(self):
        connection={
            "broker": "rabbit-broker",
            "auth-file": "/root/authentications.json"
        }

        con = Interface(connection)
        value = con.get(self._status_channel).payload[self.payload_field].as_string()
        logger.info("{} returns {}".format(self._status_channel,value))
        if value == 'enabled':
            logger.debug("{} returns {}".format(self._status_channel,value))
        else:
            logger.critical("Invalid status of {} for PID control by {}".format(self._status_channel,self.name))
            raise ThrowReply("{} returns {}".format(self._status_channel,value))

    def this_consume(self, message, method):
        logger.info('consuming message')
        this_value = message.payload[self.payload_field]
        if this_value is None:
            logger.info('value is None')
            return

        this_time = datetime.datetime.strptime(message['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if (this_time - self._last_data['time']).total_seconds() < self.minimum_elapsed_time:
            # handle self._force_reprocess from @target_value.setter
            if not self._force_reprocess:
                logger.info("not enough time has elasped: {}[{}]".format((this_time - self._last_data['time']).total_seconds(),self.minimum_elapsed_time))
                return
            logger.info("Forcing process due to changed target_value")
            self._force_reprocess = False

        self.process_new_value(timestamp=this_time, value=float(this_value))

    @property
    def target_value(self):
        return self._target_value
    @target_value.setter
    def target_value(self, value):
        self._target_value = value
        self._integral = 0
        self._force_reprocess = True

    def set_current(self, value):
        connection={
            "broker": "rabbit-broker",
            "auth-file": "/root/authentications.json"
        }

        con = Interface(connection)
        logger.info('going to set new current to: {}'.format(value))
        reply = con.set(self._set_channel, value)
        logger.info('set response was: {}'.format(reply))

    def process_new_value(self, value, timestamp):

        delta = self.target_value - value
        logger.info('value is <{}>; delta is <{}>'.format(value, delta))

        self._integral += delta * (timestamp - self._last_data['time']).total_seconds()
        if (timestamp - self._last_data['time']).total_seconds() < 2*self.minimum_elapsed_time:
            try:
                derivative = (self._last_data['value'] - value) / (timestamp - self._last_data['time']).total_seconds()
            except TypeError:
                derivative = 0
        else:
            logger.warning("invalid time for calculating derivative")
            derivative = 0.
        self._last_data = {'value': value, 'time': timestamp}

        logger.info("proportional <{}>; integral <{}>; differential <{}>".format\
            (self.Kproportional*delta, self.Kintegral*self._integral, self.Kdifferential*derivative))
        change_to_current = (self.Kproportional * delta +
                             self.Kintegral * self._integral +
                             self.Kdifferential * derivative
                            )
        new_current = (self._old_current or 0)*self.enable_offset_term + change_to_current

        if abs(change_to_current) < self.min_current_change:
            logger.info("current change less than min delta")
            logger.info("old[new] are: {}[{}]".format(self._old_current,new_current))
            return
        logger.info('computed new current to be: {}'.format(new_current))
        if new_current > self.max_current:
            logger.info("new current above max")
            new_current = self.max_current
        if new_current < self.min_current:
            logger.info("new current below min")
            new_current = self.min_current
        if new_current < 0.:
            logger.info("new current < 0")
            new_current = 0.

        self.set_current(new_current)
        logger.debug("allow settling time and checking the current value")
        # FIXME: remove sleep when set_and_check handled properly
        time.sleep(1)
        current_get = self.__get_current()
        if abs(current_get-new_current) < self.tolerance:
            logger.debug("current set is equal to current get")
        else:
            self.__validate_status()
            raise ThrowReply("set value ({}) is not equal to checked value ({})".format(new_current,current_get))

        logger.info("current set is: {}".format(new_current))
        self._old_current = new_current
