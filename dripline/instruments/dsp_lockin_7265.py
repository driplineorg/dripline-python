from __future__ import absolute_import

from ..core import Endpoint
from .prologix import GPIBInstrument

import logging
logger = logging.getLogger(__name__)

__all__ = [
            'DSPLockin7265',
            'RawSendEndpoint',
            'CallProviderMethod',
            'ProviderProperty',
          ]

class DSPLockin7265(GPIBInstrument):
    
    def __init__(self, **kwargs):
        GPIBInstrument.__init__(self, **kwargs)
        self._device_status_cmd = "ST"

    def _confirm_setup(self):
        # set the external ADC trigger mode
        value = self.send("TADC 0;TADC")
        logger.info('trig: {}'.format(value))
        # select the curves to sample
        value = self.send("CBD 55;CBD")
        logger.info('curve buffer: {}'.format(value))
        # set the status byte to include all options
        value = self.send("MSK 255;MSK")
        logger.info('status mask: {}'.format(value))

    def _check_status(self):
        raw = self.send("ST")
        if raw:
            data = int(raw)
        else:
            return "No response"
        status = ""
        if data & 0b00000010:
            ";".join([status, "invalid command"])
        if data & 0b00000100:
            ";".join([status, "invalid parameter"])
        return status

    def _taking_data_status(self):
        result = self.send("M")
        curve_status = result.split(';')[0]
        status  = None
        if curve_status == '0':
            status = 'done'
        elif curve_status == '1':
            status = 'running'
        else:
            logger.error("unexpected status byte: {}".format(curve_status))
            raise ValueError('unexpected status byte value')
        return status

    @property
    def number_of_points(self):
        return self.send("LEN")
    @number_of_points.setter
    def number_of_points(self, value):
        if not isinstance(value, int):
            raise TypeError('value must be an int')
        status = self.send("len {};ST".format(value))
        if not status == 1:
            raise ValueError("got an error status code")

    @property
    def sampling_interval(self):
        '''
        Returns the sampling interval in ms
        '''
        return self.send("STR")
    @sampling_interval.setter
    def sampling_interval(self, value):
        '''
        set the sampling interval in integer ms (must be a multiple of 5)
        '''
        if not isinstance(value, int):
            raise TypeError('value must be an int')
        status = self.send("STR {};ST".format(value))
        if not status == 1:
            raise ValueError("got an error status code")

class RawSendEndpoint(Endpoint):

    def __init__(self, base_str, **kwargs):
        Endpoint.__init__(self, **kwargs)
        self.base_str = base_str

    def on_get(self):
        return self.provider.send(self.base_str)
    
    def on_set(self, value):
        return self.provider.send(self.base_str + " " + value)

class CallProviderMethod(Endpoint):
    def __init__(self, method_name, **kwargs):
        Endpoint.__init__(self, **kwargs)
        self.target_method_name = method_name

    def on_get(self):
        method = getattr(self.provider, self.target_method_name)
        logger.debug('method is: {}'.format(method))
        return method()

    def on_set(self, value):
        method = getattr(self.provider, self.target_method_name)
        return method(value)

class ProviderProperty(Endpoint):
    def __init__(self, property_name, **kwargs):
        Endpoint.__init__(self, **kwargs)
        self.target_property = property_name

    def on_get(self):
        prop = getattr(self.provider, self.target_property)
        return prop

    def on_set(self, value):
        if hasattr(self.provider, self.target_property):
            setattr(self.provider, self.target_property, value)
        else:
            raise AttributeError
