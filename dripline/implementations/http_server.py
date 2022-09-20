from aiohttp import web
import json

from dripline.core import Interface

import scarab

import logging
logger = logging.getLogger(__name__)

__all__ = []


__all__.append('HTTPServer')
class HTTPServer(Interface):
    '''
    A fairly generic subclass of Service for connecting to ethernet-capable instruments/devices.
    In is developed for and tested against devices with a SCPI-compliant command set, but may be usable with devices which do not strictly conform.
    In particular, devices must support sending a response to every command received (either natively, or via SCPI's command composition) and responses are expected to include a termination marking complete transmission.
    '''
    def __init__(self,
                 host='localhost',
                 port=8080,
                 **kwargs
                 ):
        '''
        Args:
            host (string): IP address or URL for the HTTP server host
            port (int): Port for the HTTP server host

        '''
        Interface.__init__(self, **kwargs)

        self.host = '127.0.0.1' if host=='localhost' else host
        self.port = port

    async def handle_get(self, request):
        routing_key = self.path_to_routing_key(request.path)
        try:
            reply = self.get(endpoint=routing_key, specifier=request.headers.get('specifier'))
        except Exception as err:
            return web.Response(text=f'Unable to send GET request: {err}')
        return web.Response(
            #status=...,
            reason=reply.return_message,
            body=json.dumps(scarab.to_python(reply.payload))
        )

    async def handle_put(self, request):
        routing_key = self.path_to_routing_key(request.path)
        return web.Response(text=f'Doing set request for {routing_key}\n')

    async def handle_post(self, request):
        routing_key = self.path_to_routing_key(request.path)
        return web.Response(text=f'Doing cmd request for {routing_key}\n')

    def http_listen(self):
        '''
        
        '''
        app = web.Application()
        app.router.add_route('GET', '/{tail:.*}', self.handle_get)
        app.router.add_route('PUT', '/{tail:.*}', self.handle_put)
        app.router.add_route('POST', '/{tail:.*}', self.handle_post)

        web.run_app(app, host=self.host, port=self.port)

    def path_to_routing_key(self, input:str):
        return input[1:].replace('/', '.')