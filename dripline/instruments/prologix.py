'''
<this should say something useful>
'''

from __future__ import absolute_import

import itertools
import json
import socket
import time
import types

from ..core import Spime, Provider, SimpleSCPIGetSpime, calibrate

import logging
logger = logging.getLogger(__name__)

__all__ = [
           'GPIBInstrument',
           'MuxerGetSpime',
          ]


class GPIBInstrument(Provider):
    '''
    A Provider class intended for GPIB devices that implement the full
    IEEE 488.2 (488.1 or 488 need to use some other class).

    It expects to have a set of Simple*Spime endpoints which return SCPI commands.
    The _cmd_term attribute is appended to those commands before being passed up to
    the higher level provider which actually maintains a connection (eg PrologixSpimescape).
    '''
    def __init__(self, name, addr, **kwargs):
        Provider.__init__(self, name=name, **kwargs)
        self.addr = addr
        self.status = 0
        self.provider = None
        self._cmd_term = '\n'

    def _check_status(self):
        raw = self.provider.send('*ESR?', from_spime=self)
        if raw:
            data = int(raw)
        else:
            return "No response"
        status = ""
        if data & 0b00000100:
            ";".join([status, "query error"])
        if data & 0b00001000:
            ";".join([status, "device error"])
        if data & 0b00010000:
            ";".join([status, "execution error"])
        if data & 0b00100000:
            ";".join([status, "command error"])
        return status
            
    def send(self, cmd):
        if isinstance(cmd, types.StringType):
            cmd = [cmd]
        to_send = ['++addr {}\r'.format(self.addr)] + cmd
        result = self.provider.send(to_send)
        result = ';'.join(result.split(';')[1:])
        logger.debug("instr got back: {}".format(result))
        return result


def pt100_calibration(resistance):
    r = resistance
    value = ((r < 2.2913) * (0) +
        (2.2913 <= r and r < 3.65960) *((3.65960-r)*(-6.95647+r/0.085)/1.36831 + (r-2.2913)*(10.83979+r/.191)/1.36831 ) +
        (3.6596 <= r and r < 9.38650) *((9.38650-r)*(10.83979+r/0.191)/5.72690 + (r-3.6596)*(23.92640+r/.360)/5.72690) +
        (9.3865 <= r and r < 20.3800) *((20.3800-r)*(23.92640+r/0.360)/10.9935 + (r-9.3865)*(29.17033+r/.423)/10.9935) +
        (20.380 <= r and r < 29.9290) *((29.9890-r)*(29.17033+r/0.423)/9.54900 + (r-20.380)*(29.10402+r/.423)/9.54900) +
        (29.989 <= r and r < 50.7880) *((50.7880-r)*(29.10402+r/0.423)/20.7990 + (r-29.989)*(25.82396+r/.409)/20.7990) +
        (50.788 <= r and r < 71.0110) *((71.0110-r)*(25.82396+r/0.409)/20.2230 + (r-50.788)*(22.47250+r/.400)/20.2230) +
        (71.011 <= r and r < 90.8450) *((90.8450-r)*(22.47250+r/0.400)/19.8340 + (r-71.011)*(18.84224+r/.393)/19.8340) +
        (90.845 <= r and r < 110.354) *((110.354-r)*(18.84224+r/0.393)/19.5090 + (r-90.845)*(14.84755+r/.387)/19.5090) +
        (110.354 <= r and r < 185) * (14.84755+r/.387) +
        (185. <= r) * (0))
    if value == 0:
        value = None
    return value


def cernox_calibration(resistance, serial_number):
    data = {
            1912:[(45.5, 297), (167.5, 77), (310.9, 40), (318.2, 39), (433.4, 28)],
            1929:[(11.29, 350), (45.5, 297), (187.5, 77), (440.9, 30.5), (1922, 6.7), (2249, 5.9), (3445, 4.3), (4611, 3.5), (6146, 3), (8338, 2.5), (11048, 2.1), (11352, 2)], #note that the (11.29, 350 value is a linear extension of the next two points, not an empirical value... the function should actually be changed to use the first or last interval for out of range readings)
            33122:[(30.85, 350), (47.6, 300), (81.1, 200), (149, 100), (180, 80), (269, 50), (598, 20)], #note that the (30.85,350 value is a linear extension of the next two points, not an empirical value... the function should actually be changed to use the first or last interval for out of range readings)
            31305:[(62.8, 300), (186, 78), (4203, 4.2)],
            43022:[(68.6, 300), (248, 78), (3771, 4.2)],
            87771:[(68.3, 305), (211, 77), (1572, 4.2)],
            87791:[(66.9, 305), (209, 79), (1637, 4.2)],
            87820:[(69.2, 305), (212, 77), (1522, 4.2)],
            87821:[(68.7, 305), (218, 77), (1764, 4.2)],
            #87821:[(56.21, 276.33), (133.62, 77), (1764, 4.2)], #recal
           }
    this_data = data[serial_number]
    this_data.sort()
    last = ()
    next = ()
    for pt in this_data:
        if pt[0] < resistance:
            last = pt
        elif pt[0] == resistance:
            return pt[1]
        else:
            next = pt
            break
    if not next or not last:
        return None
    m = (math.log(next[1])-math.log(last[1])) / (math.log(next[0])-math.log(last[0]))
    b = math.log(next[1]) - m * math.log(next[0])
    return math.exp(math.log(resistance)*m+b)


class MuxerGetSpime(SimpleSCPIGetSpime):
    def __init__(self, ch_number, **kwargs):
        self.base_str = "DATA:LAST? (@{})"
        self.ch_number = ch_number
        SimpleSCPIGetSpime.__init__(self, base_str=self.base_str, **kwargs)
        self.get_value = self.on_get
    
    @calibrate([pt100_calibration, cernox_calibration])
    def on_get(self):
        very_raw = self.provider.send(self.base_str.format(self.ch_number))
        logger.debug('very raw is: {}'.format(very_raw))
        result = None
        if very_raw:
            result = very_raw.split()[0]
        return result
