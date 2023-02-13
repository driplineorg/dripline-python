from aiohttp import web
import json

from dripline.core import Interface
import dripline.core

import scarab

import logging
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

__all__ = []


__all__.append('HTTPServer')
class HTTPServer(Interface):
    '''
    An HTTP-request server that acts as a Dripline client.
    An HTTP client (e.g. user via a web browser) sends an HTTP request, which is converted to aDripline request, and forwarded to the Broker.
    When the Dripline reply is received, that's converted to an HTTP response and returned to the HTTP client.
    '''
    def __init__(self,
                 http_host=None,
                 http_port=8080,
                 web_root=None,
                 **kwargs
                 ):
        '''
        Args:
            http_host (string): IP address or URL for the HTTP server host
            http_port (int): Port for the HTTP server host
            web_root (string): Path to the root directory for static web pages

        '''
        Interface.__init__(self, **kwargs)
        logger.error('Error test')
        logger.warning('Warning test')
        logger.info('Info test')
        logger.debug('Debug test')
        print('Print test')

        self.http_host = '127.0.0.1' if http_host=='localhost' else http_host
        self.http_port = http_port

        self.web_root = web_root if web_root is not None else '/web'

        self.ret_code_conversion = {
            dripline.core.DL_Success().value: 200, # Success

            dripline.core.DL_WarningNoActionTaken().value: 100, # Continue
            dripline.core.DL_WarningDeprecatedFeature().value: 110, # Response is Stale
            dripline.core.DL_WarningDryRun().value: 112, # Disconnected Operation
            dripline.core.DL_WarningOffline().value: 112, # Disconnected Operation
            dripline.core.DL_WarningSubService().value: 199, # Miscellaneous Warning

            dripline.core.DL_AmqpError().value: 500, # Internal Server Error
            dripline.core.DL_AmqpErrorBrokerConnection().value: 500, # Internal Server Error
            dripline.core.DL_AmqpErrorRoutingkeyNotfound().value: 404, # Not found

            dripline.core.DL_ResourceError().value: 500, # Internal Server Error
            dripline.core.DL_ResourceErrorConnection().value: 503, # Service Unavailable
            dripline.core.DL_ResourceErrorNoResponse().value: 503, # Service Unavailable
            dripline.core.DL_ResourceErrorSubService().value: 503, # Service Unavailable

            dripline.core.DL_ServiceError().value: 400, # Bad request
            dripline.core.DL_ServiceErrorNoEncoding().value: 400, # Bad request
            dripline.core.DL_ServiceErrorDecodingFail().value: 400, # Bad request
            dripline.core.DL_ServiceErrorBadPayload().value: 422, # Unprocessable entity
            dripline.core.DL_ServiceErrorInvalidValue().value: 422, # Unprocessable entity
            dripline.core.DL_ServiceErrorTimeout().value: 503, # Service Unavailable
            dripline.core.DL_ServiceErrorInvalidMethod().value: 501, # Not implemented
            dripline.core.DL_ServiceErrorAccessDenied().value: 403, # Forbidden
            dripline.core.DL_ServiceErrorInvalidKey().value: 423, # Locked
            dripline.core.DL_ServiceErrorInvalidSpecifier().value: 422, # Unprocessable entity

            dripline.core.DL_ClientError().value: 500, # Internal Server Error
            dripline.core.DL_ClientErrorInvalidRequest().value: 400, # Bad Request
            dripline.core.DL_ClientErrorHandlingReply().value: 500, # Internal Server Error
            dripline.core.DL_ClientErrorUnableToSend().value: 503, # Service Unavailable
            dripline.core.DL_ClientErrorTimeout().value: 504, # Gateway Timeout
        }

    async def handle_get(self, request):
        logger.warning(f'Received HTTP GET request {request}')
        routing_key = self.path_to_routing_key(request.path)
        try:
            reply = self.get(
                endpoint=routing_key, 
                specifier=request.headers.get('specifier'),
                lockout_key=request.headers.get('lockout-key'),
            )
        except Exception as err:
            return web.Response(text=f'Unable to send GET request: {err}', status=400)
        logger.warning(f'Received DL reply:\n{reply.__str__()}')
        payload_json = json.dumps(scarab.to_python(reply.payload)) if reply.payload else None
        return web.Response(
            status=self.ret_code_conversion.get(reply.return_code, 400),
            reason=reply.return_message,
            content_type='application/json',
            headers={
                'dl_return_code': f'{reply.return_code}',
            },
            body=payload_json,
        )

    async def handle_put(self, request):
        logger.warning(f'Received HTTP SET request {request}')
        routing_key = self.path_to_routing_key(request.path)
        try:
            if request.can_read_body:
                body_json = await request.json()
                values = body_json.get('values', None) 
            reply = self.set(
                endpoint=routing_key,
                values=values,
                specifier=request.headers.get('specifier'),
                lockout_key=request.headers.get('lockout-key'),
            )
        except Exception as err:
            return web.Response(text=f'Unable to send SET request: {err}', status=400)
        logger.warning(f'Received DL reply:\n{reply.__str__()}')
        payload_json = json.dumps(scarab.to_python(reply.payload)) if reply.payload else None
        return web.Response(
            status=self.ret_code_conversion.get(reply.return_code, 199),
            reason=reply.return_message,
            content_type='application/json',
            headers={
                'dl_return_code': f'{reply.return_code}',
            },
            body=payload_json,
        )

    async def handle_post(self, request):
        routing_key = self.path_to_routing_key(request.path)
        return web.Response(text=f'Received CMD request for {routing_key}\nCMD requests are not yet implemented.\n')

    async def hello(self, request):
        return web.Response(text='Hello, world\n')

    def http_listen(self):
        '''
        Starts the HTTP server
        '''
        #logging.basicConfig(level=logging.DEBUG)

        app = web.Application()
        app.router.add_static('/web/', f'{self.web_root}')
        app.router.add_route('GET', '/hello', self.hello)
        app.router.add_route('GET', '/dl/{tail:.*}', self.handle_get)
        app.router.add_route('PUT', '/dl/{tail:.*}', self.handle_put)
        app.router.add_route('POST', '/dl/{tail:.*}', self.handle_post)

        web.run_app(app, host=self.http_host, port=self.http_port, access_log_format=" :: %r %s %T %t")

    def path_to_routing_key(self, input:str):
        # Start at index 4: URLs are expected to start with `/dl/`
        # Replace '/' with '.': Routing keys '.' instead of '/' as a separator
        # Replace '?' with '': If using a form, a GET request with have a '?' after the path, which we don't need
        return input[4:].replace('/', '.').replace('?', '')