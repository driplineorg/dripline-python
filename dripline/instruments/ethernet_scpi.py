

import socket, threading

from ..core import Provider

import logging
logger = logging.getLogger(__name__)

__all__ = ['EthernetSCPI',
           ]

class EthernetSCPI(Provider):
    def __init__(self,
                 socket_timeout=1.0,
                 socket_info=("localhost",1234),
                 response_terminator = None,
                 command_terminator = None,
                 **kwargs
                 ):
        '''
        '''
        Provider.__init__(self,**kwargs)
        self.alock = threading.Lock()
        self.socket_timeout = float(socket_timeout)
        self.socket_info = socket_info
        self.poll_thread = threading.Timer([],{})
        self.socket = socket.socket()
        self.response_terminator = response_terminator
        self.command_terminator = command_terminator
        self.endpoints = {}
        if type(self.socket_info) is str:
            import re
            re_str = "\([\"'](\S+)[\"'],(\d+)\)"
            (ip,port) = re.findall(re_str,self.socket_info)[0]
            self.socket_info = (ip,int(port))
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
        self.send("")

    def send(self, command):
        '''
        this issues commands
        '''
        self.alock.acquire()
        
        logger.debug('sending: {}'.format(command))
        if self.command_terminator is not None:
            command += self.command_terminator
        self.socket.send(command)
        data = self.get()
        self.alock.release()
        logger.debug('sync: {} -> {}'.format(repr(command),repr(data)))
        return data

    def get(self):
        data = ""
        try:
            while True:
                data += self.socket.recv(1024)
                if (self.response_terminator is not None and  data.endswith(self.response_terminator)):
                    break
        except socket.timeout:
            pass
        if self.response_terminator is not None:
            data = data.rsplit(self.response_terminator,1)[0]
        return data

    @property
    def spimes(self):
        return self.endpoints

    def add_endpoint(self,spime):
        if spime.name in self.endpoints.keys():
            logger.warning('spime "{}" already present'.format(spime.name))
            return
        self.endpoints.update({spime.name:spime})
        spime.provider = self
        logger.info('spime list is now: {}'.format(self.endpoints.keys()))
