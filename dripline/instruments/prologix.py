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
        #self.name = name
        self.addr = addr
        #self.expecting = False
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


class MuxerGetSpime(SimpleSCPIGetSpime):
    def __init__(self, ch_number, **kwargs):
        self.base_str = "DATA:LAST? (@{})"
        self.ch_number = ch_number
        SimpleSCPIGetSpime.__init__(self, base_str=self.base_str, **kwargs)
        self.get_value = self.on_get
    
    @calibrate()
    def on_get(self):
        very_raw = self.provider.send(self.base_str.format(self.ch_number))
        logger.debug('very raw is: {}'.format(very_raw))
        result = None
        if very_raw:
            result = very_raw.split()[0]
        return result
