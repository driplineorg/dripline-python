#! /usr/bin/env python

import signal
import socket
import re


class SCPICommand:
    """
    This class represents a single SCPI get/set command pair.

    It can be specified as read-only, in which case the client cannot set a value.
    """
    def __init__(self, command, value, read_only=False):
        self.command = command
        
        abbrev_pattern = re.compile(r'^([A-Z]+)([A-Za-z]*)')
        parsed = abbrev_pattern.search(self.command)
        if parsed == None:
            raise RuntimeError(f'Invalid SCPI command: {command}')
        self.short = parsed.group(1).casefold()
        self.long = (parsed.group(1) + parsed.group(2)).casefold()

        self.value = value
        self.read_only = read_only

    def handle(self, query):
        """
        Checks whether this command should handle the incoming query.

        Returns a 2-element tuple.  
        The first element specifies whether this command handled the query.
        The second element specifies the return value (if any).

        If not, it returns (False, None)

        If it should handle the query, the first return element is always True.
        A get query will return (True, value)
        A set query will return (True, None)
        """
        query_tokens = query.split()
        if len(query_tokens) == 0 or not self.compare(query_tokens[0]):
            return False, None
        
        if query_tokens[0][-1] == '?':
            return self.get()
        
        if self.read_only:
            raise RuntimeError(f'Command {self.command} is read-only')
        
        return self.set(query)

    def compare(self, command):
        command = command.lstrip('*').rstrip('?').casefold()
        return True if command == self.short or command == self.long else False
    
    def get(self):
        return True, self.value
    
    def set(self, query):
        print(repr(query))
        if len(query.split()) == 1:
            raise RuntimeError(f'Empty set received for {self.command}')

        self.value = query.lstrip('*').lstrip(self.command).strip()
        return True, None

class ASCPIDevice:
    """
    This class represents a semi-SCPI-compliant device.

    Note that it does not pay attention to the tree hierarchy of commands, or handle multiple simultaneous commands.

    Note that you won't use a class like this in an actual Dripline deployment --- 
    this takes the place of an actual device for the purpose of this tutorial.

    This class was composed with the aid of ChatGPT 3.5.
    """
    def __init__(self, host, port, commands, ending='\n'):
        self.host = host
        self.port = port
        self.socket = None

        self.ending = ending

        #self.commands = [ SCPICommand(key, value) for key, value in commands.items() ]
        self.commands = [ SCPICommand(**command_args) for command_args in commands]
        print(f'SCPI device initializing with commands: {[command.command for command in self.commands]}')

        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        self.disconnect()
    
    def start(self):
        """
        Start the device: listens on the network for incoming queries.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.bind((self.host, self.port))
            print(f'SCPI device is binding to {self.host}:{self.port}')
            while self.socket.fileno() > 0:
                print(f"Listening for connections on {self.host}:{self.port}")
                self.socket.listen(1)
                try:
                    self.handle_connection()
                except Exception as e:
                    print(f"Error: {e}")
                    break

    def disconnect(self):
        if self.socket:
            self.socket.close()
        print("Disconnected")

    def handle_connection(self):
        self.connection, addr = self.socket.accept()
        print(f'Connected to client from {addr}')
        try:
            while True:
                self.receive_data()
        except Exception as e:
            print(f"Error: {e}")

    def handle_query(self, query):
        """
        Checks the query against all commands this device knows about.
        Stops checking when a responses is returned.
        """
        try:
            for command in self.commands:
                success, response = command.handle(query)
                if success:
                    return str(response)
            return "Invalid request"
        except RuntimeError as e:
            return str(e)

    def receive_data(self):
        data = ''
        while True:
            print('In receive data loop')
            buf = self.connection.recv(1024).decode('utf-8')
            if len(buf) == 0:
                print('Empty buffer received, flushing incomplete buffer:')
                print(repr(data))
                raise RuntimeError('Forcing connection reset.')
            data += buf
            if data.endswith(self.ending):
                break
            print('Adding data')
            print(f'So far: {repr(data)}')

        print(f'Received query: {repr(data)}')
        if data:
            response = str(self.handle_query(data)) + self.ending
            print(f'Sending response <{repr(response)}>')
            self.connection.send(response.encode('utf-8'))


def main(host="127.0.0.1", port=24596):
    print('Setting up SCPI device')
    commands = [
        {'command': 'IDN', 'value': 'Instrument Model XYZ,1234,1.0,Serial123456', 'read_only': True},
        {'command': 'OPT', 'value': 'Option1,Option2,Option3', 'read_only': True},
        {'command': 'READ', 'value': 42.0},
        {'command': 'VOLTage', 'value': 3.14},
        {'command': 'FREQuency', 'value': 1.05457},
    ]

    scpi_handler = ASCPIDevice(host, port, commands)
    print('Starting SCPI device')
    scpi_handler.start()


if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])
