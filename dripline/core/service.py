__all__ = []

import scarab
from _dripline.core import _Service, DriplineConfig, create_dripline_auth_spec
from .throw_reply import ThrowReply

import logging

logger = logging.getLogger(__name__)

__all__.append('Service')


class Service(_Service):
    '''
    A service is the primary type of entity on a dripline mesh, and represents the 
    interface between dripline and a device or devices.
    Service is the bse class for all Python service objects.
    dl-serve is primarily responsible for starting up, configuring, and running a single service.
    '''

    def __init__(self, name, make_connection=True, enable_scheduling=False, 
                 broadcast_key='broadcast', loop_timeout_ms=1000, 
                 message_wait_ms=1000, heartbeat_interval_s=60, 
                 auth={}, authentication_obj=None,
                 dripline_mesh={}):
        '''
        Configures a service with the necessary parameters.

        Parameters
        ----------
            name : string
                The name of the endpoint, which specifies the binding key for request messages sent to this service.
            make_connection : bool, optional
                Flag for indicating whether the service should connect to the broker; if false, the service will be in "dry-run" mode.
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
                Provide optional dripline mesh configuration information
        '''

        # Final dripline_mesh config should be the default updated by the parameters passed by the caller
        dripline_config = DriplineConfig().to_python()
        dripline_config.update(dripline_mesh)

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
            dl_auth_spec.merge( scarab.to_param(auth) )
            auth_spec = scarab.ParamNode()
            auth_spec.add('dripline', dl_auth_spec)
            logger.debug(f'Loading auth spec:\n{auth_spec}')
            auth = scarab.Authentication()
            auth.add_groups(auth_spec)
            auth.process_spec()
            
        _Service.__init__(self, config=scarab.to_param(config), auth=auth, make_connection=make_connection)

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
            raise ThrowReply('service_error_bad_payload',
                             f"{self.name} unable to convert result to scarab payload: {result}")

    def do_get_request(self, a_request_message):
        logger.info("in get_request")
        a_specifier = a_request_message.specifier.to_string()
        if (a_specifier):
            logger.debug("has specifier")
            try:
                logger.debug(f"specifier is: {a_specifier}")
                an_attribute = getattr(self, a_specifier)
                logger.debug(f"attribute '{a_specifier}' value is [{an_attribute}]")
                the_node = scarab.ParamNode()
                the_node["values"] = scarab.ParamArray()
                the_node["values"].push_back(scarab.ParamValue(an_attribute))
                return a_request_message.reply(payload=the_node)
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
        result = method_ref(*the_args, **the_kwargs)
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
