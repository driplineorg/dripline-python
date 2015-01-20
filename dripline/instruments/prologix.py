'''
<this should say something useful>
'''

import itertools
import threading
import time
import json
import socket

from ..core import Spime, Provider, SimpleSCPIGetSpime, calibrate

import logging
logger = logging.getLogger(__name__)

__all__ = ['PrologixSpimescape',
           'GPIBInstrument',
           'SimpleGetSpime',
           'MuxerGetSpime',
           'SimpleGetSetSpime',
          ]


class PrologixSpimescape(Provider):
    def __init__(self,
                 socket_timeout=1.0,
                 socket_info=("localhost", 1234),
                 **kwargs
                ):
        '''
        '''
        Provider.__init__(self, **kwargs)
        self.alock = threading.Lock()
        self._keep_polling = True
        self._poll_interval = 0.5
        self.socket_timeout = float(socket_timeout)
        self.expecting = False
        self.socket_info = socket_info
        self.poll_thread = threading.Timer([], {})
        self.socket = socket.socket()
        self._devices = {}
        if type(self.socket_info) is str:
            import re
            re_str = "\([\"'](\S+)[\"'], (\d+)\)"
            (ip, port) = re.findall(re_str, self.socket_info)[0]
            self.socket_info = (ip, int(port))
        logger.debug('socket info is {}'.format(self.socket_info))
        self.reconnect()

    def reconnect(self):
        self.socket.close()
        self.socket = socket.socket()
        try:
            self.socket.connect(self.socket_info)
        except:
            logger.warning('connection with info: {} refused'.format(self.socket_info))
            raise
        self.socket.settimeout(self.socket_timeout)

    @property
    def spimes(self):
        return self._devices

    @property
    def endpoints(self):
        return self._devices

    @property
    def devices(self):
        return self._devices.keys()
    @devices.setter
    def devices(self, device_dict):
        self._devices = device_dict
        self._device_cycle = itertools.cycle(self._devices.keys())
        self._queue_next_check()
    def add_endpoint(self, spime):
        if spime.name in self.devices:
            logger.warning('spime "{}" already present'.format(spime.name))
            return
        self.devices = dict(self._devices.items()+[(spime.name, spime)])
        spime.provider = self
        logger.info('spime list is now: {}'.format(self.devices))

    @property
    def keep_polling(self):
        return self._keep_polling
    @keep_polling.setter
    def keep_polling(self, value):
        if value:
            self._keep_polling = True
            if not self.poll_thread.is_alive():
                self._queue_next_check()
        else:
            self._keep_polling = False
            if self.poll_thread.is_alive():
                self.poll_thread.cancel()

    def _queue_next_check(self, from_check=False):
        if self._devices and self.keep_polling and (from_check or not self.poll_thread.is_alive()):
            self.poll_thread = threading.Timer(self._poll_interval, self._check_next_status, ())
            self.poll_thread.start()
        
    def _check_next_status(self):
        device = self._device_cycle.next()
        resp = self.send('*ESR?\n', from_spime=self._devices[device])
        self._devices[device].status = int(resp)
        if resp==1:
            self._devices[device]['opc']=1
        self._queue_next_check(from_check=True)

    def send(self, command, from_spime=None):
        '''
        that is, the call to the device blocks for a response
        '''
        self.alock.acquire()
        while self.expecting == True:
            continue
        self.expecting = True
        if not from_spime:
            tosend = command
        else:
            tosend = '++addr {}\r{}'.format(from_spime.addr, command)
        logger.debug('sending: {}'.format(tosend))
        self.socket.send(tosend)
        data = self.socket.recv(1024)
        self.expecting = False
        logger.debug('sync: {} -> {}'.format(repr(command), repr(data)))
        self.alock.release()
        return data


class GPIBInstrument(Provider):
    '''
    A Provider class intended for GPIB devices.

    It expects to have a set of Simple*Spime endpoints which return SCPI commands.
    The _cmd_term attribute is appended to those commands before being passed up to
    the higher level provider which actually maintains a connection (eg PrologixSpimescape).
    '''
    def __init__(self, name, addr, **kwargs):
        Provider.__init__(self, name=name, **kwargs)
        #self.name = name
        self.addr = addr
        self.queue = []
        self.expecting = False
        self.status = 0
        self.provider = None
        self._cmd_term = '\n'
        self.endpoints = {}

    def add_endpoint(self, spime):
        self.endpoints.update({spime.name:spime})
        spime.provider = self

    def send(self, cmd):
        return self.provider.send(cmd+self._cmd_term, self)


class SimpleGetSpime(SimpleSCPIGetSpime):
    '''
    A generic Spime for SCPI commands which take no arguments (ie queries).

    It is assumed that the command will:
        1) return something
        2) return quickly

    If either assumption is wrong then you need a different Spime derived class
    '''
    def on_get(self):
        return self.provider.send(self.cmd_base+'?')


class MuxerGetSpime(SimpleGetSpime):
    def __init__(self, name, **kwargs):
        SimpleGetSpime.__init__(self, name=name, **kwargs)
        self.get_value = self.get_parsed_value
    
    @calibrate
    def get_parsed_value(self):
        raw_data = self.on_get()
        return raw_data.split()[0]


class SimpleGetSetSpime(Spime):
    '''
    A generic Spime for SCPI commands using a standard pattern for query and assignment.

    The pattern looks like the following. Consider a command "CMD"
        ~To request the current value, the SCPI command would be: "CMD?"
        ~To assign a new value, the SCPI command would be "CMD <value>;*OPC?"

    It is assumed that both of the above constructions will:
        1) return something
        2) return quickly

    If either of those assumptions is wrong then you want a different Spime derived class
    '''
    def __init__(self, base_str, **kwargs):
        self.cmd_base = base_str
        Spime.__init__(self, **kwargs)

    def on_get(self):
        return self.provider.send(self.cmd_base + '?')

    def on_set(self, value):
        return self.provider.send(self.cmd_base + ' {};*ESR?'.format(value))
