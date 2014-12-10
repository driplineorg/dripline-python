'''
<this should say something useful>
'''

import itertools
import threading
import time
import json
import socket

from ..core import Spime, Provider

import logging
logger = logging.getLogger(__name__)

__all__ = ['PrologixSpimescape',
           'GPIBInstrument',
           'SimpleGetSpime',
          ]


class PrologixSpimescape(Provider):
    def __init__(self, **kwargs):
        '''
        '''
        self.alock = threading.Lock()
        self._keep_polling = True
        self._poll_interval = 0.5
        self.socket_timeout = 1.0
        self.expecting = False
        self.socket_info = ("localhost", 1234)
        self.poll_thread = threading.Timer([], {})
        self.socket = socket.socket()
        self._devices = {}
        for k,v in kwargs.items():
            setattr(self, k, v)

    def reconnect(self):
        self.socket.close()
        self.socket = socket.socket()
        self.socket.connect(self.socket_info)
        self.socket.settimeout(self.socket_timeout)

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
        self.socket.send(tosend)
        data = self.socket.recv(1024)
        self.expecting = False
        logger.debug('sync: {} -> {}'.format(repr(command), repr(data)))
        self.alock.release()
        return data


class GPIBInstrument(Provider):
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.queue = []
        self.expecting = False
        self.status = 0
        self.provider = None
        self._cmd_term = '\n'
        self.spimes = {}

    def add_endpoint(self, spime):
        self.spimes.update({spime.name:spime})
        spime.provider = self

    def send(self, cmd):
        return self.provider.send(cmd+self._cmd_term, self)


class SimpleGetSpime(Spime):
    def __init__(self, name, base_str):
        self.name = name
        self.cmd_base = base_str
        self.provider=None

    def on_get(self):
        return self.provider.send(self.cmd_base)

#def setup_handler(handler='file'):
#    date_form = '%Y-%m-%dT%H:%M:%S'
#    try:
#        import colorlog
#        formatter = colorlog.ColoredFormatter(
#            "%(log_color)s%(levelname)-8s%(asctime)s[%(name)s:%(lineno)d] %(purple)s%(message)s",
#            datefmt = date_form,
#            reset=True,
#            log_colors={
#                    'DEBUG': 'cyan',
#                    'INFO': 'green',
#                    'WARNING': 'yellow',
#                    'ERROR': 'red',
#                    'CRITICAL': 'red',
#            }
#        )
#    except:
#        formatter = logging.Formatter("%(levelname)-8s%(asctime)s[%(name)s:%(lineno)d]%(message)s")
#    if handler == 'file':
#        new_handler = logging.FileHandler('prologix.log')
#    elif handler == 'console':
#        new_handler = logging.StreamHandler()
#    else:
#        raise ValueError('handler:{} not recognized'.format(handler))
#    new_handler.setFormatter(formatter)
#    new_handler.setLevel(logging.DEBUG)
#    logger.setLevel(logging.DEBUG)
#    logger.addHandler(new_handler)
