

from __future__ import absolute_import
import socket
import threading
import types

from ..core import Provider, Endpoint

import logging
logger = logging.getLogger(__name__)

__all__ = ['EthernetSCPI',
           'EthernetRepeater',
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
        Provider.__init__(self, **kwargs)
        self.alock = threading.Lock()
        self.socket_timeout = float(socket_timeout)
        self.socket_info = socket_info
        self.poll_thread = threading.Timer([],{})
        self.socket = socket.socket()
        self.response_terminator = response_terminator
        self.command_terminator = command_terminator
        if type(self.socket_info) is str:
            import re
            re_str = "\([\"'](\S+)[\"'], ?(\d+)\)"
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

    def send(self, commands):
        '''
        this issues commands
        '''
        if isinstance(commands, types.StringType):
            commands = [commands]
        self.alock.acquire()
        
        all_data = []
        for command in commands:
            logger.debug('sending: {}'.format(repr(command)))
            if self.command_terminator is not None:
                command += self.command_terminator
            self.socket.send(command)
            data = self.get()
            logger.debug('sync: {} -> {}'.format(repr(command),repr(data)))
            all_data.append(data)
        self.alock.release()
        return ';'.join(all_data)

    def get(self):
        data = ""
        try:
            while True:
                data += self.socket.recv(1024)
                if (self.response_terminator and  data.endswith(self.response_terminator)):
                    break
        except socket.timeout:
            pass
        if self.response_terminator:
            data = data.rsplit(self.response_terminator,1)[0]
        return data

    @property
    def spimes(self):
        return self.endpoints


class EthernetRepeater(EthernetSCPI, Endpoint):
    '''
    '''

    def __init__(self, **kwargs):
        Endpoint.__init__(self, **kwargs)
        EthernetSCPI.__init__(self, **kwargs)

    def on_send(self, to_send):
        result = self.send(to_send)
        return result
