from __future__ import absolute_import

from ..core import Endpoint
from .prologix import GPIBInstrument

import logging
logger = logging.getLogger(__name__)

__all__ = [
            'DSPLockin7265',
            'DSP_curves',
          ]

class DSPLockin7265(GPIBInstrument):
    
    def __init__(self, **kwargs):
        GPIBInstrument.__init__(self, **kwargs)
        self._device_status_cmd = "ST"

    def _confirm_setup(self):
        # set the external ADC trigger mode
        self.provider.send("TADC 0")
        # select the curves to sample
        self.provider.send("CBD 55")
        # set the status byte to include all options
        self.provider.send("MSK 255")

    def _check_status(self):
        data = int(self.provider.send("ST"))
        status = ""
        if data & 0b00000010:
            ";".join([status, "invalid command"])
        if data & 0b00000100:
            ";".join([status, "invalid parameter"])
        return status

    def _taking_data_status(self):
        curve_status = self.provider.send("M").split(';')[0]
        status  = None
        if curve_status == '0':
            status = 'done'
        elif curve_status == '1':
            status = 'running'
        else:
            raise ValueError('unexpected status byte value')
        return status

    @property
    def number_of_points(self):
        return self.provider.send("LEN")
    @number_of_points.setter
    def number_of_points(self, value):
        if not isinstance(value, int):
            raise TypeError('value must be an int')
        status = self.provider.send("len {};ST".format(value))
        if not status == 1:
            raise ValueError("got an error status code")

    @property
    def sampling_interval(self):
        '''
        Returns the sampling interval in ms
        '''
        return self.provider.send("STR")
    @sampling_interval.setter
    def sampling_interval(self, value):
        '''
        set the sampling interval in integer ms (must be a multiple of 5)
        '''
        if not isinstance(value, int):
            raise TypeError('value must be an int')
        status = self.provider.send("STR {};ST".format(value))
        if not status == 1:
            raise ValueError("got an error status code")

class DSP_curves(Endpoint):
    def on_get(self):
        return self.provider.send("M")
