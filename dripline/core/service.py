__all__ = []

import scarab
from _dripline.core import _Service, DriplineConfig, create_dripline_auth_spec
from .throw_reply import ThrowReply
from .object_creator import ObjectCreator
from .request_sender import RequestSender

import datetime
import logging

logger = logging.getLogger(__name__)

__all__.append('Service')
class Service(_Service, ObjectCreator, RequestSender):
    '''
    The primary unit of software that connects to a broker and typically provides an interface with an instrument or other software.

    The Service class is the implementation of the "service" concept in Dripline.
    It's the primary component that makes up a Dripline mesh, and it is the base class for all Python-based dripline services.

    The lifetime of a service is defined by the three main functions:
    1. `start()` -- create the AMQP channel, create the AMQP queue, bind the routing keys, and start consuming AMQP messages
    2. `listen()` -- starts the heartbeat and scheduler threads (optional), starts the receiver thread, and waits for and handles messages on the queue
    3. `stop()` -- (called asynchronously) cancels the listening service

    The ability to handle and respond to Dripline messages is embodied in the `endpoint` class.  
    Service uses `endoint` in three ways:
    1. Service is an endpoint.  A service can be setup to handle messages directed to it.
    2. Service has basic child endpoints.  These are also called "synchronous" endpoints.  
        These endpoints use the same AMQP queue as the service itself.  Messages send to the 
        service and to the synchronous endpoints are all handled serially.
    3. Service has asynchronous child endpoints.  These endpoints each have their own AMQP 
        queue and thread responsible for receiving and handling their messages.

    A service has a number of key characteristics (most of which come from its parent classes):
    * `core` -- Has all of the basic AMQP capabilities, sending messages, and making and manipulating connections
    * `endpoint` -- Handles Dripline messages
    * `listener_receiver` -- Asynchronously recieves AMQP messages and turns them into Dripline messages
    * `heartbeater` -- Sends periodic heartbeat messages
    * `scheduler` -- Can schedule events
    
    As is apparent from the above descriptions, a service is responsible for a number of threads 
    when it executes:
    * Listening -- grabs AMQP messages off the channel when they arrive
    * Message-wait -- any incomplete multi-part Dripline message will setup a thread to wait 
    *                 until the message is complete, and then submits it for handling
    * Receiver -- grabs completed Dripline messages and handles it
    * Async endpoint listening -- same as abovefor each asynchronous endpoint
    * Async endpoint message-wait -- same as above for each asynchronous endpoint
    * Async endpoint receiver -- same as above for each asynchronous endpoint
    * Heatbeater -- sends regular heartbeat messages
    * Scheduler -- executes scheduled events

    In addition to receiving messages from the broker, a user or client code can give messages directly to the service 
    using `process_message(message)`.)
    '''

    def __init__(self, name, make_connection=True, endpoints=None, add_endpoints_now=True, enable_scheduling=False, 
                 broadcast_key='broadcast', loop_timeout_ms=1000, 
                 message_wait_ms=1000, heartbeat_interval_s=60, 
                 username=None, password=None, authentication_obj=None,
                 dripline_mesh=None, **kwargs):
        '''
        Configures a service with the necessary parameters.

        Parameters
        ----------
            name : string
                The name of the endpoint, which specifies the binding key for request messages sent to this service.
            make_connection : bool, optional
                Flag for indicating whether the service should connect to the broker; if false, the service will be in "dry-run" mode.
            endpoints: list, optional
                List of endpoint configurations to add to the service
            add_endpoints_now: bool, optional
                Flag to determine whether endpoints are built in the __init__() function; if False, then endpoints must be built later with add_endpoints_from_config()
            enable_scheduling : bool, optional
            broadcast_key : string, optional
            loop_timeout_ms : int, optional
            message_wait_ms : int, optional
            heartbeat_interval_s : int, optional
            auth : dict, optional
                Manually-specified authentication information; do not use authentication_obj if using this.
                Potential (all optional) contents are:
                    'username': {
                        'value': <provide the username directly>,
                        'file': <provide a filename that contains only the username>,
                        'env': <provide an environment variable that contains the username; default is "DRIPLINE_USER">,
                        'default': <provide a default username; default (for the default) is "guest">,
                    },
                    'password': {
                        'value': <provide the password directly (this is not recommended for security reasons)>,
                        'file': <provide a filename that contains only the password>,
                        'env': <provide an environment variable that contains the password; default is "DRIPLINE_PASSWORD">,
                        'default': <provide a default password; default (for the default) is "guest">,
                    }
            authentication_obj : scarab.Authentication, optional
                Authentication information provided as a scarab.Authentication object; this will override the auth parameter.
            dripline_mesh : dict, optional
                Provide optional dripline mesh configuration information (see dripline_config for more information)
        '''
        # Final dripline_mesh config should be the default updated by the parameters passed by the caller
        dripline_config = DriplineConfig().to_python()
        dripline_config.update({} if dripline_mesh is None else dripline_mesh)

        config = {
            'name': name,
            'enable_scheduling': enable_scheduling,
            'broadcast_key': broadcast_key,
            'loop_timeout_ms': loop_timeout_ms,
            'message_wait_ms': message_wait_ms,
            'heartbeat_interval_s': heartbeat_interval_s,
            'dripline_mesh': dripline_config,
        }

        if authentication_obj is not None:
            auth = authentication_obj
        else:
            dl_auth_spec = create_dripline_auth_spec()
            auth_args = {
                'username': {} if username is None else username,
                'password': {} if password is None else password,
            }
            dl_auth_spec.merge( scarab.to_param(auth_args) )
            auth_spec = scarab.ParamNode()
            auth_spec.add('dripline', dl_auth_spec)
            logger.debug(f'Loading auth spec:\n{auth_spec}')
            auth = scarab.Authentication()
            auth.add_groups(auth_spec)
            auth.process_spec()

        _Service.__init__(self, config=scarab.to_param(config), auth=auth, make_connection=make_connection)

        RequestSender.__init__(self, sender=self)

        # Endpoints
        self.endpoint_configs = endpoints
        if( add_endpoints_now ):
            self.add_endpoints_from_config()

        if kwargs:
            logger.debug(f'Service received some kwargs that it doesn\'t handle, which will be ignored: {kwargs}')

    def add_endpoints_from_config(self):
        if self.endpoint_configs is not None:
            for an_endpoint_conf in self.endpoint_configs:
                an_endpoint = self.create_object(an_endpoint_conf, 'Endpoint')
                self.add_child( an_endpoint )
                if getattr(an_endpoint, 'log_interval', datetime.timedelta(seconds=0)) > datetime.timedelta(seconds=0):
                    logger.debug("queue up start logging for '{}'".format(an_endpoint.name))
                    an_endpoint.start_logging()


    def result_to_scarab_payload(self, result: str):
        """
        Intercept result values and throw error if scarab is unable to convert to param
        TODO: Handles global Exception case, could be more specific
        Args:
            result (str): request message passed
        """
        try:
            return scarab.to_param(result)
        except Exception as e:
            result_str = str(result)
            logger.warning(f"Bad payload: [{result_str}] is not of type bool, int, float, str, or dict. Converting to str.")
            return scarab.to_param(result_str)

    def do_get_request(self, a_request_message):
        logger.info("in get_request")
        a_specifier = a_request_message.specifier.to_string()
        if (a_specifier):
            logger.debug("has specifier")
            try:
                logger.debug(f"specifier is: {a_specifier}")
                an_attribute = getattr(self, a_specifier)
                logger.debug(f"attribute '{a_specifier}' value is [{an_attribute}]")
                return a_request_message.reply(payload=self.result_to_scarab_payload(an_attribute))
            except AttributeError as this_error:
                raise ThrowReply('service_error_invalid_specifier',
                                 f"endpoint {self.name} has no attribute {a_specifier}, unable to get")
        else:
            logger.debug('no specifier')
            the_value = self.on_get()
            return a_request_message.reply(payload=self.result_to_scarab_payload(the_value))

    def do_set_request(self, a_request_message):

        a_specifier = a_request_message.specifier.to_string()
        if not "values" in a_request_message.payload:
            raise ThrowReply('service_error_bad_payload',
                             'setting called without values, but values are required for set')
        new_value = a_request_message.payload["values"][0]()
        new_value = getattr(new_value, "as_" + new_value.type())()
        logger.debug(f'Attempting to set new_value to [{new_value}]')

        if (a_specifier):
            if not hasattr(self, a_specifier):
                raise ThrowReply('service_error_invalid_specifier',
                                 "endpoint {} has no attribute {}, unable to set".format(self.name, a_specifier))
            setattr(self, a_specifier, new_value)
            return a_request_message.reply()
        else:
            result = self.on_set(new_value)
            return a_request_message.reply(payload=self.result_to_scarab_payload(result))

    def do_cmd_request(self, a_request_message):
        # Note: any command executed in this way must return a python data structure which is
        #       able to be converted to a Param object (to be returned in the reply message)
        method_name = a_request_message.specifier.to_string()
        try:
            method_ref = getattr(self, method_name)
        except AttributeError as e:
            raise ThrowReply('service_error_invalid_method',
                             "error getting command's corresponding method: {}".format(str(e)))
        the_kwargs = a_request_message.payload.to_python()
        the_args = the_kwargs.pop('values', [])
        print(f'args: {the_args} -- kwargs: {the_kwargs}')
        try:
            result = method_ref(*the_args, **the_kwargs)
        except TypeError as e:
            raise ThrowReply('service_error_invalid_value', 
                             f'A TypeError occurred while calling the requested method for endpoint {self.name}: {method_name}. Values provided may be invalid.\nOriginal error: {str(e)}')
        return a_request_message.reply(payload=self.result_to_scarab_payload(result))

    def on_get(self):
        '''
        placeholder method for getting the value of an endpoint.
        Implementations may override to enable OP_GET operations.
        The implementation must return a value which is able to be passed to the ParamValue constructor.
        '''
        raise ThrowReply('service_error_invalid_method', "{} does not implement on_get".format(self.__class__))

    def on_set(self, _value):
        '''
        placeholder method for setting the value of an endpoint.
        Implementations may override to enable OP_SET operations.
        Any returned object must already be a scarab::Param object
        '''
        raise ThrowReply('service_error_invalid_method', "{} does not implement on_set".format(self.__class__))
