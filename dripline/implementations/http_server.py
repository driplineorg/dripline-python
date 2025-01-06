import json
import logging
from typing import Any, Dict, Optional

from aiohttp import web
import scarab

from dripline.core import Interface, Message  # Correct import paths based on your project structure
import dripline.core

logger = logging.getLogger(__name__)
# logger.setLevel("DEBUG")

__all__ = ['HTTPServer']

class HTTPServer(Interface):
    '''
    An HTTP-request server that acts as a Dripline client.
    An HTTP client (e.g., user via a web browser) sends an HTTP request, which is converted to a Dripline request and forwarded to the Broker.
    When the Dripline reply is received, that's converted to an HTTP response and returned to the HTTP client.
    '''

    def __init__(self,
                 http_host: str = 'localhost',
                 http_port: int = 8080,
                 web_root: str = '/web',
                 **kwargs: Any) -> None:
        '''
        Initializes the HTTPServer.

        Args:
            http_host (str): IP address or URL for the HTTP server host.
            http_port (int): Port for the HTTP server host.
            web_root (str): Path to the root directory for static web pages.
            **kwargs: Additional arguments passed to the Interface.
        '''
        Interface.__init__(self, **kwargs)

        self.http_host = '127.0.0.1' if http_host == 'localhost' else http_host
        self.http_port = http_port
        self.web_root = web_root

        logger.debug(f'HTTP host: {self.http_host}, HTTP port: {self.http_port}, Web root: {self.web_root}')

        self.ret_code_conversion: Dict[int, int] = {
            dripline.core.DL_Success().value: 200,
            dripline.core.DL_WarningNoActionTaken().value: 100,
            dripline.core.DL_WarningDeprecatedFeature().value: 110,
            dripline.core.DL_WarningDryRun().value: 112,
            dripline.core.DL_WarningOffline().value: 112,
            dripline.core.DL_WarningSubService().value: 199,
            dripline.core.DL_AmqpError().value: 500,
            dripline.core.DL_AmqpErrorBrokerConnection().value: 500,
            dripline.core.DL_AmqpErrorRoutingkeyNotfound().value: 404,
            dripline.core.DL_ResourceError().value: 500,
            dripline.core.DL_ResourceErrorConnection().value: 503,
            dripline.core.DL_ResourceErrorNoResponse().value: 503,
            dripline.core.DL_ResourceErrorSubService().value: 503,
            dripline.core.DL_ServiceError().value: 400,
            dripline.core.DL_ServiceErrorNoEncoding().value: 400,
            dripline.core.DL_ServiceErrorDecodingFail().value: 400,
            dripline.core.DL_ServiceErrorBadPayload().value: 422,
            dripline.core.DL_ServiceErrorInvalidValue().value: 422,
            dripline.core.DL_ServiceErrorTimeout().value: 503,
            dripline.core.DL_ServiceErrorInvalidMethod().value: 501,
            dripline.core.DL_ServiceErrorAccessDenied().value: 403,
            dripline.core.DL_ServiceErrorInvalidKey().value: 423,
            dripline.core.DL_ServiceErrorInvalidSpecifier().value: 422,
            dripline.core.DL_ClientError().value: 500,
            dripline.core.DL_ClientErrorInvalidRequest().value: 400,
            dripline.core.DL_ClientErrorHandlingReply().value: 500,
            dripline.core.DL_ClientErrorUnableToSend().value: 503,
            dripline.core.DL_ClientErrorTimeout().value: 504,
        }

    async def handle_get(self, request: web.Request) -> web.Response:
        '''
        Handle HTTP GET requests.

        Args:
            request (web.Request): The incoming GET request.

        Returns:
            web.Response: The HTTP response to send back to the client.
        '''
        logger.debug(f'Received HTTP GET request: {request}')
        routing_key = self.path_to_routing_key(request.path)
        try:
            reply: Message = self.get(
                endpoint=routing_key,
                specifier=request.headers.get('specifier'),
                lockout_key=request.headers.get('lockout-key'),
            )
            payload_json = json.dumps(scarab.to_python(reply.payload)) if reply.payload else None
            return web.Response(
                status=self.ret_code_conversion.get(reply.return_code, 400),
                reason=reply.return_message,
                content_type='application/json',
                headers={'dl_return_code': f'{reply.return_code}'},
                body=payload_json,
            )
        except Exception as err:
            logger.error(f'Error in handle_get: {err}')
            return web.Response(text=f'Error processing GET request: {err}', status=500)

    async def handle_put(self, request: web.Request) -> web.Response:
        '''
        Clients requests that use the HTTP PUT action will be converted to the Dripline CLI command 'set'.
        A PUT request is best used when updating/replacing existing data on the server.

        Args:
            request (web.Request): The incoming PUT request.

        Returns:
            web.Response: The HTTP response to send back to the client.
        '''
        logger.debug(f'Received HTTP PUT request: {request}. Converting to DripLine SET request')

        routing_key = self.path_to_routing_key(request.path)
        try:
            body_json = await request.json()
            values = body_json.get("values", [])
            keyed_args = body_json if "values" not in body_json else None

            reply = self.set(
                endpoint=routing_key,
                value=values,
                keyed_args=keyed_args,
                specifier=request.headers.get('specifier'),
                lockout_key=request.headers.get('lockout-key'),
            )
            payload_json = json.dumps(scarab.to_python(reply.payload)) if reply.payload else None
            return web.Response(
                status=self.ret_code_conversion.get(reply.return_code, 201),
                reason=reply.return_message,
                content_type='application/json',
                headers={'dl_return_code': f'{reply.return_code}'},
                body=payload_json,
            )
        except json.JSONDecodeError as err:
            logger.error(f'JSONDecodeError in handle_put: {err}')
            return web.Response(text=f'Invalid JSON in PUT request: {err}', status=400)
        except KeyError as err:
            logger.error(f'Missing key in handle_put: {err}')
            return web.Response(text=f'Missing key in PUT request: {err}', status=400)
        except Exception as err:
            logger.error(f'Error in handle_put: {err}', exc_info=True)
            return web.Response(text=f'Error processing PUT request: {err}', status=500)

    async def handle_post(self, request: web.Request) -> web.Response:
        '''
        Handle HTTP POST requests.

        Args:
            request (web.Request): The incoming POST request.

        Returns:
            web.Response: The HTTP response to send back to the client.
        '''
        logger.debug(f'Received HTTP POST request: {request}. Converting to DripLine CMD request')

        routing_key = self.path_to_routing_key(request.path)
        try:
            body_json = await request.json()
            values = [body_json.get("values", [])]
            keyed_args = body_json if "values" not in body_json else None

            reply = self.cmd(
                endpoint=routing_key,
                specifier=request.headers.get('specifier'),
                ordered_args=values,
                keyed_args=keyed_args,
                lockout_key=request.headers.get('lockout-key'),
            )
            payload_json = json.dumps(scarab.to_python(reply.payload)) if reply.payload else None
            return web.Response(
                status=self.ret_code_conversion.get(reply.return_code, 201),
                reason=reply.return_message,
                content_type='application/json',
                headers={'dl_return_code': f'{reply.return_code}'},
                body=payload_json,
            )
        except json.JSONDecodeError as err:
            logger.error(f'JSONDecodeError in handle_post: {err}')
            return web.Response(text=f'Invalid JSON in POST request: {err}', status=400)
        except KeyError as err:
            logger.error(f'Missing key in handle_post: {err}')
            return web.Response(text=f'Missing key in POST request: {err}', status=400)
        except Exception as err:
            logger.error(f'Error in handle_put: {err}', exc_info=True)
            return web.Response(text=f'Error processing POST request: {err}', status=500)

    async def hello(self, request: web.Request) -> web.Response:
        '''
        Handle HTTP requests to the /hello endpoint.

        Args:
            request (web.Request): The incoming HTTP request.

        Returns:
            web.Response: A simple 'Hello, world' response.
        '''
        return web.Response(text='Hello, world\n')

    def http_listen(self) -> None:
        '''
        Starts the HTTP server.
        '''
        app = web.Application()
        logger.debug("Configuring routes for the HTTP server.")

        app.router.add_static('/web/', self.web_root)
        app.router.add_route('GET', '/hello', self.hello)
        app.router.add_route('GET', '/dl/{tail:.*}', self.handle_get)
        app.router.add_route('PUT', '/dl/{tail:.*}', self.handle_put)
        app.router.add_route('POST', '/dl/{tail:.*}', self.handle_post)

        web.run_app(app, host=self.http_host, port=self.http_port, access_log_format=" :: %r %s %T %t")

    def path_to_routing_key(self, input_path: str) -> str:
        '''
        Converts the URL path to a routing key.

        Args:
            input_path (str): The URL path.

        Returns:
            str: The routing key.
        '''
        # Start at index 4: URLs are expected to start with `/dl/`
        # Replace '/' with '.': Routing keys use '.' instead of '/' as a separator
        # Replace '?' with '': If using a form, a GET request with have a '?' after the path, which we don't need
        return input_path[4:].replace('/', '.').replace('?', '')